#!/usr/bin/env python3
# render_report.py

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from scoring import get_scores
from seo_audit_tool import quick_tips

# ────────────────────────────────────────────────────────────────
# 1️⃣ 加载环境变量
# ----------------------------------------------------------------
ROOT = Path(__file__).parent.resolve()
load_dotenv(ROOT / ".env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    sys.exit("⚠️ 请在 .env 中设置 DEEPSEEK_API_KEY")

# ────────────────────────────────────────────────────────────────
# 2️⃣ DeepSeek 接口配置
# ----------------------------------------------------------------
DEEPSEEK_URL   = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# ────────────────────────────────────────────────────────────────
# 3️⃣ DeepSeek 请求封装
# ----------------------------------------------------------------
def chat_with_deepseek(messages, functions=None, tool_choice="auto"):
    payload = {
        "model":    DEEPSEEK_MODEL,
        "messages": messages
    }
    if functions:
        payload["tools"]       = [{"type": "function", "function": f} for f in functions]
        payload["tool_choice"] = tool_choice

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type":  "application/json"
    }
    resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()

# ────────────────────────────────────────────────────────────────
# 4️⃣ 渲染主流程
# ----------------------------------------------------------------
def main():
    # —— 读取原始数据 ——
    raw_path = Path("reports/raw.json")
    if not raw_path.exists():
        sys.exit("❌ 找不到 reports/raw.json，请先运行 run_audit.py")
    rep = json.loads(raw_path.read_text(encoding="utf-8"))

    # —— 计算分数 & 快速提示 ——
    scores = get_scores(rep)
    quick_tips_list = quick_tips(rep)
    perf = rep.get("perf", {})

    # —— 构造 LLM 调用消息 ——
    system_msg = {
        "role": "system",
        "content": (
            "你是专业 SEO 顾问，请**仅**以有效的 JSON 对象形式回复，"
            "不要输出任何多余文字或解释。"
        )
    }
    user_msg = {
        "role": "user",
        "content": (
            "请基于以下 JSON 数据返回一个 JSON 对象，包含字段：\n"
            "- summary_one_sentence（一句核心总结）\n"
            "- advice（建议列表，3-5 条）\n\n"
            f"scores: {scores}\n"
            f"analysis: {rep['analysis']}\n"
            f"robots: {rep['robots']}\n"
            f"security: {rep['security']}\n"
        )
    }

    # —— 调用 DeepSeek ——
    response = chat_with_deepseek(messages=[system_msg, user_msg])
    choice   = response["choices"][0]["message"]
    content  = choice.get("content", "")

    # —— 调试：打印原始输出 ——
    print(">>> LLM 原始输出开始 >>>")
    print(content)
    print("<<< LLM 原始输出结束 <<<")

    # —— 清洗 content —— 去掉 ```json 等标记
    for fence in ("```json", "```"):
        content = content.replace(fence, "")
    content = content.strip()

    # —— 解析 JSON ——
    try:
        llm_json = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        sys.exit("❌ LLM 返回格式有问题，请检查原始输出")

    # —— 渲染 Markdown 模板 ——
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))
    tpl = env.get_template("report.md.j2")
    markdown = tpl.render(
        rep=rep,
        scores=scores,
        quick_tips=quick_tips_list,
        perf=perf,
        llm=llm_json,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # —— 写入 report.md ——
    md_path = ROOT / "reports" / "report.md"
    md_path.write_text(markdown, encoding="utf-8")
    print("✅ report.md 已生成：", md_path)

    # —— 生成 HTML —— 同前
    from md_to_html import md_to_html
    html_path = ROOT / "reports" / "report.html"
    md_to_html(md_path, html_path)

    # —— 使用 Playwright 生成 PDF ——
    try:
        from playwright.sync_api import sync_playwright

        pdf_path = ROOT / "reports" / "report.pdf"
        print("📄 使用 Playwright 生成 PDF →", pdf_path)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{html_path.resolve()}")
            page.pdf(path=str(pdf_path), format="A4")
            browser.close()
        print("✅ report.pdf 已生成：", pdf_path)
    except Exception as e:
        print("❌ Playwright PDF 生成失败：", e)

if __name__ == "__main__":
    main()
