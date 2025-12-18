from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from app.prompts.extraction_prompts import (
    FEATURE_EXTRACTION_SYSTEM_PROMPT,
    TRANSLATION_SYSTEM_PROMPT,
    SUMMARIZE_SYSTEM_PROMPT
)


logger = logging.getLogger(__name__)


class DeepseekClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.endpoint = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

    def _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = httpx.post(self.endpoint, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()

    def chat(
        self,
        messages: list[dict[str, str]],
        json_mode: bool = False,
        temperature: float = 0.1,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        通用的对话接口
        :param messages: 消息列表 [{"role": "user", "content": "..."}]
        :param json_mode: 是否强制返回 JSON
        :param temperature: 温度系数
        :param system_prompt: 可选的系统提示词，如果提供，将作为第一条消息
        """
        if not self.api_key:
            return {
                "content": "API Key 未配置，无法调用 AI 服务。",
                "trace": {"error": "missing_api_key"},
            }

        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)

        payload = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": final_messages,
            "temperature": temperature,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            data = self._post_chat_completions(payload)
            content = data["choices"][0]["message"]["content"]
            
            # JSON 模式下的简单清理
            if json_mode:
                content = self._clean_json_string(content)
                
            return {"content": content, "trace": data}
        except Exception:
            logger.exception("DeepSeek 调用失败")
            return {
                "content": "AI 服务暂时不可用，请稍后重试。",
                "trace": {"error": "request_failed"},
            }

    def _clean_json_string(self, content: str) -> str:
        """清理 JSON 字符串中的 Markdown 标记"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def parse_json_response(self, content: str) -> dict | None:
        """尝试解析 JSON 响应"""
        import json
        try:
            cleaned = self._clean_json_string(content)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    def summarize(self, question: str, context: dict) -> dict[str, Any]:
        """
        保留此方法以兼容旧代码，但在内部调用新的 chat 方法
        """
        if not self.api_key:
            answer = self._build_fallback_answer(question, context)
            return {"answer": answer, "trace": {"mode": "fallback"}}

        messages = [
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"问题: {question}\n上下文: {context}",
            },
        ]
        
        result = self.chat(messages, temperature=0.2)
        return {"answer": result["content"], "trace": result.get("trace")}

    def _build_fallback_answer(self, question: str, context: dict) -> str:
        batch_info = context.get("batch_summary", {})
        return (
            "离线模式，基于本地数据的回答: "
            f"共 {batch_info.get('batch_count', 0)} 个批次，"
            f"最近批次包含 {batch_info.get('latest_rows', 0)} 行。"
            f"问题: {question}"
        )

    def extract_features(self, text: str, fields: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.api_key:
            return {}, {}

        import json
        system_prompt = FEATURE_EXTRACTION_SYSTEM_PROMPT.format(
            fields_json=json.dumps(fields, ensure_ascii=False),
            custom_instructions=""
        )

        user_prompt = f"产品信息: {text}"

        payload = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        
        try:
            data = self._post_chat_completions(payload)
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            cleaned = self._clean_json_string(content)
            return json.loads(cleaned), usage
        except Exception:
            logger.exception("DeepSeek 特征提取失败")
            return {}, {}

    async def extract_features_async(
        self, 
        text: str, 
        fields: list[str],
        custom_instructions: str | None = None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.api_key:
            return {}, {}

        import json
        
        instructions_part = ""
        if custom_instructions:
            instructions_part = f"\n\n额外指令：\n{custom_instructions}\n"

        system_prompt = FEATURE_EXTRACTION_SYSTEM_PROMPT.format(
            fields_json=json.dumps(fields, ensure_ascii=False),
            custom_instructions=instructions_part
        )

        # 2. User Prompt (Variable)
        user_prompt = f"产品信息: {text}"

        payload = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(self.endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                cleaned = self._clean_json_string(content)
                return json.loads(cleaned), usage
        except Exception:
            logger.exception("DeepSeek 异步特征提取失败")
            return {}, {}

    async def translate_product_info_async(self, text: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        自动翻译产品信息（标题和五点）为中文
        """
        if not self.api_key:
            return {}, {}

        import json
        
        system_prompt = TRANSLATION_SYSTEM_PROMPT

        user_prompt = f"产品信息: {text}"

        payload = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(self.endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                content = self._clean_json_string(content)
                
                return json.loads(content), usage
        except Exception:
            logger.exception("DeepSeek 翻译失败")
            return {}, {}
