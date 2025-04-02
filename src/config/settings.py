#!/usr/bin/env python3
# 配置文件
# 包含论文收集器的所有配置参数
# 作者: Liu Yide

import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# 输出文件夹配置
OUTPUT_FOLDER = os.path.join(DATA_DIR, 'collected-articles')

# 关键词配置
KEYWORDS = [
    "insect", "biologically", "microrobot", "miniature", "flapping", "mav", 
    "micro aerial vehicle", "origami", "CPG", "central pattern generator", "bionic", 
    "neuromorphic", "flight", "beetle", "dragonfly", "hovering", "liftoff", 
    "takeoff", "wing", "micromanipulator", "micromanipulation", "parallel mechanism", 
    "parallel robot", "parallel manipulator"
]

# RSS源配置
RSS_FEEDS = [
    "https://onlinelibrary.wiley.com/feed/26404567/most-recent",
    "https://iopscience.iop.org/journal/rss/1748-3190",
    "https://ieeexplore.ieee.org/rss/TOC7083369.XML",
    "https://www.nature.com/ncomms.rss",
    "https://www.nature.com/nature.rss",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv",
]

# arXiv API配置
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# 邮件配置
# 注意：不要在此处存储实际密码，请使用环境变量或conf/local_settings.py
SENDER_EMAIL = "17355626985@sohu.com"
SENDER_PASSWORD = "**********"  # 默认为空，实际使用时通过环境变量或本地配置覆盖
RECIPIENT_EMAIL = "wuchao2@sunline.cn"
SMTP_SERVER = "smtp.sohu.com"
SMTP_PORT = 25

# API服务器配置
API_HOST = "0.0.0.0"
API_PORT = 5000

# 尝试导入本地设置来覆盖默认值
try:
    from conf.local_settings import *
    print("已加载本地设置")
except ImportError:
    print("未找到本地设置，使用默认配置")

# 尝试从环境变量中读取敏感信息
SENDER_PASSWORD = os.environ.get('PAPER_COLLECTOR_PASSWORD', SENDER_PASSWORD) 