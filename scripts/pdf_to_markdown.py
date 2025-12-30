#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from pdfminer.high_level import extract_text

def convert_pdf_to_markdown(pdf_path, output_dir):
    """
    将 PDF 文件转换为 Markdown 文本文件
    """
    try:
        print(f"正在处理: {pdf_path.name} ...")
        
        # 提取文本
        text = extract_text(pdf_path)
        
        # 简单的清洗
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        content = '\n\n'.join(cleaned_lines)
        
        # 生成输出文件名
        output_filename = pdf_path.stem + ".md"
        output_path = output_dir / output_filename
        
        # 添加元数据头
        markdown_content = f"""# {pdf_path.stem}

> 来源文件: {pdf_path.name}
> 提取时间: {import_time()}

---

{content}
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"✅ 已生成: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败 {pdf_path.name}: {str(e)}")
        return False

def import_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    # 基础路径配置
    base_dir = Path(__file__).parent.parent
    references_dir = base_dir / "docs/knowledge/references"
    output_dir = base_dir / "docs/knowledge/raw_extracts"
    
    # 检查目录
    if not references_dir.exists():
        print(f"创建目录: {references_dir}")
        references_dir.mkdir(parents=True, exist_ok=True)
        print(f"请将 PDF 文件放入 {references_dir} 后再次运行此脚本")
        return

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有 PDF
    pdfs = list(references_dir.glob("*.pdf"))
    
    if not pdfs:
        print(f"⚠️  在 {references_dir} 中未找到 PDF 文件")
        print("请将需要转换的 PDF 文件放入该目录")
        return

    print(f"找到 {len(pdfs)} 个 PDF 文件，准备转换...")
    
    # 检查依赖
    try:
        import pdfminer
    except ImportError:
        print("❌ 缺少依赖: pdfminer.six")
        print("请运行: pip install pdfminer.six")
        return

    # 执行转换
    success_count = 0
    for pdf in pdfs:
        if convert_pdf_to_markdown(pdf, output_dir):
            success_count += 1
            
    print(f"\n🎉 完成! 成功转换 {success_count}/{len(pdfs)} 个文件")
    print(f"输出目录: {output_dir}")
    print("\n建议后续步骤:")
    print("1. 阅读生成的 .md 文件")
    print("2. 人工整理结构，提取核心知识点")
    print("3. 将精华内容合并到 docs/knowledge/ 下的分类文档中")

if __name__ == "__main__":
    main()
