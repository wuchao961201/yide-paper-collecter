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
RUN apt-get update && apt-get install -y tzdata curl cron && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建所需目录
RUN mkdir -p /app/data/collected-articles /app/logs /app/conf /app/src/static /app/src/templates

# 复制项目文件
COPY src /app/src
COPY run.py /app/

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 创建cron日志文件\n\
touch /app/logs/cron.log\n\
\n\
# 获取定时任务配置，默认为每1分钟运行一次\n\
CRON_SCHEDULE="${CRON_SCHEDULE:-*/1 * * * *}"\n\
\n\
# 获取当前PATH\n\
PATH_VALUE=$(echo $PATH)\n\
\n\
# 创建临时crontab文件\n\
cat > /tmp/crontab << EOF\n\
SHELL=/bin/bash\n\
PATH=$PATH_VALUE\n\
$CRON_SCHEDULE curl -X POST -H "X-API-Key: ${SECRET_KEY}" http://localhost:8080/user/api/trigger-all-collection >> /app/logs/cron.log 2>&1\n\
EOF\n\
\n\
# 安装crontab\n\
crontab /tmp/crontab\n\
rm /tmp/crontab\n\
\n\
# 启动cron服务\n\
service cron start\n\
\n\
# 初始化数据库并启动Web应用\n\
python run.py init-db && python run.py web\n\
' > /app/start.sh

# 授予执行权限
RUN chmod +x /app/run.py
RUN chmod +x /app/start.sh

# 暴露API端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD curl -f http://localhost:8080/health || exit 1

# 启动脚本
CMD ["/bin/bash", "/app/start.sh"] 