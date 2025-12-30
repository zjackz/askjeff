#!/usr/bin/env python3
"""
项目文件清理脚本
清理临时文件、归档历史文档
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 归档目录
ARCHIVE_DIR = ROOT_DIR / "docs" / "archive"
ARCHIVE_DIR.mkdir(exist_ok=True)

# 需要归档的文件 (根目录的临时文档)
FILES_TO_ARCHIVE = [
    ".final-optimization-summary.md",
    ".frontend-optimization-report.md",
    ".frontend-optimization-summary.md",
    ".optimization-plan.md",
    ".optimization-task.md",
    ".progress-optimization-plan.md",
    ".sorftime-refactor-progress.md",
    ".sorftime-refactor-summary.md",
    ".sorftime-test-refactor-plan.md",
    "ACTION-LIST.md",
    "BUG-FIX-DUPLICATE-SUBMIT.md",
    "BUG-REPORT.md",
    "DONE.md",
    "NEXT-STEPS.md",
    "OPTIMIZATION-REPORT.md",
    "PROGRESS-IMPLEMENTATION.md",
    "README-OPTIMIZATION.md",
    "SUMMARY.md",
    "TODO-PROGRESS.md",
]

# 需要删除的临时文件
FILES_TO_DELETE = [
    "temp_migration.py",
    "temp_migration_2.py",
    "test_008.sh",
    "test_008_advanced.sh",
    "test_product_request.sh",
    "api_import_553402_20251218_052353 (1).xlsx",
    "export-6c8768d2-8a62-4448-8630-26044f60ae64 (1).xlsx",
    "quick_check_api_logs.sh",
]

def archive_file(filename: str) -> bool:
    """归档文件到 docs/archive/"""
    source = ROOT_DIR / filename
    if not source.exists():
        print(f"⏭️  跳过 (不存在): {filename}")
        return False
    
    # 添加日期前缀避免冲突
    date_prefix = datetime.now().strftime("%Y%m%d")
    dest_name = f"{date_prefix}_{filename}"
    dest = ARCHIVE_DIR / dest_name
    
    try:
        shutil.move(str(source), str(dest))
        print(f"✅ 已归档: {filename} -> docs/archive/{dest_name}")
        return True
    except Exception as e:
        print(f"❌ 归档失败: {filename} - {e}")
        return False

def delete_file(filename: str) -> bool:
    """删除临时文件"""
    filepath = ROOT_DIR / filename
    if not filepath.exists():
        print(f"⏭️  跳过 (不存在): {filename}")
        return False
    
    try:
        filepath.unlink()
        print(f"🗑️  已删除: {filename}")
        return True
    except Exception as e:
        print(f"❌ 删除失败: {filename} - {e}")
        return False

def main():
    print("=" * 60)
    print("🧹 开始清理项目文件...")
    print("=" * 60)
    
    # 归档历史文档
    print("\n📦 归档历史文档:")
    print("-" * 60)
    archived_count = sum(archive_file(f) for f in FILES_TO_ARCHIVE)
    
    # 删除临时文件
    print("\n🗑️  删除临时文件:")
    print("-" * 60)
    deleted_count = sum(delete_file(f) for f in FILES_TO_DELETE)
    
    # 总结
    print("\n" + "=" * 60)
    print("✨ 清理完成!")
    print(f"📦 归档文件: {archived_count}/{len(FILES_TO_ARCHIVE)}")
    print(f"🗑️  删除文件: {deleted_count}/{len(FILES_TO_DELETE)}")
    print(f"📁 归档位置: {ARCHIVE_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
