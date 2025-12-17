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
from uuid import uuid4

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
        batch_id: Optional[int] = None # Initialize batch_id to None
        try:
            # 1. 解析输入
            logger.info(f"开始解析输入: {input_value}")
            parsed = self._parse_input(input_value, input_type)
            logger.info(f"解析结果: {parsed}")
            
            # 如果是 ASIN，需要获取类目 ID
            if parsed["type"] == "asin":
                logger.info(f"正在通过 ASIN {parsed['value']} 获取类目 ID")
                category_id = await self._get_category_by_asin(
                    parsed["value"], domain, test_mode, db
                )
                parsed["category_id"] = category_id
                logger.info(f"获取到类目 ID: {category_id}")
            
            # 2. 创建批次记录
            batch = self._create_batch(
                db,
                parsed=parsed,
                domain=domain,
                created_by=created_by,
                test_mode=test_mode,
            )
            batch_id = batch.id
            logger.info(f"[{batch_id}] 批次已创建")
            
            # 3. 获取 Best Sellers
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
            asins = [item.get("asin") for item in bestsellers if item.get("asin")]
            products = await self._fetch_details_batch(asins, domain, test_mode=test_mode, db=db)
            
            logger.info(f"[{batch_id}] 获取到 {len(products)} 个产品详情")
            
            # 5. 保存到数据库
            logger.info(f"[{batch_id}] 开始保存数据")
            await self._save_to_database(db, batch_id, products)
            
            # 6. 生成 Excel
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
                result["image"] = product.get("image")
                result["title"] = product.get("title")
                # 尝试获取类目名称或 ID
                cat_id = product.get("nodeId") or product.get("node_id") or product.get("categoryId")
                result["category_id"] = str(cat_id) if cat_id else None
                result["info"] = f"ASIN: {parsed['value']}"
                if product.get("category"):
                     result["info"] += f" | {product.get('category')}"
                
            elif parsed["type"] == "category_id":
                # 获取类目 Top 产品作为预览
                products = await self._fetch_bestsellers(parsed["value"], domain, test_mode, db)
                if products:
                    top = products[0]
                    result["image"] = top.get("image")
                    result["title"] = f"Top 1: {top.get('title')}"
                    result["info"] = f"Category ID: {parsed['value']} | Total: {len(products)}+"
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
        # 测试模式且没有 API Key 时使用 Mock 数据
        if test_mode and not settings.sorftime_api_key:
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
        # Mock 模式
        if test_mode and not settings.sorftime_api_key:
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
        self, asins: list[str], domain: int, test_mode: bool = False, db: Optional[Session] = None
    ) -> list[dict]:
        """批量获取产品详情"""
        # 测试模式且没有 API Key 时使用 Mock 数据
        if test_mode and not settings.sorftime_api_key:
            logger.info("测试模式：使用 Mock 产品详情数据")
            return [
                {
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
                }
                for asin in asins
            ]

        client = SorftimeClient(account_sk=settings.sorftime_api_key, db=db)
        
        results = []
        batch_size = 10
        batches = [asins[i:i+batch_size] for i in range(0, len(asins), batch_size)]
        
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
                    if isinstance(data, dict):
                        products = data.get("Products") or data.get("products") or []
                    elif isinstance(data, list):
                        products = data
                    else:
                        products = []
                    
                    results.extend([self._normalize_product_data(p) for p in products])
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
                # 1. 标准化数据
                normalized = ProductDataNormalizer.normalize_product(
                    raw_data=product,
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
            data.append({
                "ASIN": asin,
                "Title": product.get("title", ""),
                "Price": product.get("price"),
                "Rating": product.get("ratings"),
                "Reviews": product.get("ratingsCount"),
                "Category": product.get("category", ""),
                "Sales Rank": product.get("salesRank"),
                "Brand": product.get("brand", ""),
                "Image": product.get("image", ""),
                "Product URL": f"https://www.amazon.com/dp/{asin}" if asin else "",
                "Launch Date": product.get("launchDate"),
                "Revenue": product.get("revenue"),
                "Sales": product.get("sales"),
                "Fees": product.get("fbaFee"),
                "LQS": product.get("lqs"),
                "Variations": product.get("variations"),
                "Sellers": product.get("sellers"),
                "Weight": product.get("weight"),
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
        """标准化产品数据字段 (Sorftime API 返回大写字段，内部使用小写)"""
        # 处理图片：Photo 是列表，取第一个
        image = data.get("image")
        if not image and data.get("Photo"):
            photos = data.get("Photo")
            if isinstance(photos, list) and photos:
                image = photos[0]
            elif isinstance(photos, str):
                image = photos

        # 处理类目：Category 是列表，取第一个
        category = data.get("category")
        if not category and data.get("Category"):
            cats = data.get("Category")
            if isinstance(cats, list) and cats:
                category = cats[0] # 通常取第一个作为主类目
            elif isinstance(cats, str):
                category = cats

        # 尝试提取 nodeId
        node_id = data.get("nodeId") or data.get("node_id") or data.get("categoryId")
        
        # 如果没有直接的 nodeId，尝试从 BsrCategory 提取
        # BsrCategory 格式: [['Category Name', 'NodeID', 'Rank', 'Date'], ...]
        if not node_id and data.get("BsrCategory"):
            bsr_cats = data.get("BsrCategory")
            if isinstance(bsr_cats, list) and bsr_cats:
                first_bsr = bsr_cats[0]
                if isinstance(first_bsr, list) and len(first_bsr) >= 2:
                    node_id = first_bsr[1]

        return {
            **data, # 保留原始字段
            "asin": data.get("Asin") or data.get("asin"),
            "title": data.get("Title") or data.get("title"),
            "image": image,
            "price": data.get("Price") or data.get("price"), # 注意：Sorftime Price 可能是分
            "ratings": data.get("Ratings") or data.get("ratings"),
            "ratingsCount": data.get("RatingsCount") or data.get("ratingsCount"),
            "category": category,
            "salesRank": data.get("Rank") or data.get("salesRank"),
            "brand": data.get("Brand") or data.get("brand"),
            "nodeId": node_id, # 增强后的 nodeId
        }

# 单例
api_import_service = APIImportService()
