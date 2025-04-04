FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置pip配置以解决超时问题
RUN pip config set global.timeout 100 && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --upgrade pip

# 安装依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --default-timeout=100 -r requirements.txt

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src.app
# 不在Dockerfile中设置密码，而是通过环境变量传入
# ENV PAPER_COLLECTOR_PASSWORD="password"

# 设置时区
RUN apt-get update && apt-get install -y tzdata curl && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建所需目录
RUN mkdir -p /app/data/collected-articles /app/logs /app/conf /app/src/static /app/src/templates

# 复制项目文件
COPY src /app/src
COPY run.py /app/
COPY cron_task.py /app/

# 授予执行权限
RUN chmod +x /app/run.py
RUN chmod +x /app/cron_task.py

# 暴露API端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD curl -f http://localhost:8080/health || exit 1

# 初始化数据库并启动Web应用
CMD ["sh", "-c", "python run.py init-db && python run.py web"] 