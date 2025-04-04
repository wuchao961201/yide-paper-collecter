# YIDE论文收集器

一个智能学术论文订阅系统，自动从多个学术源收集并筛选与您研究兴趣相关的最新论文。

作者: Wu Chao & Liu Yide  
版本: 3.0

## 核心特性

- **多源采集**：自动从arXiv、TechRxiv及自定义RSS源获取最新学术论文
- **智能筛选**：基于用户定义的关键词精准匹配相关研究内容
- **个性化订阅**：每位用户可独立设置关键词、RSS源和接收时间
- **定时推送**：在用户指定时间将筛选后的论文发送至邮箱
- **去重机制**：智能记录已发送论文，避免重复推送相同内容
- **Web管理界面**：用户友好的界面，轻松管理订阅设置
- **Docker部署**：完整容器化支持，简化部署和维护流程

## Docker部署指南

### 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 部署步骤

1. 克隆仓库：
```bash
git clone https://github.com/wuchao961201/yide-paper-collecter.git
cd yide-paper-collecter
```

2. 创建环境变量文件：
```bash
cp .env.example .env
# 编辑.env文件配置邮箱和SMTP信息
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问Web界面：`http://your_server_ip:8080`

服务包含两个容器：
- `paper-collector`：Web应用和API服务
- `paper-collector-cron`：定时任务服务（按用户设置的时间发送论文）

### 容器管理

```bash
# 查看服务日志
docker logs paper-collector
docker logs paper-collector-cron

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新服务
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 环境配置

必要的环境变量（在`.env`文件中设置）：

```ini
# 邮件配置
SENDER_EMAIL=your_email@example.com
PAPER_COLLECTOR_PASSWORD=your_password
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USE_SSL=True

# 安全配置
SECRET_KEY=your_random_string

# 可选：自定义数据库（默认使用SQLite）
# DATABASE_URL=mysql+pymysql://username:password@mysql_host:3306/paper_collector
```

## 使用指南

### 用户界面

注册并登录后，您可以：

1. **仪表盘**：查看订阅状态和收集统计信息
2. **关键词管理**：添加/编辑您感兴趣的研究关键词
3. **RSS源管理**：配置要监控的学术期刊/网站RSS链接
   - 系统默认已配置arXiv和TechRxiv源
   - 您可添加其他学术期刊的RSS链接
4. **发送设置**：自定义接收邮件的时间（24小时制，如"08:00"）
5. **账户设置**：管理邮箱和密码等个人信息

### 命令行工具

```bash
# 初始化数据库
docker exec paper-collector python run.py init-db

# 手动为特定用户收集论文
docker exec paper-collector python run.py collect --user-id 1

# 为所有配置了当前时间的用户收集论文
docker exec paper-collector python run.py collect --all-users

# 启动Web应用（容器已自动运行）
docker exec paper-collector python run.py web
```

## 系统架构

- **Web应用**：Flask应用，提供用户界面和API
- **数据库**：SQLite（默认）或MySQL/PostgreSQL（可配置）
- **定时任务**：每小时检查，为设置了当前时间的用户收集和发送论文
- **论文收集**：自动从arXiv API、TechRxiv和自定义RSS源获取论文
- **邮件模块**：根据用户偏好发送格式化的论文邮件报告

## 故障排除

- **邮件发送失败**：
  - 检查SMTP服务器设置和密码
  - 确认邮箱安全设置允许第三方应用登录

- **论文收集问题**：
  - 确认关键词设置是否合理
  - 检查RSS链接是否有效
  - 查看日志：`docker logs paper-collector`

- **容器启动问题**：
  - 检查端口8080是否被占用：`lsof -i :8080`
  - 确认Docker和Docker Compose正确安装

## 支持与贡献

如有问题或改进建议，请联系开发团队或提交Issue。 