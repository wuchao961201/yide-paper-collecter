#!/usr/bin/env python3
# 本地配置文件示例
# 复制此文件为 local_settings.py 并填入您的实际配置
# 该文件不应提交到版本控制系统

# 邮件配置
SENDER_EMAIL = ""
SENDER_PASSWORD = "**********"  # 默认为空，实际使用时通过环境变量或本地配置覆盖
RECIPIENT_EMAIL = ""
SMTP_SERVER = ""
SMTP_PORT = 25

# 自定义关键词 (可选，如果定义则会覆盖默认关键词)
# KEYWORDS = [
#     "your_keyword1",
#     "your_keyword2",
#     # ...
# ]

# 自定义RSS源 (可选，如果定义则会覆盖默认RSS源)
# RSS_FEEDS = [
#     "https://your-rss-feed-url-1",
#     "https://your-rss-feed-url-2",
#     # ...
# ]

# API服务器配置 (可选)
# API_HOST = "0.0.0.0"
# API_PORT = 5000 