# 论文收集器 (PaperCollector)

一个用于自动收集与特定关键词相关的学术论文的工具，支持从多个学术期刊RSS源和arXiv抓取最新论文。

作者: Liu Yide  
版本: 2.0

## 功能特点

- 自动从多个学术期刊RSS源获取最新论文
- 自动从arXiv获取最近90天内的相关论文
- 根据预定义关键词筛选相关论文
- 识别新发表的论文（与前一天相比）
- 发送包含新论文和所有论文的邮件报告
- 提供API接口，支持按需触发收集过程
- 支持Docker部署，便于在各种环境中运行

## 目录结构

```
├── conf/                      # 配置文件目录
│   ├── local_settings.py      # 本地配置（不提交到版本控制）
│   └── local_settings.example.py # 本地配置示例
├── data/                      # 数据目录
│   └── collected-articles/    # 收集的论文存放目录
├── logs/                      # 日志文件目录
├── src/                       # 源代码目录
│   ├── api/                   # API服务器模块
│   ├── config/                # 配置模块
│   ├── core/                  # 核心功能模块
│   └── utils/                 # 工具函数模块
├── Dockerfile                 # Docker构建文件
├── docker-compose.yml         # Docker Compose配置
└── run.py                     # 主入口点脚本
```

## 安装

### 依赖项

- Python 3.6+
- feedparser
- requests
- flask (仅API服务器需要)

```bash
pip install feedparser requests flask
```

### 配置

1. 复制配置文件示例并进行修改:

```bash
cp conf/local_settings.example.py conf/local_settings.py
```

2. 在`conf/local_settings.py`中设置您的邮箱信息和其他设置:

```python
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_password"
RECIPIENT_EMAIL = "recipient@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
```

## 使用方法

### 命令行运行

1. 测试邮件发送功能:

```bash
python run.py test-email
```

2. 运行一次性论文收集:

```bash
python run.py collect
```

3. 启动API服务器:

```bash
python run.py server
```

### Docker部署

1. 修改`docker-compose.yml`中的环境变量:

```yaml
environment:
  - PAPER_COLLECTOR_PASSWORD=your_password_here
```

2. 构建并启动容器:

```bash
docker-compose up -d
```

3. 查看日志:

```bash
docker-compose logs -f paper-collector
```

### API接口

- `GET /`: 显示API信息
- `GET /trigger`: 触发论文收集和邮件发送
- `GET /send-email`: 仅发送邮件（使用最新收集的数据）
- `GET /health`: 健康检查

#### 示例: 手动触发收集和邮件发送

```bash
curl http://localhost:5000/trigger
```

#### 示例: 仅发送邮件

```bash
curl http://localhost:5000/send-email
```

## 定时执行

使用Docker Compose部署时，已配置每天上午10点自动执行论文收集并发送邮件。cron作业会记录收集结果和邮件发送状态到日志文件。

## 输出文件

- `data/collected-articles/reading_list_YYYY-MM-DD.txt`: 每日完整的论文列表
- `data/collected-articles/reading_list_new.txt`: 新增论文列表
- `logs/paper_collector.log`: 核心功能日志
- `logs/api_server.log`: API服务器日志
- `logs/cron.log`: 定时任务日志

## 故障排除

如果遇到问题，可以查看日志文件：
- `logs/paper_collector.log`: 脚本执行日志
- `logs/api_server.log`: API服务器日志
- `logs/cron.log`: 定时任务日志

### 常见问题

#### 邮件发送失败
- 检查SMTP服务器设置
- 确认邮箱密码正确
- 检查网络连接

可以使用`test_email.py`脚本测试邮件发送功能：
```
python test_email.py
```

#### Docker容器无法启动
- 检查Docker和Docker Compose是否正确安装
- 检查配置文件是否存在
- 检查端口5000是否被其他应用占用 