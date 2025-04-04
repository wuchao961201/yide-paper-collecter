# Docker部署指南（多用户版）

本文档提供了如何使用Docker部署论文收集器多用户版本的详细说明。

## 前提条件

1. 安装 [Docker](https://docs.docker.com/get-docker/)
2. 安装 [Docker Compose](https://docs.docker.com/compose/install/)
3. 基本的命令行操作知识

## 快速部署

### 步骤1: 准备环境

1. 克隆项目仓库：

```bash
git clone https://github.com/username/yide-paper-collecter.git
cd yide-paper-collecter
```

2. 创建环境变量文件：

```bash
cp .env.example .env
```

3. 编辑`.env`文件，设置必要的环境变量：

```
# 编辑邮件发送密码
PAPER_COLLECTOR_PASSWORD=your_secure_password_here

# 设置安全密钥（使用随机字符串）
SECRET_KEY=your_random_secret_key_here
```

### 步骤2: 构建和启动容器

运行以下命令启动服务：

```bash
docker-compose up -d
```

这将启动两个容器：
- `paper-collector`: Web应用和API服务
- `paper-collector-cron`: 定时任务服务，每小时检查一次是否有用户需要在当前时间接收论文

### 步骤3: 访问Web界面

在浏览器中访问 `http://your_server_ip:8080` 即可打开论文收集器的Web界面。

首次访问时，您需要注册一个新账户。注册后，您可以：
1. 添加RSS源
2. 配置关键词
3. 设置您希望接收邮件的时间

## 容器管理

### 查看日志

查看Web应用日志：

```bash
docker logs paper-collector
```

查看定时任务日志：

```bash
docker logs paper-collector-cron
```

或者查看宿主机上的日志文件：

```bash
tail -f logs/paper_collector.log
tail -f logs/cron.log
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 更新服务

当有新版本时，可以执行以下步骤更新：

```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 数据持久化

所有重要数据都存储在以下目录，并通过卷挂载到Docker容器：

- `./data`: 数据库和收集的论文
- `./logs`: 日志文件
- `./conf`: 配置文件

为确保数据安全，建议定期备份这些目录。

## 高级配置

### 使用外部数据库

默认情况下，应用使用SQLite数据库。如果您希望使用外部数据库（例如MySQL或PostgreSQL），可以在`.env`文件中修改`DATABASE_URL`：

对于MySQL：
```
DATABASE_URL=mysql+pymysql://username:password@mysql_host:3306/paper_collector
```

对于PostgreSQL：
```
DATABASE_URL=postgresql://username:password@postgres_host:5432/paper_collector
```

修改后重启服务即可。

### 自定义端口

本应用在容器内使用端口8080运行。如果需要修改宿主机映射端口，编辑`docker-compose.yml`文件中的端口映射：

```yaml
ports:
  - "9090:8080"  # 将宿主机端口从8080改为9090
```

## 故障排查

### Web应用无法启动

1. 检查日志：`docker logs paper-collector`
2. 确保环境变量设置正确：`cat .env`
3. 确保数据目录可写：`chmod -R 777 data logs`

### 定时任务不执行

1. 检查定时任务日志：`docker logs paper-collector-cron`
2. 确认容器时区设置正确：`docker exec paper-collector-cron date`
3. 手动触发收集测试：`docker exec paper-collector python run.py collect --all-users`

### 邮件发送失败

1. 检查SMTP设置是否正确(在`conf/local_settings.py`中)
2. 验证`PAPER_COLLECTOR_PASSWORD`环境变量设置正确
3. 使用测试命令：`docker exec paper-collector python run.py test-email`
