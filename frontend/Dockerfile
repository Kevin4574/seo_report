########################################
# 1️⃣ 构建阶段 (Builder)
FROM node:18 AS builder
WORKDIR /app

# ─── 安装依赖 ───
COPY frontend/package*.json ./
RUN npm ci --registry=https://registry.npmmirror.com

# ─── 复制源码并注入编译期变量 ───
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000   
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

COPY frontend/ .
RUN npm run build

########################################
# 2️⃣ 运行阶段 (Runtime)
FROM node:18 AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000   

COPY --from=builder /app ./

EXPOSE 3000
CMD ["npm", "start"]
