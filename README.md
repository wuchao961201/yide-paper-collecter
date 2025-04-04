# YIDE论文收集器 (Paper Collector)

一个强大的自动化工具，用于从多个学术来源收集与特定关键词相关的最新研究论文。

作者: Wu Chao & Liu Yide  
版本: 2.1

## 主要功能

- 自动从多个学术期刊RSS源获取最新论文
- 支持从arXiv抓取最近90天内的相关论文
- 智能关键词筛选系统，准确识别相关研究
- 每日对比功能，自动标记新发表论文
- 自定义邮件报告，包含新论文和完整论文列表
- RESTful API接口，支持灵活触发和查询
- 完整的Docker支持，便于在任何环境部署
- 内置定时任务，自动执行日常收集工作

## 项目结构

```
├── conf/                      # 配置文件目录
│   ├── local_settings.py      # 本地配置（不提交到版本控制）
│   └── local_settings.example.py # 本地配置示例
├── data/                      # 数据目录
│   └── collected-articles/    # 收集的论文存放目录
├── logs/                      # 日志文件目录
├── src/                       # 源代码目录
│   ├── api/                   # API服务器模块
│   │   └── server.py          # API服务器实现
│   ├── config/                # 配置模块
│   ├── core/                  # 核心功能模块
│   │   └── paper_collector.py # 论文收集核心实现
│   └── utils/                 # 工具函数模块
├── Dockerfile                 # 主服务Docker构建文件
├── Dockerfile.cron            # 定时任务Docker构建文件
├── docker-compose.yml         # Docker Compose配置
├── .env.example               # 环境变量示例文件
├── cron_setup.sh              # 定时任务设置脚本
├── start_paper_collector.sh   # 服务启动脚本
└── run.py                     # 主入口点脚本
```

## 快速开始

### 方法1: 使用Docker（推荐）

1. 克隆仓库：
   ```bash
   git clone https://github.com/username/yide-paper-collecter.git
   cd yide-paper-collecter
   ```

2. 创建环境变量文件：
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置必要的环境变量
   ```

3. 启动服务：
   ```bash
   docker-compose up -d
   ```
   
服务将在后台运行，并监听5000端口。自动化定时任务将每天上午10点执行。

### 方法2: 本地安装

1. 确保已安装Python 3.6+：
   ```bash
   python --version
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 创建环境变量文件：
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置必要的环境变量
   ```

4. 运行服务：
   ```bash
   ./start_paper_collector.sh
   ```

## 配置详解

### 必需配置

在`.env`文件中设置以下参数：

```ini
# 邮件发送配置
SENDER_EMAIL=your_email@example.com
PAPER_COLLECTOR_PASSWORD=your_secure_password_here

# SMTP服务器配置
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USE_SSL=True

# Flask应用配置
SECRET_KEY=change_this_to_a_long_random_string
FLASK_ENV=production
```

也可以通过环境变量直接设置这些参数。

### 高级配置

可以在`src/config/settings.py`中修改其他参数：

```python
# API配置
API_HOST = "0.0.0.0"  # API监听地址
API_PORT = 8080       # API监听端口

# 论文收集配置
DAYS_TO_FETCH = 90    # 从arXiv获取的天数范围
MAX_RESULTS = 100     # 每个查询最大结果数
```

## 使用指南

### 命令行操作

收集论文并发送邮件：
```bash
python run.py collect
```

仅收集论文（不发送邮件）：
```bash
python run.py collect --no-email
```

启动API服务器：
```bash
python run.py server [--host HOST] [--port PORT]
```

测试邮件配置：
```bash
python run.py test-email
```

### API接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务信息和状态 |
| `/trigger` | GET | 触发一次完整的论文收集和邮件发送 |
| `/send-email` | GET | 仅发送邮件（使用最近一次收集的数据） |
| `/health` | GET | 健康检查 |

示例：
```bash
# 触发论文收集
curl http://localhost:5000/trigger

# 健康检查
curl http://localhost:5000/health
```

## 定时任务

本项目支持通过cron自动定时执行：

- Docker部署：使用docker-compose中配置的cron服务自动执行
- 本地部署：使用`cron_setup.sh`脚本设置系统cron任务

默认设置为每天上午10:00自动运行论文收集和邮件发送。

## 输出文件

- `data/collected-articles/reading_list_YYYY-MM-DD.txt`: 每日完整论文列表
- `data/collected-articles/reading_list_new.txt`: 新增论文列表
- `logs/paper_collector.log`: 核心功能日志
- `logs/api_server.log`: API服务器日志
- `logs/cron.log`: 定时任务日志

## 故障排除

常见问题及解决方案：

### 邮件发送失败
- 检查SMTP服务器设置和密码
- 确认网络连接正常
- 使用测试命令：`python run.py test-email -v`

### Docker相关问题
- 确保Docker和Docker Compose已正确安装
- 检查端口5000是否被占用：`lsof -i :5000`
- 查看容器日志：`docker-compose logs paper-collector`

### 论文收集问题
- 检查关键词设置是否合理
- 确认网络可以访问学术网站
- 查看详细日志：`tail -f logs/paper_collector.log`

## 贡献与支持

如发现问题或有改进建议，请联系开发团队或提交Issue/PR。

祝您使用愉快！

## 多用户订阅系统

最新版本的论文收集器支持多用户订阅系统，允许多个用户注册自己的账号，配置个性化的RSS源和关键词，并在自定义时间接收论文邮件。

### 特性

1. **用户认证系统**：支持用户注册、登录和密码管理
2. **个性化订阅**：每个用户可以设置自己的RSS源和关键词
3. **定时发送**：用户可以设置每天接收邮件的时间
4. **仪表盘界面**：直观显示用户订阅状态和最近收到的论文

### 安装和配置

首先安装所需的依赖：

```bash
pip install -r requirements.txt
```

初始化数据库：

```bash
python run.py init-db
```

### 运行Web应用

启动Web应用：

```bash
python run.py web
```

默认情况下，应用将在 http://0.0.0.0:5000 上运行。

### 设置定时任务

论文收集器使用定时任务来检查和发送论文。使用提供的脚本设置cron作业：

```bash
bash cron_setup.sh
```

这将创建一个每小时执行一次的cron作业，检查是否有用户的发送时间与当前时间匹配，并为这些用户收集和发送论文。

### 手动触发收集

您也可以手动为特定用户触发论文收集：

```bash
# 为指定用户ID收集论文
python run.py collect --user-id 1

# 为所有当前时间应接收邮件的用户收集论文
python run.py collect --all-users
```

### 迁移

如果您之前使用的是基于配置文件的版本，可以通过以下步骤迁移到多用户系统：

1. 运行Web应用并注册一个新用户
2. 登录后，在"关键词"页面中批量导入您之前在配置文件中定义的关键词
3. 在"RSS源"页面中批量导入您之前的RSS源
4. 设置您想要接收邮件的时间 