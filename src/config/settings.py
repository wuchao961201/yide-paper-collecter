#!/usr/bin/env python3
# 配置文件
# 包含论文收集器的所有配置参数
# 作者: Liu Yide

import os
import logging
from datetime import timedelta

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# 确保必要目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# 输出文件夹配置
OUTPUT_FOLDER = os.path.join(DATA_DIR, 'collected-articles')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# arXiv API配置
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# TechRxiv API配置
TECHRXIV_API_URL = "https://ieeexplore.ieee.org/feed/rss/TechRxiv"

# 邮件配置 - 从环境变量读取
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
if not SENDER_EMAIL:
    logger.warning("SENDER_EMAIL 未在环境变量中设置")

# SMTP配置 - 从环境变量读取
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', 'True').lower() in ('true', '1', 't')

if not SMTP_SERVER:
    logger.warning("SMTP_SERVER 未在环境变量中设置")

# API服务器默认配置
API_HOST = "0.0.0.0"
API_PORT = 8080

# Flask应用配置 - 从环境变量读取
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logger.warning("SECRET_KEY 未在环境变量中设置，这在生产环境中是不安全的")
    SECRET_KEY = 'dev-key-please-change-in-production'

FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

# Session配置
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# 数据库配置
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(DATA_DIR, "paper_collector.db")}')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 邮件密码 - 从环境变量读取
SENDER_PASSWORD = os.environ.get('PAPER_COLLECTOR_PASSWORD')
if not SENDER_PASSWORD:
    logger.warning("PAPER_COLLECTOR_PASSWORD 未在环境变量中设置") 