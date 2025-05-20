# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=project.settings

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建metrics目录
RUN mkdir -p /app/metrics && chmod 777 /app/metrics

# 创建静态文件目录
RUN mkdir -p /app/static /app/media

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000
EXPOSE 3000

# 启动命令
CMD ["gunicorn", "project.wsgi_prometheus:application", "--workers", "4", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--log-format", "'{\"time\": \"%(asctime)s\", \"level\": \"%(levelname)s\", \"message\": \"%(message)s\", \"module\": \"%(module)s\", \"function\": \"%(funcName)s\", \"status\": \"%(s)s\", \"request_id\": \"%({X-Request-Id}o)s\"}'", "--env", "PROMETHEUS_MULTIPROC_DIR=/app/metrics"]