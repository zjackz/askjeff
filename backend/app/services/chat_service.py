from __future__ import annotations

from typing import Any, Callable
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ImportBatch, ProductRecord, QuerySession
from app.services.audit_service import AuditService
from app.services.deepseek_client import DeepseekClient
from app.services.log_service import LogService

ToolFunction = Callable[..., Any]


from app.services.tool_registry import ToolRegistry

class ChatService:
    def __init__(self, client: DeepseekClient | None = None) -> None:
        self.client = client or DeepseekClient()

    def ask(
        self,
        db: Session,
        *,
        question: str,
        context_batches: list[str] | None = None,
        asked_by: str | None = None,
    ) -> dict[str, Any]:
        # 确保工具已注册 (Phase 2 将实现具体工具)
        # from app.services import chat_tools  # noqa: F401

        # 1. 构造 System Prompt
        tools_schema = ToolRegistry.get_schemas()
        system_prompt = self._build_system_prompt(tools_schema)
        
        # 2. 第一轮调用：意图识别
        messages = [
            {"role": "user", "content": f"问题: {question}"},
        ]
        
        response = self.client.chat(
            messages, 
            json_mode=True, 
            temperature=0.1,
            system_prompt=system_prompt
        )
        content = response["content"]
        trace = response.get("trace", {})
        
        answer = ""
        references = []
        tool_call = None
        
        intent = self.client.parse_json_response(content)
        if not intent:
            intent = {"type": "message", "content": content}

        # 3. 处理工具调用
        if intent.get("type") == "tool_call":
            tool_name = intent.get("tool")
            params = intent.get("params", {})
            tool_func = ToolRegistry.get_tool(tool_name)
            
            if tool_func:
                try:
                    # 执行工具
                    tool_result = tool_func(db, **params)
                    tool_call = {"tool": tool_name, "params": params, "result": tool_result}
                    
                    # 4. 第二轮调用：生成回答
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user", 
                        "content": f"工具执行结果: {json.dumps(tool_result, ensure_ascii=False)}\n请根据以上结果回答用户问题。"
                    })
                    
                    final_response = self.client.chat(messages, json_mode=False, temperature=0.2)
                    answer = final_response["content"]
                    trace["final_response"] = final_response.get("trace")
                    
                    # 构造引用信息 (Phase 2 细化)
                    if isinstance(tool_result, list):
                         references = [{"data": item} for item in tool_result[:5]]
                        
                except Exception as e:
                    answer = f"执行查询时发生错误: {str(e)}"
                    trace["tool_error"] = str(e)
            else:
                answer = f"无法识别的工具: {tool_name}"
        else:
            answer = intent.get("content", str(content))

        # 5. 保存记录
        session = QuerySession(
            question=question,
            intent=tool_call["tool"] if tool_call else "direct",
            sql_template=None,
            answer=answer,
            references=references,
            deepseek_trace=trace,
            status="succeeded",
            asked_by=asked_by,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        AuditService.log_action(
            db,
            action="chat.ask",
            actor_id=asked_by,
            entity_id=session.id,
            payload={"question": question, "tool_call": tool_call},
        )
        
        return {
            "answer": session.answer,
            "references": references,
            "session_id": session.id,
        }

    def _build_system_prompt(self, tools_schema: list[dict]) -> str:
        import json
        tools_json = json.dumps(tools_schema, ensure_ascii=False, indent=2)
        return (
            "你是 Sorftime 数据分析助手。你可以使用以下工具来查询数据：\n"
            f"{tools_json}\n\n"
            "请根据用户问题，决定是否调用工具。\n"
            "如果需要查询数据，请返回 JSON 格式：\n"
            '{"type": "tool_call", "tool": "工具名称", "params": { "参数名": "参数值" }}\n\n'
            "如果不需要查询，或只是闲聊，请返回 JSON 格式：\n"
            '{"type": "message", "content": "你的回答"}\n\n'
            "注意：只返回 JSON，不要包含其他文本。"
        )

chat_service = ChatService()
