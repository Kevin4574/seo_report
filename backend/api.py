# backend/api.py
import os, re, uuid, time, subprocess, json
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse, JSONResponse
from dotenv import load_dotenv
from progress import _write

# ───── 环境 & 基本路径 ─────
BASE = Path(__file__).parent.resolve()
load_dotenv(BASE / ".env")

REPORTS   = BASE / "reports"
API_BASE  = os.getenv("API_BASE", "http://localhost:8000")
FRONTEND  = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───── 后台任务 ─────
def run_job(url: str, job_id: str):
    out_dir = REPORTS / job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 让 cli.py 自己分阶段写状态；这里只写最终状态
        subprocess.run(
            ["python", "cli.py", url, "--html", "--pdf", "--job-id", job_id],
            cwd=BASE, check=True
        )
        _write(out_dir, "done")
    except Exception:
        _write(out_dir, "error")
        raise

# ───── 提交任务 ─────
@app.post("/analyze")
async def analyze(payload: dict, bg: BackgroundTasks):
    url = payload.get("url")
    if not url:
        raise HTTPException(400, "Missing 'url'")

    job_id = time.strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6]
    job_dir = REPORTS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    _write(job_dir, "init")

    bg.add_task(run_job, url, job_id)
    return JSONResponse({"id": job_id})

# ───── 报告 Markdown ─────
@app.get("/report/{job_id}/markdown")
async def get_markdown(job_id: str):
    md_path = REPORTS / job_id / "report.md"
    if not md_path.exists():
        raise HTTPException(404, "Report not ready")

    text = md_path.read_text(encoding="utf-8")
    text = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'![{m.group(1)}]({API_BASE}/report/{job_id}/{m.group(2)})',
        text
    )
    return PlainTextResponse(text, media_type="text/plain")

# ───── 报告静态资源 ─────
@app.get("/report/{job_id}/{filename}")
async def get_asset(job_id: str, filename: str):
    fpath = REPORTS / job_id / filename
    if not fpath.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(str(fpath))

# ───── 进度接口 ─────
@app.get("/status/{job_id}")
async def get_status(job_id: str):
    fpath = REPORTS / job_id / "status.json"
    if not fpath.exists():
        raise HTTPException(404, "Unknown job_id")
    return JSONResponse(json.loads(fpath.read_text(encoding="utf-8")))


# ───── 健康检查接口 ─────
@app.get("/health")
def health():
    return {"status": "ok"}
