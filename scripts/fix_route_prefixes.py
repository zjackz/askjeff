#!/usr/bin/env python3
"""批量修改路由前缀,移除 /api 部分"""

import re
from pathlib import Path

# 需要修改的文件和对应的替换规则
files_to_update = [
    ("backend/app/api/routes/admin.py", 'router = APIRouter(prefix="/api/admin"', 'router = APIRouter(prefix="/admin"'),
    ("backend/app/api/routes/dashboard.py", 'router = APIRouter(prefix="/api/dashboard"', 'router = APIRouter(prefix="/dashboard"'),
    ("backend/app/api/routes/login.py", 'router = APIRouter(prefix="/api")', 'router = APIRouter()'),
    ("backend/app/api/routes/logs.py", 'router = APIRouter(prefix="/api/logs"', 'router = APIRouter(prefix="/logs"'),
    ("backend/app/api/routes/chat.py", 'router = APIRouter(prefix="/api/chat"', 'router = APIRouter(prefix="/chat"'),
    ("backend/app/api/routes/exports.py", 'router = APIRouter(prefix="/api/exports"', 'router = APIRouter(prefix="/exports"'),
    ("backend/app/api/routes/extraction.py", 'router = APIRouter(prefix="/api/extraction"', 'router = APIRouter(prefix="/extraction"'),
    ("backend/app/api/routes/users.py", 'router = APIRouter(prefix="/api/users"', 'router = APIRouter(prefix="/users"'),
    ("backend/app/api/routes/mcp.py", 'router = APIRouter(prefix="/api/mcp"', 'router = APIRouter(prefix="/mcp"'),
    ("backend/app/api/routes/products.py", 'router = APIRouter(prefix="/api/products"', 'router = APIRouter(prefix="/products"'),
]

base_path = Path("/home/dministrator/code/askjeff")

for file_path, old_text, new_text in files_to_update:
    full_path = base_path / file_path
    if not full_path.exists():
        print(f"⚠️  文件不存在: {file_path}")
        continue
    
    content = full_path.read_text(encoding="utf-8")
    
    if old_text in content:
        new_content = content.replace(old_text, new_text)
        full_path.write_text(new_content, encoding="utf-8")
        print(f"✅ 已更新: {file_path}")
    else:
        print(f"⏭️  跳过(未找到匹配): {file_path}")

print("\n🎉 批量更新完成!")
