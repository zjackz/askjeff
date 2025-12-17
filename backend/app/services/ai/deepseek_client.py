"""
DeepSeek API 客户端

提供与 DeepSeek AI 服务的集成，用于生成智能分析和建议。
"""

import httpx
from typing import Optional, List, Dict, Any
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            raise last_exception
        return wrapper
    return decorator


class DeepSeekClient:
    """
    DeepSeek API 客户端
    
    用于调用 DeepSeek 大语言模型进行智能分析。
    支持自动重试、错误处理和日志记录。
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: DeepSeek API 密钥
            base_url: API 基础 URL
        """
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info("DeepSeek client initialized")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        timeout: float = 60.0
    ) -> str:
        """
        调用 DeepSeek Chat Completion API
        
        Args:
            messages: 对话消息列表，格式: [{"role": "user", "content": "..."}]
            model: 模型名称，默认 "deepseek-chat"
            temperature: 温度参数，控制随机性 (0-2)
            max_tokens: 最大生成 token 数
            timeout: 请求超时时间（秒）
        
        Returns:
            AI 生成的文本内容
        
        Raises:
            httpx.HTTPError: HTTP 请求失败
            ValueError: 响应格式错误
        """
        logger.info(f"Calling DeepSeek API with model={model}, messages={len(messages)}")
        
        # 验证参数
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        if not all(isinstance(m, dict) and 'role' in m and 'content' in m for m in messages):
            raise ValueError("Invalid message format")
        
        # 构建请求
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 解析响应
                data = response.json()
                
                # 提取生成的内容
                if 'choices' not in data or not data['choices']:
                    raise ValueError("Invalid API response: no choices")
                
                content = data['choices'][0]['message']['content']
                
                # 记录使用情况
                usage = data.get('usage', {})
                logger.info(
                    f"DeepSeek API call successful. "
                    f"Tokens: {usage.get('total_tokens', 'unknown')}"
                )
                
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    async def analyze_with_system_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> str:
        """
        使用系统提示词进行分析
        
        Args:
            system_prompt: 系统提示词（定义 AI 角色）
            user_prompt: 用户提示词（具体任务）
            **kwargs: 其他参数传递给 chat_completion
        
        Returns:
            AI 生成的分析结果
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.chat_completion(messages, **kwargs)
    
    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        粗略估算：中文 1 字符 ≈ 1.5 tokens，英文 1 单词 ≈ 1.3 tokens
        
        Args:
            text: 输入文本
        
        Returns:
            估算的 token 数量
        """
        # 简单估算
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len(text.split())
        
        return int(chinese_chars * 1.5 + english_words * 1.3)
