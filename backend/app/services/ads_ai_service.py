import logging
from typing import Dict, List
from app.config import settings
from app.services.ai.deepseek_client import DeepSeekClient
from app.schemas.amazon_ads import AdsMatrixPoint

logger = logging.getLogger(__name__)

class AdsAIService:
    def __init__(self):
        self.client = DeepSeekClient(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url
        )
        
    async def generate_sku_diagnosis(self, sku: str, metrics: Dict) -> str:
        """
        使用 DeepSeek 生成 SKU 深度诊断建议
        """
        system_prompt = """你是一位资深的亚马逊广告专家，擅长通过“库存 x 广告”双维度进行生意诊断。
你的任务是根据用户提供的 SKU 指标，分析其业务痛点，并提供具体的、可操作的优化建议。

诊断逻辑参考：
1. 库存周转 (Stock Weeks): >24周为积压，<4周为断货风险。
2. TACOS (总广告费/总销售额): >20%为广告侵蚀利润，<10%为广告投入不足。
3. CTR (点击率): <0.4%说明主图或标题吸引力不足。
4. CVR (转化率): <10%说明详情页或价格竞争力不足。
5. 净利润率 (Margin): 核心目标是保持正向现金流。

回复要求：
- 语气专业、果断。
- 建议必须具体（如：降低出价20%，开启清仓促销等）。
- 保持简练，不要超过 200 字。"""

        user_prompt = f"""请诊断以下 SKU 表现：
SKU: {sku}
指标数据：
- 库存周转: {metrics.get('stock_weeks')} 周
- TACOS: {metrics.get('tacos')}%
- ACOS: {metrics.get('acos')}%
- 点击率 (CTR): {metrics.get('ctr')}%
- 转化率 (CVR): {metrics.get('cvr')}%
- 净利润率: {metrics.get('margin')}%
- 月销售额: ${metrics.get('sales')}"""

        try:
            diagnosis = await self.client.analyze_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )
            return diagnosis
        except Exception as e:
            logger.error(f"AI Diagnosis failed: {str(e)}")
            return "【AI 诊断暂时不可用】请根据当前指标手动判断。建议关注库存周转与 TACOS 的平衡。"

    async def generate_store_strategy(self, overview_data: Dict) -> str:
        """
        生成全店维度的战略规划
        """
        system_prompt = "你是一位亚马逊运营总监。请根据全店大盘数据，给出下一阶段的战略方向。"
        
        user_prompt = f"""全店大盘数据：
- 健康度评分: {overview_data.get('health_score')}
- 总销售额: ${overview_data.get('total_sales')}
- 全店 TACOS: {overview_data.get('tacos')}%
- 产品分布: {overview_data.get('quadrant_distribution')}

请给出 3 条核心战略建议。"""

        try:
            strategy = await self.client.analyze_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5
            )
            return strategy
        except Exception as e:
            logger.error(f"AI Strategy failed: {str(e)}")
            return "战略建议生成失败，请检查 API 配置。"

ads_ai_service = AdsAIService()
