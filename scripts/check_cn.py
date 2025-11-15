#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGETS = ["specs", "README.md"]
CHECK_SUFFIXES = {".md", ".txt"}
PATTERNS = [r"\[NEEDS CLARIFICATION", r"TODO\("]

violations: list[str] = []
compiled = [re.compile(pattern) for pattern in PATTERNS]

for target in TARGETS:
  path = ROOT / target
  if not path.exists():
    continue
  files = []
  if path.is_file():
    files = [path]
  else:
    files = [p for p in path.rglob("*") if p.is_file() and p.suffix in CHECK_SUFFIXES]
  for file in files:
    text = file.read_text(errors="ignore")
    if any(pattern.search(text) for pattern in compiled):
      violations.append(str(file.relative_to(ROOT)))

if violations:
  print("检测到未完成的占位符:")
  for item in violations:
    print(" -", item)
  sys.exit(1)
print("中文检查通过")
