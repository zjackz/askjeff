#!/usr/bin/env python3
"""
测试 AI 诊断功能

验证 DeepSeek 集成和广告分析 AI 诊断是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.ads_ai_service import AdsAIService
from app.config import settings


async def test_sku_diagnosis():
    """测试 SKU 诊断功能"""
    print("=" * 60)
    print("测试 1: SKU 诊断功能")
    print("=" * 60)
    
    # 初始化服务
    ai_service = AdsAIService()
    
    # 模拟一个积压清仓的 SKU
    test_metrics = {
        "stock_weeks": 32.5,
        "tacos": 28.3,
        "acos": 35.2,
        "ctr": 0.35,
        "cvr": 6.8,
        "margin": -5.2,
        "sales": 1250.00
    }
    
    print(f"\n📊 测试 SKU: TEST-SKU-001")
    print(f"指标数据:")
    for key, value in test_metrics.items():
        print(f"  - {key}: {value}")
    
    print("\n🤖 正在调用 AI 生成诊断...")
    
    try:
        diagnosis = await ai_service.generate_sku_diagnosis("TEST-SKU-001", test_metrics)
        print(f"\n✅ AI 诊断结果:")
        print(f"{diagnosis}")
        print("\n" + "=" * 60)
        return True
    except Exception as e:
        print(f"\n❌ 诊断失败: {str(e)}")
        print("=" * 60)
        return False


async def test_store_strategy():
    """测试全店战略建议"""
    print("\n" + "=" * 60)
    print("测试 2: 全店战略建议")
    print("=" * 60)
    
    ai_service = AdsAIService()
    
    # 模拟全店数据
    overview_data = {
        "health_score": 68.5,
        "total_sales": 125000.00,
        "tacos": 18.2,
        "quadrant_distribution": {
            "Q1": 12,  # 积压清仓
            "Q2": 25,  # 明星增长
            "Q3": 18,  # 潜力防御
            "Q4": 8    # 淘汰清理
        }
    }
    
    print(f"\n📈 全店大盘数据:")
    print(f"  - 健康度评分: {overview_data['health_score']}")
    print(f"  - 总销售额: ${overview_data['total_sales']:,.2f}")
    print(f"  - 全店 TACOS: {overview_data['tacos']}%")
    print(f"  - 产品分布: {overview_data['quadrant_distribution']}")
    
    print("\n🤖 正在调用 AI 生成战略建议...")
    
    try:
        strategy = await ai_service.generate_store_strategy(overview_data)
        print(f"\n✅ AI 战略建议:")
        print(f"{strategy}")
        print("\n" + "=" * 60)
        return True
    except Exception as e:
        print(f"\n❌ 战略生成失败: {str(e)}")
        print("=" * 60)
        return False


async def main():
    """主测试函数"""
    print("\n🚀 开始测试 AI 诊断功能")
    print(f"📡 DeepSeek API URL: {settings.deepseek_base_url}")
    print(f"🔑 API Key 已配置: {'是' if settings.deepseek_api_key else '否'}")
    
    if not settings.deepseek_api_key:
        print("\n❌ 错误: DEEPSEEK_API_KEY 未配置")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return
    
    # 运行测试
    results = []
    results.append(await test_sku_diagnosis())
    results.append(await test_store_strategy())
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过!")
    else:
        print(f"⚠️  {total - passed} 个测试失败")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
