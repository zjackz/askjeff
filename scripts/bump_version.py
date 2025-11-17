#!/usr/bin/env python3
from __future__ import annotations

"""
语义化版本号统一升级脚本。

功能：
- 从根目录 VERSION 读取当前版本（若无则回退到 backend/pyproject.toml 或 frontend/package.json）。
- 根据 --type [patch|minor|major] 或 --set X.Y.Z 计算新版本。
- 回写：VERSION、backend/pyproject.toml、frontend/package.json。
- 可选：创建 Git 提交并打标签。

用法示例：
  python3 scripts/bump_version.py --type patch --commit --tag
  python3 scripts/bump_version.py --set 0.2.0 --commit --tag
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
PYPROJECT = ROOT / "backend" / "pyproject.toml"
PKGJSON = ROOT / "frontend" / "package.json"


SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def read_version() -> str:
    if VERSION_FILE.exists():
        v = VERSION_FILE.read_text(encoding="utf-8").strip()
        if SEMVER_RE.match(v):
            return v
    # fallback: read backend pyproject
    if PYPROJECT.exists():
        text = PYPROJECT.read_text(encoding="utf-8")
        m = re.search(r"^version\s*=\s*\"(\d+\.\d+\.\d+)\"", text, flags=re.M)
        if m:
            return m.group(1)
    # fallback: frontend package.json
    if PKGJSON.exists():
        data = json.loads(PKGJSON.read_text(encoding="utf-8"))
        v = data.get("version")
        if isinstance(v, str) and SEMVER_RE.match(v):
            return v
    raise SystemExit("无法读取当前版本号")


def bump(v: str, t: str) -> str:
    m = SEMVER_RE.match(v)
    if not m:
        raise SystemExit(f"非法版本号: {v}")
    major, minor, patch = map(int, m.groups())
    if t == "patch":
        patch += 1
    elif t == "minor":
        minor += 1
        patch = 0
    elif t == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise SystemExit("type 仅支持 patch|minor|major")
    return f"{major}.{minor}.{patch}"


def write_version(newv: str) -> None:
    VERSION_FILE.write_text(newv + "\n", encoding="utf-8")

    # backend/pyproject.toml
    if PYPROJECT.exists():
        txt = PYPROJECT.read_text(encoding="utf-8")
        txt = re.sub(r'^(version\s*=\s*")\d+\.\d+\.\d+(\")', rf"\g<1>{newv}\2", txt, flags=re.M)
        PYPROJECT.write_text(txt, encoding="utf-8")

    # frontend/package.json
    if PKGJSON.exists():
        data = json.loads(PKGJSON.read_text(encoding="utf-8"))
        data["version"] = newv
        PKGJSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="统一升级版本号")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--type", choices=["patch", "minor", "major"], help="语义化升级类型")
    g.add_argument("--set", dest="set_version", help="直接指定版本号 X.Y.Z")
    ap.add_argument("--commit", action="store_true", help="创建 Git 提交")
    ap.add_argument("--tag", action="store_true", help="创建 Git 标签 vX.Y.Z")
    args = ap.parse_args()

    cur = read_version()
    newv = args.set_version if args.set_version else bump(cur, args.type)
    if args.set_version and not SEMVER_RE.match(args.set_version):
        raise SystemExit("--set 需为 X.Y.Z 形式")

    write_version(newv)
    print(f"版本已更新: {cur} -> {newv}")

    if args.commit:
        git("add", "VERSION", str(PYPROJECT), str(PKGJSON))
        msg = f"chore(release): bump version to v{newv}"
        r = git("commit", "-m", msg)
        if r.returncode != 0:
            print(r.stderr)
        else:
            print("已创建提交")

    if args.tag:
        tag = f"v{newv}"
        r = git("tag", tag, "-m", f"Release {tag}")
        if r.returncode != 0:
            print(r.stderr)
        else:
            print(f"已创建标签 {tag}")


if __name__ == "__main__":
    main()

