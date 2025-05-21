#!/usr/bin/env python3
"""
把 Markdown 转为自带样式的单页 HTML。
"""

from pathlib import Path
import markdown

def md_to_html(md_path: Path, out_path: Path) -> Path:
    # 1) 读取 Markdown
    md_text = md_path.read_text(encoding="utf-8")
    # 2) 转 HTML（启用表格/代码块扩展）
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code"]
    )
    # 3) 包裹完整 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>SEO Audit Report</title>
  <style>
    body {{ max-width: 800px; margin: auto; padding: 20px; font-family: sans-serif; }}
    img {{ max-width: 100%; }}
    pre {{ background: #f4f4f4; padding: 10px; overflow: auto; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 8px; }}
    details {{ margin: 8px 0; }}
  </style>
</head>
<body>
{html_body}
</body>
</html>"""
    # 4) 写出文件
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ 已生成 HTML：{out_path}")
    return out_path

# 支持脚本直接执行
if __name__ == "__main__":
    reports = Path(__file__).parent / "reports"
    md_file = reports / "report.md"
    html_file = reports / "report.html"
    if md_file.exists():
        md_to_html(md_file, html_file)
    else:
        print("❌ 找不到 report.md，请先生成 Markdown 报告。")
