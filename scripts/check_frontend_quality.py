#!/usr/bin/env python3
"""
前端代码质量检查脚本

检查 Vue/TypeScript 代码质量

使用方法:
    python scripts/check_frontend_quality.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend" / "src"


class FrontendQualityChecker:
    """前端代码质量检查器"""
    
    def __init__(self):
        self.issues: List[Tuple[str, str, int, str]] = []
        self.stats = {
            "files_checked": 0,
            "issues_found": 0,
            "critical": 0,
            "warning": 0,
            "info": 0,
        }
    
    def check_all(self):
        """执行所有检查"""
        print("🔍 开始前端代码质量检查...\\n")
        
        # 检查 Vue 和 TS 文件
        vue_files = list(FRONTEND_DIR.rglob("*.vue"))
        ts_files = list(FRONTEND_DIR.rglob("*.ts"))
        all_files = vue_files + ts_files
        
        self.stats["files_checked"] = len(all_files)
        
        for file_path in all_files:
            self._check_file(file_path)
        
        self._print_report()
    
    def _check_file(self, file_path: Path):
        """检查单个文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\\n")
            
            # 1. 检查文件长度
            self._check_file_length(file_path, lines)
            
            # 2. 检查 console 调用
            self._check_console_calls(file_path, lines)
            
            # 3. 检查 TODO 注释
            self._check_todo_comments(file_path, lines)
            
            # 4. 检查 any 类型
            self._check_any_type(file_path, lines)
            
        except Exception as e:
            print(f"⚠️  无法检查文件 {file_path}: {e}")
    
    def _check_file_length(self, file_path: Path, lines: List[str]):
        """检查文件长度"""
        line_count = len(lines)
        
        if file_path.suffix == ".vue":
            if line_count > 1000:
                self._add_issue(
                    file_path, "critical", 1,
                    f"Vue 文件严重过长({line_count} 行),必须立即拆分(建议 ≤ 300 行)"
                )
            elif line_count > 500:
                self._add_issue(
                    file_path, "warning", 1,
                    f"Vue 文件过长({line_count} 行),建议拆分(建议 ≤ 300 行)"
                )
            elif line_count > 300:
                self._add_issue(
                    file_path, "info", 1,
                    f"Vue 文件较长({line_count} 行),考虑拆分"
                )
        
        elif file_path.suffix == ".ts":
            if line_count > 300:
                self._add_issue(
                    file_path, "warning", 1,
                    f"TS 文件过长({line_count} 行),建议拆分(建议 ≤ 200 行)"
                )
    
    def _check_console_calls(self, file_path: Path, lines: List[str]):
        """检查 console 调用"""
        for i, line in enumerate(lines, 1):
            if re.search(r'console\.(log|error|warn|info|debug)', line):
                # 排除注释
                if not line.strip().startswith('//'):
                    self._add_issue(
                        file_path, "warning", i,
                        f"发现 console 调用,生产环境应移除: {line.strip()[:60]}"
                    )
    
    def _check_todo_comments(self, file_path: Path, lines: List[str]):
        """检查 TODO 注释"""
        for i, line in enumerate(lines, 1):
            if "TODO" in line or "FIXME" in line or "HACK" in line:
                comment = line.strip()
                if len(comment) > 80:
                    comment = comment[:77] + "..."
                self._add_issue(
                    file_path, "info", i,
                    f"待办事项: {comment}"
                )
    
    def _check_any_type(self, file_path: Path, lines: List[str]):
        """检查 any 类型使用"""
        if file_path.suffix != ".ts":
            return
        
        for i, line in enumerate(lines, 1):
            # 检查 : any 或 <any>
            if re.search(r':\s*any\b|<any>', line):
                # 排除注释和字符串
                if not line.strip().startswith('//') and not line.strip().startswith('*'):
                    self._add_issue(
                        file_path, "warning", i,
                        f"使用了 any 类型,应该定义具体类型: {line.strip()[:60]}"
                    )
    
    def _add_issue(self, file_path: Path, severity: str, line: int, message: str):
        """添加问题"""
        rel_path = file_path.relative_to(ROOT_DIR)
        self.issues.append((str(rel_path), severity, line, message))
        self.stats["issues_found"] += 1
        if severity == "critical":
            self.stats["critical"] += 1
        elif severity == "warning":
            self.stats["warning"] += 1
        else:
            self.stats["info"] += 1
    
    def _print_report(self):
        """打印检查报告"""
        print("\\n" + "="*80)
        print("📊 前端代码检查报告")
        print("="*80)
        print(f"检查文件数: {self.stats['files_checked']}")
        print(f"发现问题数: {self.stats['issues_found']}")
        print(f"  - 🔴 严重问题: {self.stats['critical']}")
        print(f"  - ⚠️  警告: {self.stats['warning']}")
        print(f"  - ℹ️  信息: {self.stats['info']}")
        print("="*80)
        
        if not self.issues:
            print("\\n✅ 太棒了!没有发现问题!")
            return
        
        # 按严重程度排序
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        sorted_issues = sorted(
            self.issues,
            key=lambda x: (severity_order.get(x[1], 3), x[0], x[2])
        )
        
        # 分组显示
        for severity in ["critical", "warning", "info"]:
            severity_issues = [i for i in sorted_issues if i[1] == severity]
            if not severity_issues:
                continue
            
            icon = {"critical": "🔴", "warning": "⚠️ ", "info": "ℹ️ "}[severity]
            title = {"critical": "严重问题", "warning": "警告", "info": "信息"}[severity]
            print(f"\\n{icon} {title} ({len(severity_issues)} 个)")
            print("-" * 80)
            
            current_file = None
            for file_path, _, line, message in severity_issues:
                if file_path != current_file:
                    print(f"\\n📄 {file_path}")
                    current_file = file_path
                print(f"  行 {line}: {message}")
        
        print("\\n" + "="*80)
        print("💡 建议:")
        print("  1. 优先修复严重问题(🔴) - 立即拆分超大文件")
        print("  2. 处理警告(⚠️ ) - 移除 console,定义类型")
        print("  3. 查看信息(ℹ️ ) - 处理 TODO,了解改进点")
        print("  4. 参考 AGENTS/frontend-guidelines.md 前端规范")
        print("  5. 参考 AGENTS/optimization-patterns.md 优化模式")
        print("="*80)
        
        # 如果有严重问题,返回非零退出码
        if self.stats["critical"] > 0:
            sys.exit(1)


def main():
    """主函数"""
    checker = FrontendQualityChecker()
    checker.check_all()


if __name__ == "__main__":
    main()
