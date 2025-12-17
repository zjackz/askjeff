"""
产品数据标准化器

统一处理文件导入和 API 导入的产品数据，确保：
1. 数据结构一致
2. 类型转换统一
3. 验证规则统一
4. 尽可能保存完整数据
"""
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class ProductDataNormalizer:
    """产品数据标准化器"""
    
    # 核心字段映射（数据库字段）
    CORE_FIELDS = {
        "asin": ["asin", "Asin", "ASIN"],
        "title": ["title", "Title", "product_name", "ProductName"],
        "category": ["category", "Category", "category_name"],
        "price": ["price", "Price"],
        "currency": ["currency", "Currency"],
        "sales_rank": ["sales_rank", "salesRank", "Rank", "rank", "bsr"],
        "reviews": ["reviews", "Reviews", "ratingsCount", "RatingsCount", "review_count"],
        "rating": ["rating", "Rating", "ratings", "Ratings", "star_rating"],
    }
    
    # 扩展字段映射（存入 extended_data）
    EXTENDED_FIELDS = {
        "brand": ["brand", "Brand"],
        "image_url": ["image", "Image", "photo", "Photo", "image_url", "main_image"],
        "product_url": ["product_url", "url", "link"],
        "launch_date": ["launch_date", "launchDate", "LaunchDate", "release_date"],
        "revenue": ["revenue", "Revenue"],
        "sales_volume": ["sales", "Sales", "sales_volume"],
        "fba_fee": ["fbaFee", "FbaFee", "fba_fee", "fees"],
        "lqs": ["lqs", "Lqs", "LQS"],
        "variation_count": ["variations", "Variations", "variation_count"],
        "seller_count": ["sellers", "Sellers", "seller_count"],
        "weight": ["weight", "Weight"],
        "dimensions": ["dimensions", "Dimensions"],
        "bsr_category": ["BsrCategory", "bsrCategory", "bsr_category"],
        "parent_asin": ["parentAsin", "ParentAsin", "parent_asin"],
        "is_amazon": ["isAmazon", "IsAmazon", "is_amazon"],
        "availability": ["availability", "Availability", "in_stock"],
    }
    
    @classmethod
    def normalize_product(
        cls,
        raw_data: Dict[str, Any],
        source: str = "file"  # "file" or "api"
    ) -> Dict[str, Any]:
        """
        将原始数据标准化为统一格式
        
        Args:
            raw_data: 原始数据字典
            source: 数据来源 ("file" 或 "api")
        
        Returns:
            标准化后的数据字典，包含：
            - 核心字段（直接存入数据库列）
            - extended_data（扩展字段，JSON 存储）
            - raw_payload（原始数据，完整保留）
        """
        normalized = {}
        extended = {}
        
        # 1. 提取核心字段
        for std_field, possible_names in cls.CORE_FIELDS.items():
            value = cls._extract_field(raw_data, possible_names)
            
            # 类型转换
            if std_field == "price":
                normalized[std_field] = cls._to_decimal(value)
            elif std_field in ["sales_rank", "reviews"]:
                normalized[std_field] = cls._to_int(value)
            elif std_field == "rating":
                normalized[std_field] = cls._to_decimal(value, scale=2)
            elif std_field == "currency":
                normalized[std_field] = cls._normalize_currency(value)
            else:
                normalized[std_field] = str(value) if value is not None else None
        
        # 2. 提取扩展字段
        for std_field, possible_names in cls.EXTENDED_FIELDS.items():
            value = cls._extract_field(raw_data, possible_names)
            if value is not None:
                # 特殊处理
                if std_field == "image_url":
                    extended[std_field] = cls._normalize_image_url(value)
                elif std_field == "bsr_category":
                    extended[std_field] = cls._normalize_bsr_category(value)
                else:
                    extended[std_field] = value
        
        # 3. 保留原始数据中的其他字段
        for key, value in raw_data.items():
            # 如果不在核心字段和扩展字段中，也保存到 extended_data
            if not cls._is_mapped_field(key):
                extended[f"raw_{key}"] = value
        
        return {
            **normalized,
            "extended_data": extended if extended else None,
            "raw_payload": raw_data,
            "data_source": source,
        }
    
    @classmethod
    def validate_product(cls, data: Dict[str, Any]) -> Tuple[str, Optional[Dict[str, str]]]:
        """
        验证产品数据
        
        Returns:
            (validation_status, validation_messages)
            - validation_status: "valid", "warning", "error"
            - validation_messages: {field: message}
        """
        messages = {}
        status = "valid"
        
        # 1. 必填字段检查
        required_fields = ["asin", "title"]
        for field in required_fields:
            if not data.get(field):
                messages[field] = f"{field} 是必填字段"
                status = "error"
        
        # 2. ASIN 格式验证
        asin = data.get("asin", "")
        if asin and not re.match(r"^B0[A-Z0-9]{8}$", asin):
            messages["asin"] = "ASIN 格式不正确（应为 B0 开头的 10 位字符）"
            if status != "error":
                status = "warning"
        
        # 3. 价格范围验证
        price = data.get("price")
        if price is not None:
            if price < 0:
                messages["price"] = "价格不能为负数"
                status = "error"
            elif price > 100000:
                messages["price"] = "价格异常高，请检查"
                if status != "error":
                    status = "warning"
        
        # 4. 评分范围验证
        rating = data.get("rating")
        if rating is not None:
            if rating < 0 or rating > 5:
                messages["rating"] = "评分应在 0-5 之间"
                status = "error"
        
        # 5. 评论数验证
        reviews = data.get("reviews")
        if reviews is not None and reviews < 0:
            messages["reviews"] = "评论数不能为负数"
            status = "error"
        
        return status, messages if messages else None
    
    @classmethod
    def _extract_field(cls, data: Dict[str, Any], possible_names: list) -> Any:
        """从数据中提取字段，支持多种可能的字段名"""
        for name in possible_names:
            if name in data:
                return data[name]
        return None
    
    @classmethod
    def _is_mapped_field(cls, field_name: str) -> bool:
        """检查字段是否已被映射"""
        all_mapped = set()
        for names in cls.CORE_FIELDS.values():
            all_mapped.update(names)
        for names in cls.EXTENDED_FIELDS.values():
            all_mapped.update(names)
        return field_name in all_mapped
    
    @classmethod
    def _to_decimal(cls, value: Any, scale: int = 2) -> Optional[Decimal]:
        """统一的 Decimal 转换"""
        if value is None or value == "":
            return None
        
        try:
            # 处理字符串中的货币符号和逗号
            if isinstance(value, str):
                value = value.replace("$", "").replace("¥", "").replace("€", "")
                value = value.replace(",", "").strip()
            
            decimal_value = Decimal(str(value))
            
            # 四舍五入到指定小数位
            if scale is not None:
                decimal_value = decimal_value.quantize(Decimal(10) ** -scale)
            
            return decimal_value
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"无法转换为 Decimal: {value}, 错误: {e}")
            return None
    
    @classmethod
    def _to_int(cls, value: Any) -> Optional[int]:
        """统一的 int 转换"""
        if value is None or value == "":
            return None
        
        try:
            # 处理字符串中的逗号
            if isinstance(value, str):
                value = value.replace(",", "").strip()
            
            # 处理浮点数（向下取整）
            if isinstance(value, float):
                return int(value)
            
            return int(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"无法转换为 int: {value}, 错误: {e}")
            return None
    
    @classmethod
    def _normalize_currency(cls, value: Any) -> Optional[str]:
        """标准化货币代码"""
        if not value:
            return None
        
        currency_map = {
            "$": "USD",
            "usd": "USD",
            "dollar": "USD",
            "¥": "CNY",
            "cny": "CNY",
            "rmb": "CNY",
            "€": "EUR",
            "eur": "EUR",
            "£": "GBP",
            "gbp": "GBP",
            "¥": "JPY",  # 日元也用 ¥
            "jpy": "JPY",
        }
        
        value_lower = str(value).lower().strip()
        
        # 直接匹配
        if value_lower in currency_map:
            return currency_map[value_lower]
        
        # 已经是标准格式
        if len(value_lower) == 3 and value_lower.isalpha():
            return value_lower.upper()
        
        return "USD"  # 默认美元
    
    @classmethod
    def _normalize_image_url(cls, value: Any) -> Optional[str]:
        """标准化图片 URL"""
        if not value:
            return None
        
        # 如果是列表，取第一个
        if isinstance(value, list):
            if not value:
                return None
            value = value[0]
        
        # 如果是字典，尝试提取 URL
        if isinstance(value, dict):
            value = value.get("url") or value.get("link") or value.get("src")
        
        url = str(value).strip()
        
        # 确保是有效的 URL
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        
        return None
    
    @classmethod
    def _normalize_bsr_category(cls, value: Any) -> Optional[list]:
        """
        标准化 BSR 类目数据
        
        Sorftime 返回格式: [['Category Name', 'NodeID', 'Rank', 'Date'], ...]
        """
        if not value:
            return None
        
        if not isinstance(value, list):
            return None
        
        # 已经是标准格式
        return value
    
    @classmethod
    def create_normalized_payload(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建标准化的 normalized_payload
        
        用于存储到 ProductRecord.normalized_payload 字段
        """
        return {
            # 核心字段
            "asin": data.get("asin"),
            "title": data.get("title"),
            "category": data.get("category"),
            "price": float(data["price"]) if data.get("price") else None,
            "currency": data.get("currency"),
            "sales_rank": data.get("sales_rank"),
            "reviews": data.get("reviews"),
            "rating": float(data["rating"]) if data.get("rating") else None,
            
            # 扩展字段（从 extended_data 提取）
            **data.get("extended_data", {}),
        }
