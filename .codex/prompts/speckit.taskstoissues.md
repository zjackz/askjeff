---
description: 基于可用设计文档，将现有任务转换为可执行、按依赖排序的 GitHub issues。
tools: ['github/github-mcp-server/issue_write']
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Outline

1. 在仓库根目录运行 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`，解析 FEATURE_DIR 与 AVAILABLE_DOCS 列表。所有路径必须是绝对路径。对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）。
1. 从脚本输出中获取 **tasks** 的路径。
1. 通过运行以下命令获取 Git 远端：

```bash
git config --get remote.origin.url
```

**仅当远端为 GitHub URL 时继续下一步**

1. 针对任务列表的每个任务，使用 GitHub MCP 服务器在与远端匹配的仓库内创建新 issue。

**绝对不得在与远端不匹配的仓库创建 issue**
