from __future__ import annotations

import os
from typing import Any

import httpx


class DeepseekClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.endpoint = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

    def summarize(self, question: str, context: dict) -> dict[str, Any]:
        if not self.api_key:
            # 无 API KEY 时返回占位答案，确保离线可运行
            answer = self._build_fallback_answer(question, context)
            return {"answer": answer, "trace": {"mode": "fallback"}}

        payload = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": "你是 Sorftime 数据分析助手，请使用中文回答"},
                {
                    "role": "user",
                    "content": f"问题: {question}\n上下文: {context}",
                },
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = httpx.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return {"answer": content, "trace": data}
        except Exception as exc:  # noqa: BLE001
            print(f"DeepSeek API Error: {exc}", flush=True)
            return {
                "answer": self._build_fallback_answer(question, context),
                "trace": {"error": str(exc)},
            }

    def _build_fallback_answer(self, question: str, context: dict) -> str:
        batch_info = context.get("batch_summary", {})
        return (
            "离线模式，基于本地数据的回答: "
            f"共 {batch_info.get('batch_count', 0)} 个批次，"
            f"最近批次包含 {batch_info.get('latest_rows', 0)} 行。"
            f"问题: {question}"
        )

    def extract_features(self, text: str, fields: list[str]) -> dict[str, Any]:
        if not self.api_key:
            return {}

        prompt = (
            "你是一个电商产品专家。请根据以下产品信息，提取指定的特征字段。\n\n"
            f"产品信息: {text}\n"
            f"需要提取的字段: {', '.join(fields)}\n\n"
            "请以 JSON 格式返回结果，key 为字段名，value 为提取出的内容。如果无法提取，value 请留空。\n"
            "只返回 JSON，不要包含markdown格式或其他文本。"
        )

        payload = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": "你是 Sorftime 数据分析助手，请使用中文回答"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,  # Lower temperature for extraction
            "response_format": {"type": "json_object"}, # DeepSeek supports json_object
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = httpx.post(self.endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Simple cleanup if model returns markdown code blocks despite instructions
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            import json
            return json.loads(content)
        except Exception as exc:
            print(f"DeepSeek Extraction Error: {exc}", flush=True)
            return {}
