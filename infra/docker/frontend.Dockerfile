FROM node:20

WORKDIR /app

# 使用 Corepack/PNPM，锁定依赖安装
RUN corepack enable && npm config set registry https://registry.npmmirror.com

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm config set registry https://registry.npmmirror.com && pnpm install --frozen-lockfile

COPY frontend/ /app/

EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5173"]
