#!/usr/bin/env python3
"""
代码质量自动检查脚本 v2.0

按照 AGENTS/coding-guidelines.md 中的自检清单自动扫描代码问题。

新增功能:
- 检查文件长度
- 检查函数复杂度
- 检查 TODO 注释

使用方法:
    python scripts/check_code_quality.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend" / "app"


class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self):
        self.issues: List[Tuple[str, str, int, str]] = []  # (file, severity, line, message)
        self.stats = {
            "files_checked": 0,
            "issues_found": 0,
            "critical": 0,
            "warning": 0,
            "info": 0,
        }
    
    def check_all(self):
        """执行所有检查"""
        print("🔍 开始代码质量检查 v2.0...\\n")
        
        # 检查 Python 文件
        py_files = list(BACKEND_DIR.rglob("*.py"))
        self.stats["files_checked"] = len(py_files)
        
        for file_path in py_files:
            self._check_file(file_path)
        
        self._print_report()
    
    def _check_file(self, file_path: Path):
        """检查单个文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\\n")
            
            # 1. 检查文件长度
            self._check_file_length(file_path, lines)
            
            # 2. 检查 HTTP 超时配置
            self._check_http_timeout(file_path, lines)
            
            # 3. 检查分页限制
            self._check_pagination_limit(file_path, lines)
            
            # 4. 检查敏感数据记录
            self._check_sensitive_logging(file_path, lines)
            
            # 5. 检查函数复杂度
            self._check_function_complexity(file_path, lines)
            
            # 6. 检查 TODO 注释
            self._check_todo_comments(file_path, lines)
            
        except Exception as e:
            print(f"⚠️  无法检查文件 {file_path}: {e}")
    
    def _check_file_length(self, file_path: Path, lines: List[str]):
        """检查文件长度"""
        line_count = len(lines)
        if line_count > 500:
            self._add_issue(
                file_path, "warning", 1,
                f"文件过长({line_count} 行),建议拆分(建议 ≤ 300 行)"
            )
        elif line_count > 300:
            self._add_issue(
                file_path, "info", 1,
                f"文件较长({line_count} 行),考虑拆分"
            )
    
    def _check_function_complexity(self, file_path: Path, lines: List[str]):
        """检查函数复杂度(简化版 - 只检查行数)"""
        in_function = False
        function_start = 0
        function_name = ""
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            # 检测函数定义
            func_match = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
            if func_match:
                # 保存上一个函数的信息
                if in_function and function_start > 0:
                    func_length = i - function_start
                    if func_length > 120:
                        self._add_issue(
                            file_path, "warning", function_start,
                            f"函数 {function_name} 过长({func_length} 行),建议拆分(建议 ≤ 80 行)"
                        )
                    elif func_length > 80:
                        self._add_issue(
                            file_path, "info", function_start,
                            f"函数 {function_name} 较长({func_length} 行),考虑拆分"
                        )
                
                # 开始新函数
                in_function = True
                function_start = i
                function_name = func_match.group(2)
                indent_level = len(func_match.group(1))
            
            # 检测函数结束(遇到同级或更低缩进的非空行)
            elif in_function and line.strip() and not line.strip().startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and not line.strip().startswith('@'):
                    # 函数结束
                    func_length = i - function_start
                    if func_length > 120:
                        self._add_issue(
                            file_path, "warning", function_start,
                            f"函数 {function_name} 过长({func_length} 行),建议拆分(建议 ≤ 80 行)"
                        )
                    elif func_length > 80:
                        self._add_issue(
                            file_path, "info", function_start,
                            f"函数 {function_name} 较长({func_length} 行),考虑拆分"
                        )
                    in_function = False
    
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
    
    def _check_http_timeout(self, file_path: Path, lines: List[str]):
        """检查 HTTP 客户端超时配置"""
        for i, line in enumerate(lines, 1):
            # 检查 httpx.AsyncClient 是否有超时配置
            if "httpx.AsyncClient(" in line and "timeout=" not in line:
                # 检查下一行是否有 timeout
                next_lines = "".join(lines[i:min(i+3, len(lines))])
                if "timeout=" not in next_lines:
                    self._add_issue(
                        file_path, "critical", i,
                        "httpx.AsyncClient 缺少超时配置,可能导致请求永久阻塞"
                    )
            
            # 检查 httpx.post/get 等方法
            if re.search(r'httpx\.(post|get|put|delete|patch)\(', line):
                # 检查是否有 timeout 参数
                method_call = "".join(lines[i-1:min(i+5, len(lines))])
                if "timeout=" not in method_call:
                    self._add_issue(
                        file_path, "warning", i,
                        "HTTP 请求建议添加 timeout 参数"
                    )
    
    def _check_pagination_limit(self, file_path: Path, lines: List[str]):
        """检查分页查询限制"""
        for i, line in enumerate(lines, 1):
            # 检查 Query 参数中的 page_size
            if "page_size" in line and "Query(" in line:
                if "le=" not in line and "lt=" not in line:
                    self._add_issue(
                        file_path, "warning", i,
                        "分页参数 page_size 建议添加上限(le=200)"
                    )
    
    def _check_sensitive_logging(self, file_path: Path, lines: List[str]):
        """检查敏感数据记录"""
        sensitive_patterns = [
            (r'logger\.(info|debug|warning).*password["\']?\s*:', "密码"),
            (r'logger\.(info|debug|warning).*api_key["\']?\s*:', "API Key"),
            (r'logger\.(info|debug|warning).*token["\']?\s*:', "Token"),
            (r'logger\.(info|debug|warning).*secret["\']?\s*:', "Secret"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, name in sensitive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # 检查是否有脱敏处理
                    if "***" not in line and "mask" not in line.lower():
                        self._add_issue(
                            file_path, "critical", i,
                            f"日志中可能记录了未脱敏的{name},请检查"
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
        print("📊 检查报告")
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
        print("  1. 优先修复严重问题(🔴)")
        print("  2. 处理警告(⚠️ )")
        print("  3. 查看信息(ℹ️ )了解代码改进点")
        print("  4. 参考 AGENTS/coding-guidelines.md 中的自检清单")
        print("  5. 参考 AGENTS/optimization-patterns.md 查找优化模式")
        print("="*80)
        
        # 如果有严重问题,返回非零退出码
        if self.stats["critical"] > 0:
            sys.exit(1)


def main():
    """主函数"""
    checker = CodeQualityChecker()
    checker.check_all()


if __name__ == "__main__":
    main()
