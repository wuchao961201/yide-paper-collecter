#!/usr/bin/env python3
# 本地配置示例文件
# 请复制为local_settings.py并填入实际的配置信息
# 作者: Liu Yide

# 腾讯SES邮件服务配置
# 在腾讯云SES控制台创建的发信人地址
SENDER_EMAIL = "your-sender@example.com"
# 在腾讯云SES控制台为发信地址设置的SMTP密码
SENDER_PASSWORD = "your-smtp-password"
# 邮件接收人地址，可以是字符串或列表
RECIPIENT_EMAIL = "recipient@example.com"
# 或者多个收件人
# RECIPIENT_EMAIL = ["recipient1@example.com", "recipient2@example.com"]

# 腾讯SES SMTP服务器配置
# 可选的地区服务器: 
# - smtp.qcloudmail.com (香港)
# - sg-smtp.qcloudmail.com (新加坡)
# - gz-smtp.qcloudmail.com (广州)
SMTP_SERVER = "smtp.qcloudmail.com"
SMTP_PORT = 465  # 465或587使用SSL，25使用TLS
SMTP_USE_SSL = True  # 使用SSL加密连接

# 其他可选配置
# 自定义收集的RSS源
# RSS_FEEDS = [
#    "https://your-custom-rss-feed.com/feed",
# ]

# 自定义关键词
# KEYWORDS = [
#    "your-custom-keyword1",
#    "your-custom-keyword2",
# ] 