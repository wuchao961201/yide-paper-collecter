#!/usr/bin/env python3
# 配置文件
# 包含论文收集器的所有配置参数
# 作者: Liu Yide

import os
import logging

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

# 邮件默认配置
# 注意：不要在此处存储实际密码，请使用环境变量或conf/local_settings.py
SENDER_EMAIL = "**********"
SENDER_PASSWORD = ""  # 默认为空，实际使用时通过环境变量或本地配置覆盖
RECIPIENT_EMAIL = "**********"

# 腾讯SES SMTP配置
# 可选的地区服务器: smtp.qcloudmail.com(香港), sg-smtp.qcloudmail.com(新加坡), gz-smtp.qcloudmail.com(广州)
SMTP_SERVER = "smtp.qcloudmail.com"
SMTP_PORT = 465  # 465/587使用SSL，25使用TLS
SMTP_USE_SSL = True  # 是否使用SSL连接

# API服务器默认配置
API_HOST = "0.0.0.0"
API_PORT = 5000

# 尝试导入本地设置来覆盖默认值
try:
    import importlib.util
    local_settings_path = os.path.join(BASE_DIR, 'conf', 'local_settings.py')
    if os.path.exists(local_settings_path):
        spec = importlib.util.spec_from_file_location("local_settings", local_settings_path)
        local_settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_settings)
        
        # 从local_settings中获取所有大写变量
        for setting in dir(local_settings):
            if setting.isupper():
                locals()[setting] = getattr(local_settings, setting)
        
        logger.info("已加载本地设置")
    else:
        logger.warning("未找到本地设置文件，使用默认配置")
except ImportError as e:
    logger.error(f"导入本地设置时出错: {e}")
    logger.warning("使用默认配置")
except Exception as e:
    logger.error(f"加载本地设置时出错: {e}")
    logger.warning("使用默认配置")

# 尝试从环境变量中读取敏感信息
SENDER_PASSWORD = os.environ.get('PAPER_COLLECTOR_PASSWORD', SENDER_PASSWORD) 