# Prompt 配置化指南

所有用于 AI 生成的 System Prompt **必须**配置化，禁止硬编码在业务逻辑中。

## 目录结构

```
backend/app/prompts/
├── README.md                      # 本文档
├── __init__.py                    # Python 包标识
└── [module]_prompts.py            # 具体模块的 Prompt 定义
```

## 配置文件格式

```python
"""
[Prompt 用途说明]
"""

PROMPT_NAME = """
[System Prompt 内容]
"""
```

## 使用规范

1. **独立文件**: 所有 Prompt 必须独立成文件。
2. **导入使用**: 在业务代码中通过 `from app.prompts.xxx import PROMPT_NAME` 引用。
3. **版本管理**: 修改 Prompt 必须提交 Git 记录，并在 commit message 中说明原因。
4. **禁止硬编码**: 严禁在 Service 层或 Router 层直接拼接 Prompt 字符串。
