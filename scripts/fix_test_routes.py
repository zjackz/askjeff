#!/usr/bin/env python3
"""
批量修复测试文件中的路由前缀
将 /api/xxx 更新为 /api/v1/xxx (除了 /api/login 和 /api/health)
"""
import re
from pathlib import Path

# 测试文件目录
TESTS_DIR = Path(__file__).parent.parent / "backend" / "tests"

# 需要添加 /v1 的路由模式
ROUTES_TO_FIX = [
    "imports",
    "exports", 
    "products",
    "chat",
    "extraction",
    "users",
    "admin",
    "logs",
    "dashboard",
    "mcp",
    "sorftime",
    "ai",
    "backups",
]

# 不需要修改的路由 (已经是正确的)
EXCLUDE_ROUTES = ["login", "health"]

def fix_route_in_line(line: str) -> str:
    """修复单行代码中的路由前缀"""
    # 匹配 "/api/xxx" 模式
    pattern = r'"/api/([a-z_]+)'
    
    def replace_route(match):
        route = match.group(1)
        # 如果路由在排除列表中,不修改
        if route in EXCLUDE_ROUTES:
            return match.group(0)
        # 如果已经是 /api/v1/,不修改
        if route == "v1":
            return match.group(0)
        # 如果路由需要修复,添加 /v1
        if any(route.startswith(r) for r in ROUTES_TO_FIX):
            return f'"/api/v1/{route}'
        return match.group(0)
    
    return re.sub(pattern, replace_route, line)

def fix_file(filepath: Path) -> tuple[bool, int]:
    """
    修复单个文件
    
    Returns:
        (是否修改, 修改行数)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        changed_count = 0
        
        for line in lines:
            new_line = fix_route_in_line(line)
            if new_line != line:
                changed_count += 1
            new_lines.append(new_line)
        
        if changed_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True, changed_count
        
        return False, 0
    
    except Exception as e:
        print(f"❌ 处理失败: {filepath} - {e}")
        return False, 0

def main():
    print("=" * 70)
    print("🔧 批量修复测试路由前缀")
    print("=" * 70)
    
    # 查找所有 Python 测试文件
    test_files = list(TESTS_DIR.rglob("test_*.py"))
    
    print(f"\n📁 找到 {len(test_files)} 个测试文件")
    print("-" * 70)
    
    total_files_changed = 0
    total_lines_changed = 0
    
    for filepath in sorted(test_files):
        changed, count = fix_file(filepath)
        if changed:
            rel_path = filepath.relative_to(TESTS_DIR.parent)
            print(f"✅ {rel_path}: {count} 行")
            total_files_changed += 1
            total_lines_changed += count
    
    print("-" * 70)
    print(f"\n✨ 修复完成!")
    print(f"📝 修改文件: {total_files_changed}/{len(test_files)}")
    print(f"📝 修改行数: {total_lines_changed}")
    print("=" * 70)
    
    if total_files_changed > 0:
        print("\n💡 下一步:")
        print("   1. 运行测试验证: docker exec askjeff-dev-backend-1 poetry run pytest tests/")
        print("   2. 提交更改: git add tests/ && git commit -m 'test: 修复测试路由前缀'")

if __name__ == "__main__":
    main()
