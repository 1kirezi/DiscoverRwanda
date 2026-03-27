FROM node:20-alpine AS frontend-build

WORKDIR /build/client
COPY client/package*.json ./
RUN npm install --legacy-peer-deps
COPY client/ ./
RUN npm run build

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev default-libmysqlclient-dev pkg-config default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server

RUN mkdir -p /app/server/app/static
COPY --from=frontend-build /build/client/dist /app/server/app/static

WORKDIR /app/server

EXPOSE 8000

CMD ["sh", "/app/server/scripts/docker-entrypoint.sh"]
