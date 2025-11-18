#!/usr/bin/env bash
set -euo pipefail

# 轻量 speckit 校验：存在性+环境提示，不做重型测试。
# 可用 SKIP_SPECKIT=1 跳过；可用 SPECKIT_ENV=dev|test 指定期望环境（默认 dev）。

if [[ "${SKIP_SPECKIT:-0}" == "1" ]]; then
  echo "[speckit] skipped via SKIP_SPECKIT=1"
  exit 0
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_EXPECTED="${SPECKIT_ENV:-dev}"

fail() { echo "[speckit][FAIL] $1" >&2; exit 1; }
warn() { echo "[speckit][WARN] $1" >&2; }
info() { echo "[speckit][INFO] $1"; }

# 1) 宪章存在
[[ -f .specify/memory/constitution.md ]] || fail "缺少 .specify/memory/constitution.md"

# 2) 关键文档存在（若有 specs 目录）
if ls specs 1>/dev/null 2>&1; then
  MISSING=0
  for f in plan.md spec.md tasks.md; do
    if ! find specs -name "$f" -maxdepth 3 | grep -q .; then
      warn "未找到 $f（请确保对应 feature 下有 $f）"
      MISSING=1
    fi
  done
  [[ "$MISSING" == "0" ]] || fail "关键交付文档缺失"
fi

# 3) 环境一致性提示
if [[ "${COMPOSE_ENV:-dev}" != "$ENV_EXPECTED" ]]; then
  warn "当前 COMPOSE_ENV='${COMPOSE_ENV:-dev}'，期望 $ENV_EXPECTED（如需切换：COMPOSE_ENV=$ENV_EXPECTED make up）"
fi

# 4) 前端 E2E 报告（如存在测试结果）
if [[ -d frontend/playwright-report ]]; then
  info "检测到前端 E2E 报告目录 frontend/playwright-report"
fi

info "speckit 基础检查通过"
