# backend/Dockerfile  ── 修正版
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

# 1️⃣ 安装 Node.js 18 与 Lighthouse
RUN apt-get update \
 && apt-get install -y curl gnupg ca-certificates \
 && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get install -y nodejs \
 && npm install -g lighthouse

# 2️⃣ 让 Lighthouse 用 Playwright 自带的 Chromium
RUN CHROME_BIN=$(find /ms-playwright -type f -path "*/chrome-linux/chrome" | head -n1) \
 && ln -sf "$CHROME_BIN" /usr/bin/chrome \
 && echo "Linked Playwright Chromium ➜ $CHROME_BIN -> /usr/bin/chrome"

# 3️⃣ 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ 复制后端源码，再打补丁修改启动参数
COPY backend/ .
# 给所有 Lighthouse 调用追加 root 模式下必需的 flags
RUN sed -i \
    's/--headless"/--headless --no-sandbox --disable-gpu --disable-dev-shm-usage"/' \
    /app/run_audit.py

# 5️⃣ 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    API_BASE=http://localhost:8000 \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    CHROME_PATH=/usr/bin/chrome

# 6️⃣ 暴露端口 & 启动服务
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]


