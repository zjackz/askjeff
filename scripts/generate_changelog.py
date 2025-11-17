#!/usr/bin/env python3
from __future__ import annotations

"""
根据 Git 提交生成简易 CHANGELOG，支持分类（feat/fix/ci/infra/test/docs/other）。

默认比较范围：上一个标签（若无则从仓库初始）..HEAD。
可通过 --since 指定起点引用（tag/commit），--version 指定本次版本号，用于标题。
"""

import argparse
import datetime as dt
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


def sh(*args: str) -> str:
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if p.returncode != 0:
        return ""
    return p.stdout.strip()


def last_tag() -> str | None:
    out = sh("git", "describe", "--tags", "--abbrev=0")
    return out or None


def collect_commits(since: str | None) -> list[str]:
    revspec = f"{since}..HEAD" if since else "HEAD"
    out = sh("git", "log", "--pretty=%s", revspec)
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return lines


def categorize(lines: list[str]) -> dict[str, list[str]]:
    cats = {
        "🧩 新功能": [],
        "🐛 修复": [],
        "⚙️ 基础设施 / CI": [],
        "🧪 测试": [],
        "📚 文档": [],
        "其他": [],
    }
    for ln in lines:
        l = ln.lower()
        if l.startswith("feat"):
            cats["🧩 新功能"].append(ln)
        elif l.startswith("fix"):
            cats["🐛 修复"].append(ln)
        elif l.startswith("ci") or "infra" in l or l.startswith("chore"):
            cats["⚙️ 基础设施 / CI"].append(ln)
        elif l.startswith("test"):
            cats["🧪 测试"].append(ln)
        elif l.startswith("docs"):
            cats["📚 文档"].append(ln)
        else:
            cats["其他"].append(ln)
    return cats


def render(version: str, cats: dict[str, list[str]]) -> str:
    date = dt.date.today().isoformat()
    lines = [f"## v{version} - {date}", ""]
    for title, items in cats.items():
        if not items:
            continue
        lines.append(f"### {title}")
        for it in items:
            lines.append(f"- {it}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="生成简易 CHANGELOG")
    ap.add_argument("--since", help="起始标签/提交（默认自动取上一个标签）", default=None)
    ap.add_argument("--version", help="本次版本号（用于标题，如 0.1.0）", required=True)
    args = ap.parse_args()

    since = args.since or last_tag()
    lines = collect_commits(since)
    cats = categorize(lines)
    content = render(args.version, cats)

    header = "# 更新日志\n\n" if not CHANGELOG.exists() else ""
    old = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    CHANGELOG.write_text(header + content + old, encoding="utf-8")
    print(f"CHANGELOG 已更新: v{args.version}")


if __name__ == "__main__":
    main()

