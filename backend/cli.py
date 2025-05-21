#!/usr/bin/env python3
"""
cli.py – 一键生成 SEO 报告（超细化进度 & 完整功能保留）

Usage:
  python cli.py https://www.example.com [--html] [--pdf] [--job-id JOB_ID]

执行流程：采集 → Lighthouse → 画图 → 渲染 Markdown/HTML/PDF → 完成
"""

import argparse
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from progress import _write

ROOT    = Path(__file__).parent.resolve()
REPORTS = ROOT / "reports"

def cli():
    p = argparse.ArgumentParser(description="一键生成 SEO 报告（超细化进度 & 完整功能保留）")
    p.add_argument("url", help="待检测 URL")
    p.add_argument("--html", action="store_true", help="同时生成 HTML 版")
    p.add_argument("--pdf",  action="store_true", help="同时生成 PDF 版")
    p.add_argument(
        "--job-id", dest="job_id",
        help="API 指定的 job_id；不传则自动生成",
        default=None
    )
    args = p.parse_args()

    # 生成或使用外部传入的 job_id
    job_id = args.job_id or (time.strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6])
    out_dir = REPORTS / job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 0️⃣ 阶段：初始化
        _write(out_dir, "init")

        # 1️⃣ 阶段：开始采集数据
        print(f"📥 1/5 采集基础数据 → {REPORTS}/raw.json")
        _write(out_dir, "fetch_start")
        subprocess.run([sys.executable, "run_audit.py", args.url], cwd=ROOT, check=True)
        _write(out_dir, "fetch_done")
        # 保留 raw.json 到 job 目录
        shutil.copy(REPORTS / "raw.json", out_dir / "raw.json")

        # 2️⃣ 阶段：Lighthouse 性能检测（已在 run_audit 中完成）
        print("🚀 2/5 Lighthouse 性能检测 …")
        _write(out_dir, "lighthouse")

        # 3️⃣ 阶段：开始生成图表
        print("🎨 3/5 生成图表 → *.png")
        _write(out_dir, "charts_start")
        subprocess.run([sys.executable, "charts.py"], cwd=ROOT, check=True)
        _write(out_dir, "charts_done")
        for img in (
            "gauge.png","headings.png","links.png","radar.png",
            "security_heatmap.png","schema_cloud.png","perf_line.png"
        ):
            shutil.move(REPORTS / img, out_dir / img)

        # 4️⃣ 阶段：渲染报告 (Markdown + HTML)
        print("📝 4/5 渲染 Markdown/HTML …")
        _write(out_dir, "render_md")
        subprocess.run([sys.executable, "render_report.py"], cwd=ROOT, check=True)
        _write(out_dir, "render_html")
        # 移动 report.md & report.html
        for fn in ("report.md", "report.html"):
            src = REPORTS / fn
            if src.exists():
                shutil.move(src, out_dir / fn)

        # 5️⃣ 阶段：PDF（可选）
        if args.pdf:
            print("📄 5/5 生成 PDF …")
            _write(out_dir, "render_pdf_start")
            # render_report.py 已经生成 report.pdf
            src = REPORTS / "report.pdf"
            if src.exists():
                shutil.move(src, out_dir / "report.pdf")
                _write(out_dir, "render_pdf_done")

        # ✅ 结束
        print(f"\n✅ 完成！所有文件已生成至：{out_dir}")
        _write(out_dir, "done")

    except Exception as e:
        _write(out_dir, "error")
        print(f"❌ 执行出错：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli()
