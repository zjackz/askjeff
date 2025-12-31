"""
Mock 数据生成器

用于测试和开发环境,生成模拟的 Amazon 数据
"""

from datetime import date, timedelta
from typing import List, Dict
from uuid import UUID
import random


class MockDataGenerator:
    """
    Mock 数据生成器
    
    生成模拟的库存、业务和广告数据,用于测试和开发
    
    Example:
        >>> generator = MockDataGenerator()
        >>> inventory = generator.generate_inventory_data(store_id, days=7)
        >>> business = generator.generate_business_data(store_id, days=7)
    """
    
    # 模拟 SKU 列表
    MOCK_SKUS = [
        ("TEST-SKU-001", "B00TEST001", "Wireless Mouse"),
        ("TEST-SKU-002", "B00TEST002", "Bluetooth Keyboard"),
        ("TEST-SKU-003", "B00TEST003", "USB-C Cable"),
        ("TEST-SKU-004", "B00TEST004", "Phone Stand"),
        ("TEST-SKU-005", "B00TEST005", "Laptop Sleeve"),
        ("TEST-SKU-006", "B00TEST006", "Screen Protector"),
        ("TEST-SKU-007", "B00TEST007", "Power Bank"),
        ("TEST-SKU-008", "B00TEST008", "Earbuds Case"),
        ("TEST-SKU-009", "B00TEST009", "Charging Dock"),
        ("TEST-SKU-010", "B00TEST010", "Cable Organizer"),
    ]
    
    @staticmethod
    def generate_inventory_data(
        store_id: UUID,
        days: int = 30,
        num_skus: int = None
    ) -> List[Dict]:
        """
        生成库存快照数据
        
        Args:
            store_id: 店铺 ID
            days: 生成天数
            num_skus: SKU 数量 (None 表示使用所有 Mock SKU)
        
        Returns:
            List[Dict]: 库存数据列表
        """
        results = []
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 选择 SKU
        skus = MockDataGenerator.MOCK_SKUS
        if num_skus:
            skus = skus[:num_skus]
        
        # 为每个 SKU 生成每日库存数据
        for sku, asin, name in skus:
            # 基础库存量 (会随时间波动)
            base_inventory = random.randint(50, 500)
            
            current_date = start_date
            while current_date <= end_date:
                # 添加随机波动
                daily_change = random.randint(-20, 30)
                fba_inventory = max(0, base_inventory + daily_change)
                
                results.append({
                    'store_id': store_id,
                    'date': current_date,
                    'sku': sku,
                    'asin': asin,
                    'fba_inventory': fba_inventory,
                    'inbound_inventory': random.randint(0, 100),
                    'reserved_inventory': random.randint(0, 20),
                    'unfulfillable_inventory': random.randint(0, 10),
                })
                
                # 更新基础库存
                base_inventory = fba_inventory
                current_date += timedelta(days=1)
        
        return results
    
    @staticmethod
    def generate_business_data(
        store_id: UUID,
        days: int = 30,
        num_skus: int = None
    ) -> List[Dict]:
        """
        生成业务指标数据
        
        Args:
            store_id: 店铺 ID
            days: 生成天数
            num_skus: SKU 数量
        
        Returns:
            List[Dict]: 业务数据列表
        """
        results = []
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        skus = MockDataGenerator.MOCK_SKUS
        if num_skus:
            skus = skus[:num_skus]
        
        for sku, asin, name in skus:
            # 每个 SKU 的基础销售参数
            base_price = random.uniform(15.0, 50.0)
            base_daily_units = random.randint(5, 50)
            
            current_date = start_date
            while current_date <= end_date:
                # 每日销量波动
                daily_units = max(0, base_daily_units + random.randint(-10, 15))
                daily_sales = daily_units * base_price
                
                # 流量数据
                sessions = random.randint(100, 1000)
                page_views = sessions + random.randint(50, 500)
                
                results.append({
                    'store_id': store_id,
                    'date': current_date,
                    'sku': sku,
                    'asin': asin,
                    'total_sales_amount': round(daily_sales, 2),
                    'total_units_ordered': daily_units,
                    'sessions': sessions,
                    'page_views': page_views,
                    'unit_session_percentage': round(daily_units / sessions * 100, 2) if sessions > 0 else 0,
                })
                
                current_date += timedelta(days=1)
        
        return results
    
    @staticmethod
    def generate_ads_data(
        store_id: UUID,
        days: int = 30,
        num_skus: int = None
    ) -> List[Dict]:
        """
        生成广告指标数据
        
        Args:
            store_id: 店铺 ID
            days: 生成天数
            num_skus: SKU 数量
        
        Returns:
            List[Dict]: 广告数据列表
        """
        results = []
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        skus = MockDataGenerator.MOCK_SKUS
        if num_skus:
            skus = skus[:num_skus]
        
        for sku, asin, name in skus:
            # 每个 SKU 的广告参数
            avg_cpc = random.uniform(0.3, 1.5)  # 平均点击成本
            base_daily_clicks = random.randint(10, 100)
            conversion_rate = random.uniform(0.05, 0.15)  # 5-15% 转化率
            
            current_date = start_date
            while current_date <= end_date:
                # 每日广告数据
                impressions = random.randint(1000, 10000)
                clicks = max(0, base_daily_clicks + random.randint(-20, 30))
                spend = round(clicks * avg_cpc, 2)
                orders = int(clicks * conversion_rate)
                units = orders * random.randint(1, 2)  # 每单 1-2 件
                sales = round(units * random.uniform(20.0, 60.0), 2)
                
                results.append({
                    'store_id': store_id,
                    'date': current_date,
                    'sku': sku,
                    'asin': asin,
                    'spend': spend,
                    'sales': sales,
                    'impressions': impressions,
                    'clicks': clicks,
                    'orders': orders,
                    'units': units,
                })
                
                current_date += timedelta(days=1)
        
        return results
    
    @staticmethod
    def generate_all_data(
        store_id: UUID,
        days: int = 30,
        num_skus: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        生成所有类型的数据
        
        Args:
            store_id: 店铺 ID
            days: 生成天数
            num_skus: SKU 数量
        
        Returns:
            Dict: 包含所有数据类型的字典
        """
        return {
            'inventory': MockDataGenerator.generate_inventory_data(store_id, days, num_skus),
            'business': MockDataGenerator.generate_business_data(store_id, days, num_skus),
            'advertising': MockDataGenerator.generate_ads_data(store_id, days, num_skus),
        }
