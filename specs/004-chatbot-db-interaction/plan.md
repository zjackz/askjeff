# 技术实施计划：Chatbot 数据库交互 (004)

## 1. 架构设计

采用 **Function Calling (工具调用)** 模式，流程如下：

1. **User Query** -> **LLM (DeepSeek)**
2. **LLM** -> **JSON Instruction** (e.g., `{"tool": "query_products", "params": {...}}`)
3. **Backend** -> **Execute Tool** (Call `ProductService`) -> **Data (JSON)**
4. **Backend** -> **LLM (DeepSeek)** (Query + Data Context)
5. **LLM** -> **Final Answer**

## 2. 模块变更

### 2.1 `app/services/deepseek_client.py`
- **修改 `summarize` 方法**：
  - 更新 System Prompt，描述可用工具及其参数格式。
  - 增加对 JSON 输出的解析逻辑，识别是“直接回答”还是“工具调用”。
  - 增加 `call_with_context` 方法，用于第二轮对话（生成最终回答）。

### 2.2 `app/services/chat_service.py`
- **新增 `tools` 模块**：定义可供 LLM 调用的工具函数映射。
- **修改 `ask` 方法**：
  - 实现“思考-执行-回答”的循环逻辑。
  - 处理工具调用的执行结果。

### 2.3 `app/services/product_service.py` (及其他 Service)
- 确保现有的查询方法（如 `list_products`）可以被工具函数方便地调用。

## 3. 数据结构

### 3.1 工具定义 (Prompt 中)

```json
[
  {
    "name": "query_products",
    "description": "查询产品列表",
    "parameters": {
      "keyword": "搜索关键词",
      "sort_by": "排序字段 (price, sales_rank, rating)",
      "limit": "返回数量 (默认 5)"
    }
  }
]
```

### 3.2 LLM 响应格式

```json
{
  "type": "tool_call",
  "tool": "query_products",
  "params": {
    "sort_by": "sales_rank",
    "limit": 5
  }
}
```

或者

```json
{
  "type": "message",
  "content": "你好，有什么可以帮你的吗？"
}
```

## 4. 风险评估

- **Prompt 注入**：需严格限制 Prompt，防止用户诱导 LLM 执行非预期操作。
- **性能问题**：两轮 LLM 调用会增加延迟。需优化 Prompt 长度，并考虑流式输出（暂不实现流式，先实现功能）。
- **Token 限制**：查询结果可能很大，需限制返回给 LLM 的数据量（如最多 20 条记录，只包含关键字段）。
