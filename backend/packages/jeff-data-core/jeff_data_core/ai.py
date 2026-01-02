"""
Jeff Data Core AI Provider 模块

提供 AI 服务的基础类和具体实现（DeepSeek、OpenAI）
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """AI 提供商基类"""

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """AI 对话

        Args:
            messages: 对话消息列表
                [{"role": "user", "content": "..."}, ...]
            model: 模型名称（可选）
            **kwargs: 额外参数

        Returns:
            AI 响应文本
        """
        pass

    @abstractmethod
    async def extract_features(
        self, 
        data: List[Dict[str, Any]], 
        **kwargs
    ) -> Dict[str, Any]:
        """特征提取

        Args:
            data: 要提取特征的数据列表
            **kwargs: 额外参数

        Returns:
            提取的特征字典
        """
        pass

    @abstractmethod
    async def analyze(
        self, 
        data: Any, 
        **kwargs
    ) -> str:
        """数据分析

        Args:
            data: 要分析的数据
            **kwargs: 额外参数

        Returns:
            分析结果文本
        """
        pass

    @abstractmethod
    def calculate_cost(
        self, 
        input_tokens: int, 
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """计算调用成本

        Args:
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            model: 模型名称

        Returns:
            成本（USD）
        """
        pass

    def validate_api_key(self) -> bool:
        """验证 API Key 是否有效"""
        return bool(self.api_key)

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek AI 提供商"""

    BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self, api_key: str, timeout: int = 60):
        super().__init__(api_key, timeout)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """DeepSeek 对话"""
        model = model or self.DEFAULT_MODEL

        url = f"{self.BASE_URL}/chat/completions"

        try:
            response = await self.client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            # 提取响应文本
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return content

        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise

    async def extract_features(
        self,
        data: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """DeepSeek 特征提取"""
        # 构建提示词
        prompt = self._build_extraction_prompt(data, **kwargs)

        messages = [{"role": "user", "content": prompt}]

        content = await self.chat(messages, **kwargs)

        # 尝试解析 JSON 响应
        features = self._parse_json_response(content)

        return features

    async def analyze(
        self,
        data: Any,
        **kwargs
    ) -> str:
        """DeepSeek 数据分析"""
        prompt = self._build_analysis_prompt(data, **kwargs)

        messages = [{"role": "user", "content": prompt}]

        return await self.chat(messages, **kwargs)

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """计算 DeepSeek 调用成本

        DeepSeek 定价（示例，需要根据实际情况调整）：
        - deepseek-chat: $0.001 / 1K tokens
        - deepseek-coder: $0.002 / 1K tokens
        """
        model = model or self.DEFAULT_MODEL

        # 定价映射
        pricing = {
            "deepseek-chat": 0.001,
            "deepseek-coder": 0.002
        }

        price_per_1k = pricing.get(model, 0.001)
        total_tokens = (input_tokens + output_tokens) / 1000

        cost = total_tokens * price_per_1k

        return round(cost, 6)

    def _build_extraction_prompt(
        self,
        data: List[Dict[str, Any]],
        **kwargs
    ) -> str:
        """构建特征提取提示词"""
        prompt = kwargs.get("prompt_template") or """
        请从以下产品数据中提取关键特征：
        - 产品标题
        - 品牌
        - 价格区间
        - 目标受众
        - 核心卖点

        产品数据：
        {products}

        请以 JSON 格式返回提取的特征。
        """

        # 格式化产品数据
        products_text = "\n".join([
            f"产品 {i+1}: {item.get('title', 'N/A')} - {item.get('price', 'N/A')}"
            for i, item in enumerate(data[:10])  # 限制数量
        ])

        return prompt.format(products=products_text)

    def _build_analysis_prompt(
        self,
        data: Any,
        **kwargs
    ) -> str:
        """构建数据分析提示词"""
        prompt = kwargs.get("prompt_template") or """
        请分析以下数据，提供优化建议：

        数据：
        {data}

        请从以下维度分析：
        1. 数据质量
        2. 异常点
        3. 优化建议
        """

        return prompt.format(data=str(data))

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        try:
            import json
            # 尝试提取 JSON 块
            import re
            json_match = re.search(r'\{.*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(content)
        except Exception as e:
            logger.warning(f"解析 JSON 响应失败: {e}")
            return {}


class OpenAIProvider(BaseAIProvider):
    """OpenAI 提供商（预留）"""

    BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-3.5-turbo"

    def __init__(self, api_key: str, timeout: int = 60):
        super().__init__(api_key, timeout)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """OpenAI 对话"""
        model = model or self.DEFAULT_MODEL

        url = f"{self.BASE_URL}/chat/completions"

        try:
            response = await self.client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return content

        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            raise

    async def extract_features(
        self,
        data: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """OpenAI 特征提取"""
        prompt = self._build_extraction_prompt(data, **kwargs)
        messages = [{"role": "user", "content": prompt}]

        content = await self.chat(messages, **kwargs)
        return self._parse_json_response(content)

    async def analyze(
        self,
        data: Any,
        **kwargs
    ) -> str:
        """OpenAI 数据分析"""
        prompt = self._build_analysis_prompt(data, **kwargs)
        messages = [{"role": "user", "content": prompt}]

        return await self.chat(messages, **kwargs)

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """计算 OpenAI 调用成本

        OpenAI 定价（需要根据实际情况调整）：
        - gpt-3.5-turbo: $0.0005 / 1K tokens
        - gpt-4: $0.03 / 1K tokens
        """
        model = model or self.DEFAULT_MODEL

        pricing = {
            "gpt-3.5-turbo": 0.0005,
            "gpt-4": 0.03
        }

        price_per_1k = pricing.get(model, 0.0005)
        total_tokens = (input_tokens + output_tokens) / 1000

        cost = total_tokens * price_per_1k

        return round(cost, 6)

    def _build_extraction_prompt(self, data: List[Dict[str, Any]], **kwargs) -> str:
        """构建特征提取提示词"""
        prompt = kwargs.get("prompt_template") or """
        请从以下产品数据中提取关键特征。

        产品数据：
        {products}

        请以 JSON 格式返回提取的特征。
        """

        products_text = "\n".join([
            f"产品 {i+1}: {item.get('title', 'N/A')} - {item.get('price', 'N/A')}"
            for i, item in enumerate(data[:10])
        ])

        return prompt.format(products=products_text)

    def _build_analysis_prompt(self, data: Any, **kwargs) -> str:
        """构建数据分析提示词"""
        prompt = kwargs.get("prompt_template") or """
        请分析以下数据。

        数据：
        {data}

        请提供优化建议。
        """

        return prompt.format(data=str(data))

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        try:
            import json
            import re
            json_match = re.search(r'\{.*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(content)
        except Exception as e:
            logger.warning(f"解析 JSON 响应失败: {e}")
            return {}


class AIProviderFactory:
    """AI 提供商工厂"""

    @staticmethod
    def create_provider(
        provider_type: str,
        api_key: str,
        **kwargs
    ) -> BaseAIProvider:
        """创建 AI 提供商实例

        Args:
            provider_type: 提供商类型
                - "deepseek": DeepSeekProvider
                - "openai": OpenAIProvider
            api_key: API Key
            **kwargs: 额外参数（timeout等）

        Returns:
            AI 提供商实例
        """
        if provider_type == "deepseek":
            return DeepSeekProvider(api_key, **kwargs)
        elif provider_type == "openai":
            return OpenAIProvider(api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_type}")
