"""
API 批量导入服务

从 Sorftime API 批量获取产品数据并导入系统
测试阶段：只抓取一批数据(10个产品)
"""

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.import_batch import ImportBatch, ProductRecord
from app.services.import_repository import ImportRepository
from app.services.log_service import LogService
from app.services.sorftime.client import SorftimeClient

logger = logging.getLogger(__name__)


class APIImportService:
    """API 批量导入服务"""

    def __init__(self):
        self.api_import_dir = settings.storage_dir / "api_imports"
        self.api_import_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认配置
        self.default_test_batch_size = 10

    async def import_from_input(
        self,
        db: Session,
        input_value: str,
        input_type: Optional[str] = None,
        domain: int = 1,
        created_by: Optional[str] = None,
        test_mode: bool = False,
        limit: int = 100,
        batch_id: Optional[int] = None,
    ) -> int:
        """
        从输入启动导入流程
        
        Args:
            db: 数据库会话
            input_value: 输入值 (ASIN, 类目ID, URL)
            input_type: 输入类型 (可选，自动识别)
            domain: 站点 (1=美国)
            created_by: 创建者
            test_mode: 是否开启测试模式 (只抓取少量数据)
            
        Returns:
            batch_id: 导入批次 ID (整数)
        """
        from app.services.progress_tracker import ProgressTracker
        
        batch_id: Optional[int] = None
        try:
            # 1. 解析输入
            logger.info(f"开始解析输入: {input_value}")
            parsed = self._parse_input(input_value, input_type)
            logger.info(f"解析结果: {parsed}")
            
            # 如果是 ASIN,需要获取类目 ID
            if parsed["type"] == "asin":
                logger.info(f"正在通过 ASIN {parsed['value']} 获取类目 ID")
                category_id = await self._get_category_by_asin(
                    parsed["value"], domain, test_mode, db
                )
                parsed["category_id"] = category_id
                logger.info(f"获取到类目 ID: {category_id}")
            
            # 2. 获取或创建批次记录
            logger.info(f"[DEBUG] batch_id parameter: {batch_id}")
            if batch_id:
                # 使用已有批次,更新状态和 metadata
                logger.info(f"[DEBUG] Attempting to get existing batch {batch_id}")
                batch = ImportRepository.get_batch(db, batch_id)
                if not batch:
                    logger.error(f"[DEBUG] Batch {batch_id} not found in database!")
                    raise ValueError(f"批次 {batch_id} 不存在")
                
                logger.info(f"[DEBUG] Found batch {batch_id}, updating metadata")
                # 更新 metadata (特别是 category_id)
                if batch.import_metadata:
                    batch.import_metadata["category_id"] = parsed.get("category_id")
                
                batch.status = "running"
                db.commit()
                logger.info(f"[{batch_id}] 使用已有批次,已更新 category_id")
            else:
                # 创建新批次 (这个分支不应该在后台任务中执行)
                logger.warning(f"[DEBUG] batch_id is None, creating new batch!")
                batch = self._create_batch(
                    db,
                    parsed=parsed,
                    domain=domain,
                    created_by=created_by,
                    test_mode=test_mode,
                )
                batch_id = batch.id
                logger.info(f"[{batch_id}] 创建新批次")
            
            logger.info(f"[{batch_id}] 任务开始处理")
            
            # 进度: 准备阶段
            ProgressTracker.update_progress(db, batch_id, phase="preparing", message="正在准备...")
            
            # 3. 获取 Best Sellers
            ProgressTracker.update_progress(db, batch_id, phase="fetching_list", message="正在获取产品列表...")
            
            logger.info(f"[{batch_id}] 开始获取 Best Sellers (Category: {parsed['category_id']})")
            bestsellers = await self._fetch_bestsellers(
                category_id=parsed["category_id"],
                domain=domain,
                test_mode=test_mode,
                db=db,
            )
            
            if not bestsellers:
                raise ValueError("未获取到 Best Sellers 数据")
            
            logger.info(f"[{batch_id}] 获取到 {len(bestsellers)} 个产品")
            
            # 测试模式：只取第一批
            if test_mode:
                bestsellers = bestsellers[:self.default_test_batch_size]
                logger.info(f"[{batch_id}] 测试模式：只处理前 {len(bestsellers)} 个产品")
            elif limit > 0:
                bestsellers = bestsellers[:limit]
                logger.info(f"[{batch_id}] 限制抓取数量：{len(bestsellers)} (Limit: {limit})")
            
            # 4. 批量获取详情
            logger.info(f"[{batch_id}] 开始获取产品详情")
            
            # 提前更新 total_rows
            batch.total_rows = len(bestsellers)
            db.commit()
            
            # 进度: 开始获取详情
            ProgressTracker.update_progress(
                db, batch_id,
                phase="fetching_details",
                current=0,
                total=len(bestsellers),
                message=f"开始获取产品详情 (0/{len(bestsellers)})"
            )
            
            asins = [item.get("asin") for item in bestsellers if item.get("asin")]
            products = await self._fetch_details_batch(asins, domain, test_mode=test_mode, db=db, batch_id=batch_id)
            
            logger.info(f"[{batch_id}] 获取到 {len(products)} 个产品详情")
            
            # 5. 保存到数据库
            ProgressTracker.update_progress(
                db, batch_id,
                phase="saving",
                current=len(products),
                total=len(products),
                message=f"正在保存数据 ({len(products)} 条)"
            )
            logger.info(f"[{batch_id}] 开始保存数据")
            await self._save_to_database(db, batch_id, products)
            
            # 5.5 自动翻译 (在生成 Excel 之前)
            try:
                from app.services.extraction_service import ExtractionService
                from app.services.deepseek_client import DeepseekClient
                translation_service = ExtractionService(db, DeepseekClient())
                logger.info(f"[{batch_id}] 开始自动翻译标题")
                await translation_service.auto_translate_batch(batch_id)
                # 重新从数据库加载产品以获取翻译后的数据
                from app.models.import_batch import ProductRecord
                db_products = db.query(ProductRecord).filter(ProductRecord.batch_id == batch_id).all()
                # 更新 products 列表用于生成 Excel
                products = []
                for p in db_products:
                    prod_dict = p.normalized_payload or {}
                    prod_dict["asin"] = p.asin
                    prod_dict["title"] = p.title
                    prod_dict["raw_payload"] = p.raw_payload
                    products.append(prod_dict)
            except Exception as e:
                logger.error(f"[{batch_id}] 自动翻译失败 (不影响后续流程): {e}")

            # 6. 生成 Excel
            ProgressTracker.update_progress(
                db, batch_id,
                phase="generating_excel",
                message="正在生成 Excel 文件..."
            )
            logger.info(f"[{batch_id}] 开始生成 Excel")
            excel_path = await self._generate_excel(batch_id, products, parsed)
            
            # 计算相对路径 (用于下载)
            relative_path = str(excel_path.relative_to(settings.storage_dir))
            batch.storage_path = relative_path
            db.add(batch) # 确保更新被保存
            
            # 7. 更新批次状态
            ImportRepository.update_batch_stats(
                db,
                batch,
                status="succeeded",
                total_rows=len(products),
                success_rows=len(products),
                failed_rows=0,
            )
            
            # 进度: 完成
            ProgressTracker.update_progress(
                db, batch_id,
                phase="completed",
                current=len(products),
                total=len(products),
                message=f"导入完成! 共 {len(products)} 条数据"
            )
            
            LogService.log(
                db,
                level="info",
                category="api_import",
                message=f"API 导入完成，批次 {batch_id}",
                context={
                    "input_type": parsed["type"],
                    "input_value": parsed["value"],
                    "total": len(products),
                    "excel_path": str(excel_path),
                    "download_path": relative_path,
                },
                trace_id=str(batch_id),
            )
            
            return batch_id
            
        except Exception as e:
            logger.error(f"导入失败: {e}", exc_info=True)
            
            # 更新批次状态为失败
            if 'batch' in locals():
                ImportRepository.update_batch_stats(
                    db,
                    batch,
                    status="failed",
                    total_rows=0,
                    success_rows=0,
                    failed_rows=0,
                    failure_summary={"error": str(e)},
                )
                
                # 进度: 标记失败
                ProgressTracker.mark_failed(db, batch.id, str(e))
            
            if batch_id is not None:
                LogService.log(
                    db,
                    level="error",
                    category="api_import",
                    message=f"API 导入失败，批次 {batch_id}",
                    context={"error": str(e)},
                    trace_id=str(batch_id),
                )
            
            raise

    async def preview_input(
        self, input_value: str, domain: int = 1, test_mode: bool = False, db: Optional[Session] = None
    ) -> dict:
        """
        预览输入内容
        """
        try:
            parsed = self._parse_input(input_value)
            result = {
                "type": parsed["type"],
                "value": parsed["value"],
                "category_id": parsed.get("category_id"),
                "image": None,
                "title": None,
                "info": None,
                "valid": True,
                "error": None
            }
            
            if parsed["type"] == "asin":
                # 获取 ASIN 详情
                product = await self._fetch_single_product(parsed["value"], domain, test_mode, db)
                # Note: Normalized product data uses 'image_url' key
                result["image"] = product.get("image_url") or product.get("image")
                result["title"] = product.get("title")
                # 尝试获取类目名称或 ID
                cat_id = product.get("nodeId") or product.get("node_id") or product.get("categoryId")
                result["category_id"] = str(cat_id) if cat_id else None
                
                # 增强预览信息
                result["price"] = product.get("price")
                result["currency"] = product.get("currency")
                result["rating"] = product.get("rating")
                result["reviews"] = product.get("reviews")
                result["sales_rank"] = product.get("sales_rank")
                result["brand"] = product.get("brand")
                result["bullets"] = product.get("bullets") or product.get("Bullet Points") or product.get("bullet_points")
                
                info_parts = [f"ASIN: {parsed['value']}"]
                if result["brand"]:
                    info_parts.append(f"品牌: {result['brand']}")
                if product.get("category"):
                    info_parts.append(f"类目: {product.get('category')}")
                result["info"] = " | ".join(info_parts)
                
            elif parsed["type"] == "category_id":
                # 获取类目 Top 产品作为预览
                products = await self._fetch_bestsellers(parsed["value"], domain, test_mode, db)
                if products:
                    top = products[0]
                    # Note: Normalized product data uses 'image_url' key
                    result["image"] = top.get("image_url") or top.get("image")
                    result["title"] = f"Top 1: {top.get('title')}"
                    
                    # 增强预览信息
                    result["price"] = top.get("price")
                    result["currency"] = top.get("currency")
                    result["rating"] = top.get("rating")
                    result["reviews"] = top.get("reviews")
                    result["sales_rank"] = top.get("sales_rank")
                    result["brand"] = top.get("brand")
                    result["bullets"] = top.get("bullets") or top.get("Bullet Points") or top.get("bullet_points")
                    
                    result["info"] = f"类目 ID: {parsed['value']} | 预计抓取: {len(products)} 个产品"
                else:
                    result["valid"] = False
                    result["error"] = "未找到该类目下的产品"
                    
            return result
            
        except Exception as e:
            logger.error(f"预览失败: {e}")
            return {
                "type": "unknown",
                "value": input_value,
                "valid": False,
                "error": str(e)
            }

    def _parse_input(
        self, input_value: str, input_type: Optional[str] = None
    ) -> dict:
        """
        解析输入，识别类型和提取信息
        """
        value = input_value.strip()
        
        # 1. 如果指定了类型
        if input_type:
            if input_type == "category_id":
                return {"type": "category_id", "value": value, "category_id": value}
            elif input_type == "asin":
                return {"type": "asin", "value": value}
            elif input_type == "url":
                # 尝试从 URL 提取
                pass  # 继续下面的自动识别逻辑
        
        # 2. 自动识别
        
        # 类目 ID: 纯数字
        if value.isdigit():
            return {
                "type": "category_id",
                "value": value,
                "category_id": value,
            }
            
        # ASIN: B + 9 位字母数字
        asin_match = re.search(r"(B[A-Z0-9]{9})", value)
        if asin_match:
            # 如果是纯 ASIN
            if len(value) == 10:
                return {"type": "asin", "value": value}
            
            # 如果是 URL 中的 ASIN
            if "amazon" in value or "/dp/" in value:
                return {"type": "asin", "value": asin_match.group(1)}

        # 类目 URL: node=123456
        node_match = re.search(r"[?&]node=(\d+)", value)
        if node_match:
            return {
                "type": "category_id",
                "value": node_match.group(1),
                "category_id": node_match.group(1),
            }

        # 尝试从 URL 路径中提取类目 ID (针对 Best Sellers 等页面)
        # 例如: .../bestsellers/sporting-goods/16062041/...
        if "amazon" in value:
            # 查找路径中的纯数字 ID (通常 > 3位)
            # 排除 /dp/ 后的数字 (那是 ASIN 的一部分，虽然 ASIN 通常含字母)
            # 排除 /gp/product/ 后的数字
            
            # 匹配 /数字/ 或 /数字 结尾
            path_ids = re.findall(r"/(\d+)(?:/|$|[?])", value)
            for pid in path_ids:
                # 简单的启发式规则：类目 ID 通常较长，且不是 HTTP 状态码等短数字
                if len(pid) >= 4:
                    return {
                        "type": "category_id",
                        "value": pid,
                        "category_id": pid,
                    }
            
        raise ValueError(f"无法识别的输入格式: {value}")

    def _create_batch(
        self,
        db: Session,
        parsed: dict,
        domain: int,
        created_by: Optional[str],
        test_mode: bool = False,
    ) -> ImportBatch:
        """创建批次记录"""
        filename = f"api_import_{parsed['category_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        batch = ImportRepository.create_batch(
            db,
            filename=filename,
            storage_path="",  # 稍后更新
            import_strategy="append",
            source_type="api",
            created_by=created_by,
        )
        
        # 更新元数据
        batch.import_metadata = {
            "input_type": parsed["type"],
            "input_value": parsed["value"],
            "category_id": parsed.get("category_id"),
            "domain": domain,
            "start_time": datetime.utcnow().isoformat(),
            "test_mode": test_mode,
        }
        db.commit()
        
        return batch

    async def _fetch_bestsellers(
        self, category_id: str, domain: int, test_mode: bool = False, db: Optional[Session] = None
    ) -> list[dict]:
        """获取 Best Sellers Top 100"""
        # 测试模式优先使用 Mock 数据
        if test_mode:
            logger.info("测试模式：使用 Mock Best Sellers 数据")
            return [
                {
                    "asin": f"B0{i:08d}",
                    "title": f"Mock Product {i}",
                    "category": "Electronics",
                    "salesRank": i + 1,
                }
                for i in range(100)
            ]

        # 检查 API Key
        if not settings.sorftime_api_key:
            raise ValueError("未配置 SORFTIME_API_KEY，无法进行真实 API 调用。请配置环境变量或使用 test_mode=True。")

        client = SorftimeClient(account_sk=settings.sorftime_api_key, db=db)
        
        try:
            response = await client.category_request(
                node_id=category_id,
                domain=domain,
            )
            
            logger.info(f"CategoryRequest Response: code={response.code}, data type={type(response.data)}")
            
            if response.code != 0:
                raise ValueError(f"API 调用失败: {response.message}")
            
            # 返回产品列表
            data = response.data
            logger.info(f"Response data type: {type(data)}, keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
            
            products = []
            if isinstance(data, dict):
                # Sorftime API 返回 Data.Products 或 Data.products
                products = data.get("Products") or data.get("products") or []
                logger.info(f"Extracted {len(products)} products from dict (key: Products/products)")
            elif isinstance(data, list):
                products = data
                logger.info(f"Got {len(products)} products from list")
            else:
                logger.warning(f"Unexpected data type: {type(data)}")
            
            if not products:
                logger.error(f"No products found. Data: {str(data)[:200]}")
            
            return [self._normalize_product_data(p) for p in products]
            
        except Exception as e:
            logger.error(f"获取 Best Sellers 失败: {e}", exc_info=True)
            raise

    async def _fetch_single_product(
        self, asin: str, domain: int, test_mode: bool = False, db: Optional[Session] = None
    ) -> dict:
        """获取单个产品信息"""
        # 测试模式优先使用 Mock 数据
        if test_mode:
            return {
                "asin": asin,
                "title": f"Mock Product {asin}",
                "nodeId": "172282",
                "category": "Electronics",
                "image": "https://via.placeholder.com/150"
            }

        if not settings.sorftime_api_key:
            raise ValueError("未配置 SORFTIME_API_KEY")

        client = SorftimeClient(account_sk=settings.sorftime_api_key, db=db)
        response = await client.product_request(asin=asin, domain=domain)
        
        if response.code != 0:
            raise ValueError(f"无法获取产品信息: {response.message}")
            
        data = response.data
        
        # 兼容不同的返回格式
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict) and "products" in data:
            products = data["products"]
        elif isinstance(data, dict) and ("Asin" in data or "asin" in data):
            products = [data]
        else:
            products = []
        
        if not products:
             raise ValueError(f"未找到产品信息: {asin}")
             
        return self._normalize_product_data(products[0])

    async def _get_category_by_asin(
        self, asin: str, domain: int, test_mode: bool = False, db: Optional[Session] = None
    ) -> str:
        """通过 ASIN 获取类目 ID"""
        try:
            product = await self._fetch_single_product(asin, domain, test_mode, db)
            
            node_id = product.get("nodeId") or product.get("node_id") or product.get("categoryId")
            
            if not node_id:
                logger.warning(f"产品数据中未找到类目 ID: {product}")
                raise ValueError(f"无法从产品数据中提取类目 ID: {asin}")
                
            return str(node_id)
            
        except Exception as e:
            logger.error(f"ASIN 反查类目失败: {e}", exc_info=True)
            raise

    async def _fetch_details_batch(
        self, asins: list[str], domain: int, test_mode: bool = False, db: Optional[Session] = None, batch_id: Optional[int] = None
    ) -> list[dict]:
        """批量获取产品详情"""
        # 测试模式优先使用 Mock 数据
        if test_mode:
            logger.info("测试模式：使用 Mock 产品详情数据")
            # Mock 模式下也模拟进度更新
            total = len(asins)
            results = []
            for i, asin in enumerate(asins):
                results.append({
                    "asin": asin,
                    "title": f"Mock Product {asin}",
                    "price": 99.99,
                    "ratings": 4.5,
                    "ratingsCount": 1000,
                    "category": "Electronics",
                    "salesRank": 1,
                    "brand": "Mock Brand",
                    "image": "https://example.com/image.jpg",
                    "launchDate": "2025-01-01",
                    "revenue": 100000,
                    "sales": 1000,
                    "fbaFee": 5.0,
                    "lqs": 10,
                    "variations": 2,
                    "sellers": 5,
                    "weight": 1.5,
                })
                # Mock 模式下也更新进度
                if batch_id and db and (i + 1) % 5 == 0:
                    from app.services.progress_tracker import ProgressTracker
                    ProgressTracker.update_progress(
                        db, batch_id,
                        phase="fetching_details",
                        current=i + 1,
                        total=total,
                        message=f"测试模式: 获取详情 ({i + 1}/{total})"
                    )
                await asyncio.sleep(0.1) # 模拟延迟
            return results

        client = SorftimeClient(account_sk=settings.sorftime_api_key, db=db)
        
        results = []
        batch_size = 10
        batches = [asins[i:i+batch_size] for i in range(0, len(asins), batch_size)]
        
        current_fetched_count = 0
        
        for i, batch in enumerate(batches):
            logger.info(f"处理批次 {i+1}/{len(batches)}, {len(batch)} 个产品")
            
            try:
                # 调用 API
                asin_str = ",".join(batch)
                response = await client.product_request(
                    asin=asin_str,
                    trend=0,  # 不需要趋势数据
                    domain=domain,
                )
                
                if response.code == 0:
                    data = response.data
                    # 兼容不同的返回格式
                    if isinstance(data, list):
                        products = data
                    elif isinstance(data, dict):
                        # 尝试常见的包装键
                        products = (
                            data.get("Products") or 
                            data.get("products") or 
                            data.get("list") or 
                            data.get("data")
                        )
                        # 如果没有包装键，但本身包含 ASIN，说明 dict 就是产品本身
                        if products is None and ("Asin" in data or "asin" in data):
                            products = [data]
                        elif products is None:
                            products = []
                    else:
                        products = []
                    
                    fetched_items = [self._normalize_product_data(p) for p in products]
                    results.extend(fetched_items)
                    current_fetched_count += len(fetched_items)
                    
                    # 更新进度 (使用 ProgressTracker)
                    if batch_id and db:
                        from app.services.progress_tracker import ProgressTracker
                        ProgressTracker.update_progress(
                            db, batch_id,
                            phase="fetching_details",
                            current=current_fetched_count,
                            total=len(asins),
                            message=f"正在获取产品详情 ({current_fetched_count}/{len(asins)})"
                        )
                            
                else:
                    logger.warning(f"批次 {i+1} API 调用失败: {response.message}")
                
                # 延迟（避免限流）
                if i < len(batches) - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"批次 {i+1} 处理失败: {e}", exc_info=True)
                continue
        
        return results

    async def _save_to_database(
        self, db: Session, batch_id: str, products: list[dict]
    ):
        """保存到数据库（使用统一标准化）"""
        from app.services.product_normalizer import ProductDataNormalizer
        
        records = []
        
        for product in products:
            try:
                # 1. 标准化数据 (优先使用原始数据)
                raw_data = product.get("_raw_data", product)
                normalized = ProductDataNormalizer.normalize_product(
                    raw_data=raw_data,
                    source="api"
                )
                
                # 2. 验证数据
                validation_status, validation_messages = ProductDataNormalizer.validate_product(
                    normalized
                )
                
                # 3. 创建 normalized_payload
                normalized_payload = ProductDataNormalizer.create_normalized_payload(normalized)
                
                # 4. 创建记录
                record = ProductRecord(
                    batch_id=batch_id,
                    asin=normalized["asin"],
                    title=normalized["title"],
                    category=normalized["category"],
                    price=normalized["price"],
                    currency=normalized["currency"],
                    sales_rank=normalized["sales_rank"],
                    reviews=normalized["reviews"],
                    rating=normalized["rating"],
                    raw_payload=normalized["raw_payload"],
                    normalized_payload=normalized_payload,
                    extended_data=normalized.get("extended_data"),  # 新增
                    data_source=normalized.get("data_source", "api"),  # 新增
                    validation_status=validation_status,
                    validation_messages=validation_messages,
                )
                records.append(record)
                
            except Exception as e:
                logger.error(f"处理产品数据失败 (ASIN: {product.get('asin', 'unknown')}): {e}", exc_info=True)
                continue
        
        if records:
            ImportRepository.create_product_records(db, records)
            logger.info(f"保存了 {len(records)} 条记录（API 导入）")

    async def _generate_excel(
        self, batch_id: str, products: list[dict], parsed: dict
    ) -> Path:
        """生成 Excel 文件"""
        # 准备数据
        data = []
        for product in products:
            asin = product.get("asin", "")
            # 尝试从 raw_payload 中获取翻译后的标题
            raw_payload = product.get("raw_payload") or {}
            title_cn = raw_payload.get("title_cn") or product.get("title_cn", "")
            bullets = raw_payload.get("Bullet Points") or raw_payload.get("bullet_points") or product.get("bullets", "")
            bullets_cn = raw_payload.get("bullets_cn") or product.get("bullets_cn", "")
            
            data.append({
                "ASIN": asin,
                "Title": product.get("title", ""),
                "Title (CN)": title_cn,
                "Bullet Points": bullets,
                "Bullet Points (CN)": bullets_cn,
                "Price": product.get("price"),
                "Rating": product.get("rating"),
                "Reviews": product.get("reviews"),
                "Category": product.get("category", ""),
                "Sales Rank": product.get("sales_rank"),
                "Brand": product.get("brand", ""),
                "Store": product.get("store_name", ""),
                "Image": product.get("image_url", ""),
                "Product URL": product.get("product_url") or (f"https://www.amazon.com/dp/{asin}" if asin else ""),
                "Launch Date": product.get("launch_date"),
                "Online Days": product.get("online_days"),
                "Revenue": product.get("revenue"),
                "Sales": product.get("sales_volume"),
                "Fees": product.get("fba_fee"),
                "Is FBA": "Yes" if product.get("is_fba") else "No",
                "Ships From": product.get("ships_from", ""),
                "LQS": product.get("lqs"),
                "Variations": product.get("variation_count"),
                "Sellers": product.get("seller_count"),
                "Weight": product.get("weight"),
                "Dimensions": str(product.get("dimensions", "")),
                "Has Video": "Yes" if product.get("has_video") else "No",
                "A+ Page": "Yes" if product.get("a_plus") else "No",
                "Coupon": product.get("coupon"),
            })
        
        # 创建 DataFrame
        df = pd.DataFrame(data)
        
        # 生成文件名
        filename = f"api_import_{parsed['category_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = self.api_import_dir / filename
        
        # 保存 Excel
        df.to_excel(filepath, index=False, engine="openpyxl")
        
        logger.info(f"Excel 文件已生成: {filepath}")
        
        return filepath


    def _normalize_product_data(self, data: dict) -> dict:
        """标准化产品数据字段 (使用统一的 ProductDataNormalizer)"""
        from app.services.product_normalizer import ProductDataNormalizer
        
        # 1. 执行标准化
        normalized = ProductDataNormalizer.normalize_product(data, source="api")
        
        # 2. 创建平坦化的 Payload (方便 Excel 导出和预览)
        flat_data = ProductDataNormalizer.create_normalized_payload(normalized)
        
        # 3. 保留原始数据，供 _save_to_database 使用
        flat_data["_raw_data"] = data
        
        # 4. 补充一些 API 导入特有的字段
        if "nodeId" not in flat_data:
            node_id = data.get("nodeId") or data.get("node_id") or data.get("categoryId")
            if not node_id and data.get("BsrCategory"):
                bsr_cats = data.get("BsrCategory")
                if isinstance(bsr_cats, list) and bsr_cats:
                    first_bsr = bsr_cats[0]
                    if isinstance(first_bsr, list) and len(first_bsr) >= 2:
                        node_id = first_bsr[1]
            flat_data["nodeId"] = node_id

        return flat_data

# 单例
api_import_service = APIImportService()
