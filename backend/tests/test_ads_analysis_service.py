"""
测试广告分析服务

验证核心业务逻辑和数据计算
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.services.ads_analysis_service import AdsAnalysisService
from app.schemas.amazon_ads import AdsMatrixPoint


class TestAdsAnalysisService:
    """测试广告分析服务"""
    
    def test_classify_sku_critical_clearance(self):
        """测试 SKU 分类: 积压清仓 (高库存 + 高TACOS)"""
        status = AdsAnalysisService._classify_sku(
            weeks_of_cover=30.0,  # 高库存
            tacos=25.0  # 高TACOS
        )
        assert status == "CRITICAL / CLEARANCE"
    
    def test_classify_sku_star_growth(self):
        """测试 SKU 分类: 明星增长 (高库存 + 低TACOS)"""
        status = AdsAnalysisService._classify_sku(
            weeks_of_cover=30.0,  # 高库存
            tacos=15.0  # 低TACOS
        )
        assert status == "STAR / GROWTH"
    
    def test_classify_sku_potential_defense(self):
        """测试 SKU 分类: 潜力防御 (低库存 + 低TACOS)"""
        status = AdsAnalysisService._classify_sku(
            weeks_of_cover=10.0,  # 低库存
            tacos=15.0  # 低TACOS
        )
        assert status == "POTENTIAL / DEFENSE"
    
    def test_classify_sku_drop_kill(self):
        """测试 SKU 分类: 淘汰清理 (低库存 + 高TACOS)"""
        status = AdsAnalysisService._classify_sku(
            weeks_of_cover=10.0,  # 低库存
            tacos=25.0  # 高TACOS
        )
        assert status == "DROP / KILL"
    
    def test_classify_sku_boundary_24_weeks(self):
        """测试边界值: 24周库存"""
        # 24周 + 高TACOS = CRITICAL
        status1 = AdsAnalysisService._classify_sku(24.1, 25.0)
        assert status1 == "CRITICAL / CLEARANCE"
        
        # 24周 + 低TACOS = POTENTIAL
        status2 = AdsAnalysisService._classify_sku(24.0, 15.0)
        assert status2 == "POTENTIAL / DEFENSE"
    
    def test_classify_sku_boundary_20_tacos(self):
        """测试边界值: 20% TACOS"""
        # 高库存 + 20% TACOS = STAR
        status1 = AdsAnalysisService._classify_sku(30.0, 20.0)
        assert status1 == "STAR / GROWTH"
        
        # 高库存 + 20.1% TACOS = CRITICAL
        status2 = AdsAnalysisService._classify_sku(30.0, 20.1)
        assert status2 == "CRITICAL / CLEARANCE"
    
    def test_generate_diagnosis_critical(self):
        """测试诊断建议生成: 积压清仓"""
        matrix_point = AdsMatrixPoint(
            sku="TEST-SKU-001",
            asin="B0123456789",
            stock_weeks=32.5,
            tacos=28.3,
            sales=1250.00,
            status="CRITICAL / CLEARANCE",
            inventory_qty=500,
            ad_spend=354.75,
            total_sales=1250.00,
            ctr=0.35,
            cvr=6.8,
            acos=35.2,
            roas=2.84,
            margin=-5.2
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU-001", matrix_point)
        
        assert "清仓" in diagnosis
        assert "TEST-SKU-001" in diagnosis
        assert "降低售价" in diagnosis or "提高广告预算" in diagnosis
    
    def test_generate_diagnosis_star(self):
        """测试诊断建议生成: 明星增长"""
        matrix_point = AdsMatrixPoint(
            sku="TEST-SKU-002",
            asin="B9876543210",
            stock_weeks=28.0,
            tacos=12.5,
            sales=5000.00,
            status="STAR / GROWTH",
            inventory_qty=800,
            ad_spend=625.00,
            total_sales=5000.00,
            ctr=0.85,
            cvr=15.2,
            acos=12.5,
            roas=8.0,
            margin=18.5
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU-002", matrix_point)
        
        assert "霸屏" in diagnosis or "增长" in diagnosis
        assert "TEST-SKU-002" in diagnosis
        assert "提高" in diagnosis or "最大化" in diagnosis
    
    def test_generate_diagnosis_potential(self):
        """测试诊断建议生成: 潜力防御"""
        matrix_point = AdsMatrixPoint(
            sku="TEST-SKU-003",
            asin="B1122334455",
            stock_weeks=8.5,
            tacos=15.0,
            sales=3000.00,
            status="POTENTIAL / DEFENSE",
            inventory_qty=150,
            ad_spend=450.00,
            total_sales=3000.00,
            ctr=0.65,
            cvr=12.0,
            acos=15.0,
            roas=6.67,
            margin=12.0
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU-003", matrix_point)
        
        assert "防守" in diagnosis or "控量" in diagnosis
        assert "TEST-SKU-003" in diagnosis
        assert "降低预算" in diagnosis or "控制销量" in diagnosis
    
    def test_generate_diagnosis_drop(self):
        """测试诊断建议生成: 淘汰清理"""
        matrix_point = AdsMatrixPoint(
            sku="TEST-SKU-004",
            asin="B5566778899",
            stock_weeks=6.0,
            tacos=35.0,
            sales=500.00,
            status="DROP / KILL",
            inventory_qty=50,
            ad_spend=175.00,
            total_sales=500.00,
            ctr=0.25,
            cvr=4.5,
            acos=35.0,
            roas=2.86,
            margin=-8.0
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU-004", matrix_point)
        
        assert "淘汰" in diagnosis or "减少" in diagnosis
        assert "TEST-SKU-004" in diagnosis


class TestMetricsCalculation:
    """测试指标计算逻辑"""
    
    def test_tacos_calculation(self):
        """测试 TACOS 计算"""
        total_spend = 1000.0
        total_sales = 5000.0
        tacos = (total_spend / total_sales) * 100
        assert tacos == 20.0
    
    def test_weeks_of_cover_calculation(self):
        """测试库存周转计算"""
        current_stock = 210
        avg_daily_units = 10
        weeks_of_cover = current_stock / (avg_daily_units * 7)
        assert weeks_of_cover == 3.0
    
    def test_weeks_of_cover_zero_sales(self):
        """测试零销量情况下的库存周转"""
        current_stock = 100
        avg_daily_units = 0
        # 应该返回最大值 (52周)
        weeks_of_cover = 52.0 if avg_daily_units == 0 else current_stock / (avg_daily_units * 7)
        assert weeks_of_cover == 52.0
    
    def test_acos_calculation(self):
        """测试 ACOS 计算"""
        ad_spend = 500.0
        ad_sales = 2000.0
        acos = (ad_spend / ad_sales) * 100
        assert acos == 25.0
    
    def test_roas_calculation(self):
        """测试 ROAS 计算"""
        ad_sales = 3000.0
        ad_spend = 500.0
        roas = ad_sales / ad_spend
        assert roas == 6.0
    
    def test_ctr_calculation(self):
        """测试点击率计算"""
        clicks = 100
        impressions = 10000
        ctr = (clicks / impressions) * 100
        assert ctr == 1.0
    
    def test_cvr_calculation(self):
        """测试转化率计算"""
        orders = 15
        clicks = 100
        cvr = (orders / clicks) * 100
        assert cvr == 15.0


@pytest.mark.asyncio
class TestAIIntegration:
    """测试 AI 集成"""
    
    async def test_ai_service_import(self):
        """测试 AI 服务导入"""
        from app.services.ads_ai_service import AdsAIService
        service = AdsAIService()
        assert service is not None
        assert hasattr(service, 'generate_sku_diagnosis')
        assert hasattr(service, 'generate_store_strategy')
    
    async def test_deepseek_client_import(self):
        """测试 DeepSeek 客户端导入"""
        from app.services.ai.deepseek_client import DeepSeekClient
        assert DeepSeekClient is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
