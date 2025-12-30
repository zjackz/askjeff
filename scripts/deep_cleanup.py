#!/usr/bin/env python3
"""
项目深度清理脚本
清理虚拟环境、缓存文件、临时文件
"""
import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# 需要删除的虚拟环境目录
VENV_DIRS_TO_DELETE = [
    "backend/venv",
    "backend/venv_fix", 
    "backend/venv_test",
    "backend/.venv_broken",
    "tmp_venv",
    "venv",
]

# 需要删除的临时文件
TEMP_FILES_TO_DELETE = [
    "backend/debug_output.txt",
    "backend/test.xlsx",
]

# 需要删除的缓存目录模式
CACHE_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules/.cache",
]

def get_dir_size(path: Path) -> int:
    """计算目录大小 (MB)"""
    if not path.exists():
        return 0
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return total // (1024 * 1024)

def delete_directory(dir_path: str) -> tuple[bool, int]:
    """删除目录并返回释放的空间"""
    full_path = ROOT_DIR / dir_path
    if not full_path.exists():
        print(f"⏭️  跳过 (不存在): {dir_path}")
        return False, 0
    
    size_mb = get_dir_size(full_path)
    try:
        shutil.rmtree(full_path)
        print(f"🗑️  已删除: {dir_path} ({size_mb}MB)")
        return True, size_mb
    except Exception as e:
        print(f"❌ 删除失败: {dir_path} - {e}")
        return False, 0

def delete_file(file_path: str) -> bool:
    """删除文件"""
    full_path = ROOT_DIR / file_path
    if not full_path.exists():
        print(f"⏭️  跳过 (不存在): {file_path}")
        return False
    
    try:
        full_path.unlink()
        print(f"🗑️  已删除: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 删除失败: {file_path} - {e}")
        return False

def clean_cache_dirs(pattern: str) -> tuple[int, int]:
    """清理匹配模式的缓存目录"""
    count = 0
    total_size = 0
    
    for cache_dir in ROOT_DIR.rglob(pattern):
        if cache_dir.is_dir():
            # 跳过 node_modules 内部的缓存 (太多了)
            if 'node_modules' in str(cache_dir) and pattern != 'node_modules/.cache':
                continue
            
            size_mb = get_dir_size(cache_dir)
            try:
                shutil.rmtree(cache_dir)
                count += 1
                total_size += size_mb
            except Exception as e:
                print(f"❌ 清理失败: {cache_dir} - {e}")
    
    return count, total_size

def main():
    print("=" * 70)
    print("🧹 开始深度清理项目...")
    print("=" * 70)
    
    total_freed = 0
    
    # 1. 删除多余的虚拟环境
    print("\n📦 清理虚拟环境:")
    print("-" * 70)
    venv_count = 0
    for venv_dir in VENV_DIRS_TO_DELETE:
        success, size = delete_directory(venv_dir)
        if success:
            venv_count += 1
            total_freed += size
    
    # 2. 删除临时文件
    print("\n🗑️  清理临时文件:")
    print("-" * 70)
    temp_count = sum(delete_file(f) for f in TEMP_FILES_TO_DELETE)
    
    # 3. 清理 Python 缓存
    print("\n🐍 清理 Python 缓存:")
    print("-" * 70)
    pyc_count, pyc_size = clean_cache_dirs("__pycache__")
    print(f"✅ 已清理 {pyc_count} 个 __pycache__ 目录 ({pyc_size}MB)")
    total_freed += pyc_size
    
    # 4. 清理测试缓存
    print("\n🧪 清理测试缓存:")
    print("-" * 70)
    pytest_count, pytest_size = clean_cache_dirs(".pytest_cache")
    print(f"✅ 已清理 {pytest_count} 个 .pytest_cache 目录 ({pytest_size}MB)")
    total_freed += pytest_size
    
    ruff_count, ruff_size = clean_cache_dirs(".ruff_cache")
    print(f"✅ 已清理 {ruff_count} 个 .ruff_cache 目录 ({ruff_size}MB)")
    total_freed += ruff_size
    
    # 总结
    print("\n" + "=" * 70)
    print("✨ 深度清理完成!")
    print(f"🗑️  删除虚拟环境: {venv_count}/{len(VENV_DIRS_TO_DELETE)}")
    print(f"🗑️  删除临时文件: {temp_count}/{len(TEMP_FILES_TO_DELETE)}")
    print(f"🧹 清理缓存目录: {pyc_count + pytest_count + ruff_count} 个")
    print(f"💾 释放空间: ~{total_freed}MB")
    print("=" * 70)
    
    # 提示
    print("\n💡 提示:")
    print("   - 保留的虚拟环境: backend/.venv, backend/.venv-user")
    print("   - 这些是 Docker 容器使用的,请勿删除")
    print("   - 如需重建环境,请运行: make rebuild")

if __name__ == "__main__":
    main()
