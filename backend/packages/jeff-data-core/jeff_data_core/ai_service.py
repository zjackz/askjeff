"""
Jeff Data Core AI Service

提供统一的 AI 服务接口，支持多个 AI 提供商
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from .ai import BaseAIProvider, AIProviderFactory
from .config import JDCConfig

logger = logging.getLogger(__name__)


class AIService:
    """统一的 AI 服务"""

    def __init__(self, config: JDCConfig):
        self.config = config
        self.providers: Dict[str, BaseAIProvider] = {}

        # 初始化配置的 AI 提供商
        self._init_providers()

    def _init_providers(self):
        """初始化 AI 提供商"""
        # DeepSeek
        if self.config.ai.deepseek_api_key:
            self.providers['deepseek'] = AIProviderFactory.create_provider(
                'deepseek',
                self.config.ai.deepseek_api_key,
                timeout=60
            )
            logger.info("DeepSeek provider initialized")

        # OpenAI
        if self.config.ai.openai_api_key:
            self.providers['openai'] = AIProviderFactory.create_provider(
                'openai',
                self.config.ai.openai_api_key,
                timeout=60
            )
            logger.info("OpenAI provider initialized")

    def get_provider(self, provider_type: Optional[str] = None) -> BaseAIProvider:
        """获取 AI 提供商实例

        Args:
            provider_type: 提供商类型（可选，默认使用配置的默认提供商）

        Returns:
            AI 提供商实例
        """
        if not provider_type:
            provider_type = self.config.ai.default_provider

        if provider_type not in self.providers:
            raise ValueError(f"AI provider not initialized: {provider_type}")

        return self.providers[provider_type]

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """AI 对话

        Args:
            messages: 对话消息列表
            provider: AI 提供商（可选）
            model: 模型名称（可选）
            **kwargs: 额外参数

        Returns:
            {
                "content": AI 响应文本,
                "provider": 提供商类型,
                "model": 使用的模型,
                "input_tokens": 输入 token 数,
                "output_tokens": 输出 token 数,
                "cost_usd": 成本（USD）
            }
        """
        ai_provider = self.get_provider(provider)

        try:
            content = await ai_provider.chat(messages, model=model, **kwargs)

            # TODO: 计算 token 数量（需要根据 AI 提供商的响应解析）
            # 这里先使用估算
            input_tokens = len(str(messages)) * 10  # 估算
            output_tokens = len(content) * 5  # 估算

            # 计算成本
            cost = ai_provider.calculate_cost(input_tokens, output_tokens, model)

            return {
                "content": content,
                "provider": provider or self.config.ai.default_provider,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost
            }

        except Exception as e:
            logger.error(f"AI chat failed: {e}")
            raise

    async def extract_features(
        self,
        data: List[Dict[str, Any]],
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """AI 特征提取

        Args:
            data: 产品数据列表
            provider: AI 提供商（可选）
            **kwargs: 额外参数

        Returns:
            提取的特征字典
        """
        ai_provider = self.get_provider(provider)

        try:
            features = await ai_provider.extract_features(data, **kwargs)

            return features

        except Exception as e:
            logger.error(f"AI feature extraction failed: {e}")
            raise

    async def analyze_ads(
        self,
        ads_data: Dict[str, Any],
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """AI 广告诊断

        Args:
            ads_data: 广告数据
            provider: AI 提供商（可选）
            **kwargs: 额外参数

        Returns:
            分析结果文本
        """
        ai_provider = self.get_provider(provider)

        try:
            result = await ai_provider.analyze(ads_data, **kwargs)

            return result

        except Exception as e:
            logger.error(f"AI ads analysis failed: {e}")
            raise

    def validate_provider(self, provider: Optional[str] = None) -> bool:
        """验证 AI 提供商配置

        Args:
            provider: AI 提供商类型

        Returns:
            是否有效
        """
        try:
            ai_provider = self.get_provider(provider)
            return ai_provider.validate_api_key()
        except Exception as e:
            logger.error(f"Provider validation failed: {e}")
            return False

    def close_all(self):
        """关闭所有 AI 提供商连接"""
        for provider in self.providers.values():
            provider.close()
        logger.info("All AI providers closed")


class AIServiceWithLogging:
    """带日志记录的 AI 服务包装器"""

    def __init__(self, ai_service: AIService, log_storage, tenant_id: str):
        self.ai_service = ai_service
        self.log_storage = log_storage
        self.tenant_id = tenant_id

    async def chat(self, *args, **kwargs) -> Dict[str, Any]:
        """带日志记录的 AI 对话"""
        start_time = datetime.utcnow()
        success = False
        error_message = None
        cost_usd = 0.0
        input_tokens = 0
        output_tokens = 0

        try:
            result = await self.ai_service.chat(*args, **kwargs)
            success = True
            input_tokens = result.get('input_tokens', 0)
            output_tokens = result.get('output_tokens', 0)
            cost_usd = result.get('cost_usd', 0.0)

            # 记录日志
            await self.log_storage.store_ai_call(
                tenant_id=self.tenant_id,
                provider=kwargs.get('provider') or self.ai_service.config.ai.default_provider,
                function_type='chat',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost_usd,
                input_text=str(args[0])[:500] if args else '',
                output_text=result['content'][:1000],
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                success=True
            )

            return result

        except Exception as e:
            error_message = str(e)
            logger.error(f"AI chat with logging failed: {e}")
            raise

    async def extract_features(self, *args, **kwargs) -> Dict[str, Any]:
        """带日志记录的特征提取"""
        start_time = datetime.utcnow()
        success = False
        error_message = None
        cost_usd = 0.0
        input_tokens = 0
        output_tokens = 0

        try:
            result = await self.ai_service.extract_features(*args, **kwargs)
            success = True

            # 估算 token
            input_tokens = len(str(kwargs.get('data', []))) * 5
            output_tokens = len(str(result)) * 3
            cost_usd = self.ai_service.get_provider().calculate_cost(
                input_tokens, output_tokens
            )

            # 记录日志
            await self.log_storage.store_ai_call(
                tenant_id=self.tenant_id,
                provider=kwargs.get('provider') or self.ai_service.config.ai.default_provider,
                function_type='extract_features',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost_usd,
                input_text=str(kwargs.get('data', ''))[:500],
                output_text=str(result)[:1000],
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                success=True
            )

            return result

        except Exception as e:
            error_message = str(e)
            logger.error(f"AI feature extraction with logging failed: {e}")
            raise

    async def analyze_ads(self, *args, **kwargs) -> str:
        """带日志记录的广告分析"""
        start_time = datetime.utcnow()
        success = False
        error_message = None
        cost_usd = 0.0
        input_tokens = 0
        output_tokens = 0

        try:
            result = await self.ai_service.analyze(*args, **kwargs)
            success = True

            # 估算 token
            input_tokens = len(str(kwargs.get('ads_data', {}))) * 10
            output_tokens = len(result) * 5
            cost_usd = self.ai_service.get_provider().calculate_cost(
                input_tokens, output_tokens
            )

            # 记录日志
            await self.log_storage.store_ai_call(
                tenant_id=self.tenant_id,
                provider=kwargs.get('provider') or self.ai_service.config.ai.default_provider,
                function_type='analyze',
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost_usd,
                input_text=str(kwargs.get('ads_data', ''))[:500],
                output_text=result[:1000],
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                success=True
            )

            return result

        except Exception as e:
            error_message = str(e)
            logger.error(f"AI ads analysis with logging failed: {e}")
            raise
