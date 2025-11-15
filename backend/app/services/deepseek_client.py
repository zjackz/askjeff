from __future__ import annotations

import os
from typing import Any, Dict

import httpx


class DeepseekClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.endpoint = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

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
