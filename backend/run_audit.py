#!/usr/bin/env python3
# run_audit.py
# 一键采集 SEO 数据 + Lighthouse 性能指标 → 保存 reports/raw.json

import argparse
import json
import subprocess
import sys
from pathlib import Path

from seo_audit_tool import audit

def fetch_lighthouse(url: str, timeout: int = 120) -> dict:
    cmd = (
        f'npx lighthouse "{url}" --quiet '
        '--chrome-flags="--headless" --output=json'
    )
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        print("⚠️ Lighthouse 执行超时", file=sys.stderr)
        return {}

    if proc.returncode != 0:
        print("⚠️ Lighthouse 执行失败，stderr:", proc.stderr, file=sys.stderr)
        return {}

    raw = proc.stdout or ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("❌ JSON 解析 Lighthouse 输出失败:", e, file=sys.stderr)
        return {}

    audits = data.get("audits", {})
    return {
        "lcp": audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
        "inp": audits.get("interactive", {}).get("numericValue", 0),
        "cls": audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
    }


def main():
    p = argparse.ArgumentParser(description="采集 SEO 报告原始数据")
    p.add_argument("url", help="要分析的目标 URL")
    p.add_argument(
        "--no-render", action="store_true",
        help="仅静态抓取，不使用浏览器渲染"
    )
    p.add_argument(
        "--wait", type=int, default=3000,
        help="渲染模式下等待毫秒数 (default: 3000)"
    )
    args = p.parse_args()

    url = args.url
    print(f"🔍 采集 SEO 基础数据：{url}")
    rep = audit(url, render=not args.no_render, wait=args.wait)

    print("🚀 开始 Lighthouse 性能检测…")
    perf = fetch_lighthouse(url)
    rep["perf"] = perf

    # 确保输出目录存在
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 写入 JSON
    raw_path = out_dir / "raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(f"✅ 采集完成，原始数据已保存至：{raw_path}")

if __name__ == "__main__":
    main()

