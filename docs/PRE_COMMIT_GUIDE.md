# Pre-commit Hooks 使用指南

## 安装

### 1. 安装 pre-commit

```bash
pip install pre-commit
```

### 2. 启用 pre-commit hooks

```bash
cd /home/dministrator/code/askjeff
pre-commit install
pre-commit install --hook-type commit-msg
```

### 3. 首次运行 (检查所有文件)

```bash
pre-commit run --all-files
```

---

## 配置说明

### 已启用的检查

#### 通用检查

- ✅ 删除行尾空格
- ✅ 确保文件以换行符结尾
- ✅ 检查 YAML/JSON 语法
- ✅ 防止提交大文件 (>1MB)
- ✅ 检查合并冲突标记
- ✅ 检查文件名大小写冲突

#### Python 检查

- ✅ Black 代码格式化 (行长 100)
- ✅ Flake8 代码检查
- ✅ isort import 排序

#### 前端检查

- ✅ Prettier 代码格式化
- ✅ ESLint 代码检查
- ✅ Markdown 格式检查

#### 提交信息检查

- ✅ Conventional Commits 规范
  - feat: 新功能
  - fix: 修复
  - docs: 文档
  - style: 格式
  - refactor: 重构
  - test: 测试
  - chore: 构建/工具

---

## 使用方法

### 自动运行

提交代码时自动运行:

```bash
git add .
git commit -m "feat: 添加新功能"
# pre-commit 会自动运行并修复问题
```

### 手动运行

```bash
# 检查所有文件
pre-commit run --all-files

# 检查特定文件
pre-commit run --files backend/app/main.py

# 跳过 pre-commit (不推荐)
git commit --no-verify -m "message"
```

---

## 常见问题

### 1. 检查失败怎么办?

pre-commit 会自动修复大部分问题,修复后需要重新 add 和 commit:

```bash
git add .
git commit -m "message"
```

### 2. 如何临时跳过某个检查?

```bash
SKIP=flake8 git commit -m "message"
```

### 3. 如何更新 hooks?

```bash
pre-commit autoupdate
```

---

## 配置文件

- `.pre-commit-config.yaml` - Pre-commit 配置
- `.markdownlint.yaml` - Markdown 检查配置
- `.prettierrc` - Prettier 配置 (如需自定义)
- `.flake8` - Flake8 配置 (如需自定义)

---

## 最佳实践

1. **定期更新**: 每月运行 `pre-commit autoupdate`
2. **团队协作**: 确保所有开发者都安装了 pre-commit
3. **CI 集成**: 在 CI 中也运行 pre-commit
4. **逐步启用**: 可以先禁用某些检查,逐步启用

---

## CI 集成 (可选)

在 `.github/workflows/pre-commit.yml` 中:

```yaml
name: Pre-commit

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - uses: pre-commit/action@v3.0.0
```
