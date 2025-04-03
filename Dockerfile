FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 不在Dockerfile中设置密码，而是通过环境变量传入
# ENV PAPER_COLLECTOR_PASSWORD="password"

# 设置时区
RUN apt-get update && apt-get install -y tzdata curl && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建所需目录
RUN mkdir -p /app/data/collected-articles /app/logs /app/conf

# 复制项目文件
COPY src /app/src
COPY conf /app/conf
COPY run.py /app/

# 授予执行权限
RUN chmod +x /app/run.py

# 暴露API端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "run.py", "server"] 