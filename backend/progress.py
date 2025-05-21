# backend/progress.py
from pathlib import Path
import json, time

# 10 个阶段，每个阶段 +10%
STAGES = [
    ("init",            "已排队，等待开始",       0),
    ("fetch_start",     "1/10 开始采集数据 …",    10),
    ("fetch_done",      "2/10 数据采集完成",      20),
    ("lighthouse",      "3/10 Lighthouse 性能检测 …", 30),
    ("charts_start",    "4/10 开始生成图表 …",      40),
    ("charts_done",     "5/10 图表生成完成",        50),
    ("render_md",       "6/10 渲染 Markdown …",    60),
    ("render_html",     "7/10 渲染 HTML …",       70),
    ("render_pdf_start","8/10 开始生成 PDF …",      80),
    ("render_pdf_done", "9/10 PDF 生成完成",        90),
    ("done",            "✅ 全部完成！",          100),
    ("error",           "❌ 任务出错，请稍后重试",  100),
]

def _write(job_dir: Path, stage_key: str):
    msg, pct = next(((m,p) for k,m,p in STAGES if k==stage_key), ("未知阶段",0))
    (job_dir/"status.json").write_text(
        json.dumps({
            "stage":   stage_key,
            "message": msg,
            "percent": pct,
            "ts":      int(time.time())
        }, ensure_ascii=False),
        encoding="utf-8"
    )
