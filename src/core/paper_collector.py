#!/usr/bin/env python3
# 论文收集器核心模块
# 该模块负责从多个来源收集论文，筛选相关内容，并发送邮件报告
# 作者: Liu Yide
# 版本: 2.0

import os
import feedparser
import requests
from datetime import datetime, timedelta
import concurrent.futures
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import importlib.util
import sys
import ssl
from email.header import Header
from email.utils import formataddr

# 添加src目录到Python路径
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# 导入配置模块
from src.config import settings

# 设置日志
def setup_logging():
    """设置日志配置"""
    log_dir = os.path.join(src_dir, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        filename=os.path.join(log_dir, 'paper_collector.log'),
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def is_relevant_paper(title, summary, keywords):
    """
    检查论文是否与关键词相关
    如果匹配则返回True，否则返回False
    """
    text = title.lower() + ' ' + (summary or "").lower()
    return any(keyword.lower() in text for keyword in keywords)

def fetch_arxiv_papers(keyword):
    """
    根据关键词从arXiv获取论文
    限制为最近90天内的提交
    """
    all_papers = []
    # 计算90天前的日期（arXiv格式：YYYY-MM-DD）
    one_month_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    params = {
        'search_query': f'all:{keyword}',  # 在所有字段中搜索关键词
        'start': 0,  # 搜索结果的起始索引
        'max_results': 5,  # 每个关键词限制为5个结果（可根据需要调整）
        'sortBy': 'submittedDate',  # 按提交日期排序
        'sortOrder': 'descending'  # 显示最新论文
    }
    query_url = f"{settings.ARXIV_API_URL}?search_query=all:{keyword}+AND+submittedDate:[{one_month_ago}0000+TO+*]"

    try:
        response = requests.get(query_url, params=params)
        response.raise_for_status()  # 检查请求是否成功

        # 解析XML响应
        feed = response.text
        entries = feedparser.parse(feed).entries
        for entry in entries:
            title = entry.title
            summary = entry.summary
            link = entry.link
            all_papers.append((title, summary, link))
    except requests.exceptions.RequestException as e:
        logger.error(f"从arXiv获取关键词'{keyword}'的论文时出错: {e}")
    
    return all_papers

def fetch_techrxiv_papers(keywords):
    """
    从TechRxiv获取论文
    使用TechRxiv的RSS feed
    """
    try:
        feed = feedparser.parse(settings.TECHRXIV_API_URL)
        relevant_papers = []

        for entry in feed.entries:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            summary = entry.get('summary', '')

            if is_relevant_paper(title, summary, keywords):
                relevant_papers.append((title, summary, link))

        return relevant_papers
    except Exception as e:
        logger.error(f"从TechRxiv获取论文时出错: {e}")
        return []

def parse_rss_feed(feed_url, keywords):
    """
    解析RSS源，根据关键词筛选论文，并返回相关论文列表
    添加网络或解析问题的错误处理
    """
    try:
        feed = feedparser.parse(feed_url)
        relevant_papers = []

        for entry in feed.entries:
            title = entry.get('title', 'No Title')  # 安全获取标题
            link = entry.link
            summary = entry.get('summary', '')

            if is_relevant_paper(title, summary, keywords):
                relevant_papers.append((title, summary, link))

        return relevant_papers
    except Exception as e:
        logger.error(f"解析RSS源 {feed_url} 时出错: {e}")
        return []

def collect_papers_for_user(user):
    """
    为特定用户收集论文并发送邮件
    
    参数:
        user: 用户对象，包含用户的RSS订阅和关键词信息
    
    返回:
        tuple: (成功标志, 总论文数, 新论文数, 消息)
    """
    import logging
    from ..models import RssFeed, Keyword, SentPaper, db
    
    logger = logging.getLogger(__name__)
    
    try:
        # 获取用户的RSS订阅源
        rss_feeds = [feed.url for feed in RssFeed.query.filter_by(user_id=user.id).all()]
        
        if not rss_feeds:
            return False, 0, 0, "用户未添加任何RSS源"
        
        # 获取用户的关键词
        keywords = [kw.text for kw in Keyword.query.filter_by(user_id=user.id).all()]
        
        if not keywords:
            return False, 0, 0, "用户未添加任何关键词"
        
        # 获取用户已经发送过的论文URL列表
        sent_paper_urls = {paper.paper_url for paper in SentPaper.query.filter_by(user_id=user.id).all()}
        
        # 收集论文
        all_papers = []
        
        # 1. 从RSS源收集
        for feed_url in rss_feeds:
            try:
                papers = parse_rss_feed(feed_url, keywords)
                all_papers.extend(papers)
            except Exception as e:
                logger.error(f"为用户 {user.email} 解析RSS源 {feed_url} 时出错: {e}")
        
        # 2. 对于每个关键词，从arXiv收集
        for keyword in keywords:
            try:
                papers = fetch_arxiv_papers(keyword)
                all_papers.extend(papers)
            except Exception as e:
                logger.error(f"为用户 {user.email} 从arXiv获取关键词 '{keyword}' 的论文时出错: {e}")
        
        # 3. 从TechRxiv收集
        try:
            papers = fetch_techrxiv_papers(keywords)
            all_papers.extend(papers)
        except Exception as e:
                logger.error(f"为用户 {user.email} 从TechRxiv获取论文时出错: {e}")
        
        # 过滤掉已经发送过的论文
        new_papers = []
        for paper in all_papers:
            title, summary, url = paper
            if url not in sent_paper_urls:
                new_papers.append(paper)
                # 记录新论文到已发送列表
                sent_paper = SentPaper(
                    user_id=user.id,
                    paper_url=url,
                    title=title,
                    sent_at=datetime.utcnow()
                )
                db.session.add(sent_paper)
        
        # 提交数据库更改
        db.session.commit()
        
        # 如果有新论文，发送邮件
        if new_papers:
            # 检查是否有足够的信息发送邮件
            if not user.email:
                return True, len(all_papers), len(new_papers), "用户邮箱为空，无法发送邮件"
            
            # 准备邮件内容
            today_str = datetime.now().strftime("%Y-%m-%d")
            subject = f"[论文订阅] {today_str} - 发现 {len(new_papers)} 篇新论文"
            
            # 发送邮件
            email_success, email_message = send_email_to_user(user, subject, new_papers, all_papers)
            
            if email_success:
                return True, len(all_papers), len(new_papers), "邮件发送成功"
            else:
                return False, len(all_papers), len(new_papers), f"邮件发送失败: {email_message}"
        else:
            return True, len(all_papers), 0, "没有新论文"
        
    except Exception as e:
        logger.error(f"为用户 {user.email} 收集论文时出错: {e}")
        return False, 0, 0, str(e)

def send_email_to_user(user, subject, new_papers, all_papers=None):
    """
    向特定用户发送论文邮件
    
    参数:
        user: 用户对象
        subject: 邮件主题
        new_papers: 新论文列表
        all_papers: 所有论文列表，可选
    
    返回:
        tuple: (成功标志, 消息)
    """
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    import ssl
    from email.header import Header
    from email.utils import formataddr
    import logging
    
    from src.config import settings
    
    logger = logging.getLogger(__name__)
    
    try:
        # 创建邮件消息
        msg = MIMEMultipart()
        
        # 添加发件人和收件人
        msg['From'] = formataddr((str(Header('论文收集器', 'utf-8')), settings.SENDER_EMAIL))
        msg['To'] = user.email
        msg['Subject'] = subject
        
        # 生成邮件正文 - 优化样式，更加简洁现代
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px;
                }}
                h1 {{ 
                    color: #333; 
                    font-size: 24px; 
                    margin-bottom: 20px; 
                    border-bottom: 1px solid #eee; 
                    padding-bottom: 10px; 
                }}
                h2 {{ 
                    color: #444; 
                    font-size: 20px; 
                    margin-top: 25px; 
                    margin-bottom: 15px; 
                }}
                .paper {{ 
                    margin-bottom: 25px; 
                    padding-bottom: 15px; 
                    border-bottom: 1px solid #f1f1f1; 
                }}
                .paper h3 {{ 
                    margin-bottom: 10px; 
                    color: #1a73e8; 
                    font-size: 18px; 
                }}
                .summary {{ 
                    color: #555; 
                    margin-bottom: 10px; 
                    font-size: 15px;
                    line-height: 1.5;
                }}
                .link {{ 
                    display: inline-block;
                    color: #1a73e8; 
                    text-decoration: none; 
                    font-weight: 500;
                    padding: 4px 0;
                }}
                .footer {{ 
                    margin-top: 30px; 
                    padding-top: 15px;
                    border-top: 1px solid #eee; 
                    color: #777; 
                    font-size: 14px; 
                }}
                .count-badge {{
                    display: inline-block;
                    background: #f1f8ff;
                    border: 1px solid #dbedff;
                    color: #1a73e8;
                    border-radius: 12px;
                    padding: 2px 8px;
                    font-size: 14px;
                    margin-left: 8px;
                    font-weight: normal;
                }}
            </style>
        </head>
        <body>
            <h1>论文订阅</h1>
            <p>尊敬的 {user.username}，</p>
            <p>以下是根据您的关键词筛选出的论文：</p>
        """
        
        if new_papers:
            html_body += f"""
            <h2>发现的论文 <span class="count-badge">{len(new_papers)}</span></h2>
            """
            
            for i, paper in enumerate(new_papers, 1):
                title, summary, link = paper
                html_body += f"""
                <div class="paper">
                    <h3>{title}</h3>
                    <div class="summary">{summary[:250]}{'...' if len(summary) > 250 else ''}</div>
                    <a class="link" href="{link}">阅读详情 →</a>
                </div>
                """
        else:
            html_body += """
            <p>没有发现新论文。</p>
            """
        
        html_body += f"""
            <div class="footer">
                <p>此邮件由论文收集器自动发送，请勿回复。</p>
            </div>
        </body>
        </html>
        """
        
        # 添加HTML内容
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # 连接到SMTP服务器并发送邮件
        if settings.SMTP_USE_SSL:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, context=context) as server:
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"成功向用户 {user.email} 发送邮件")
        return True, "邮件发送成功"
    
    except Exception as e:
        logger.error(f"向用户 {user.email} 发送邮件时出错: {e}")
        return False, str(e)

def collect_papers_for_all_users():
    """
    为所有活跃用户收集论文
    
    返回:
        tuple: (成功用户数, 总用户数, 错误信息列表)
    """
    import logging
    from datetime import datetime
    from ..models import User
    
    logger = logging.getLogger(__name__)
    
    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    # 查找当前时间应该接收邮件的活跃用户
    users = User.query.filter_by(is_active=True).filter_by(send_time=current_time).all()
    
    if not users:
        logger.info(f"当前时间 {current_time} 没有需要发送邮件的用户")
        return 0, 0, []
    
    success_count = 0
    errors = []
    
    # 为每个用户收集论文
    for user in users:
        try:
            success, total, new, message = collect_papers_for_user(user)
            
            if success:
                success_count += 1
                logger.info(f"为用户 {user.email} 成功收集论文: 共 {total} 篇，其中 {new} 篇为新论文")
            else:
                errors.append(f"用户 {user.email}: {message}")
                logger.error(f"为用户 {user.email} 收集论文失败: {message}")
        
        except Exception as e:
            errors.append(f"用户 {user.email}: {str(e)}")
            logger.error(f"为用户 {user.email} 收集论文时出错: {e}")
    
    return success_count, len(users), errors

if __name__ == "__main__":
    # 直接运行此模块时的测试代码
    print("论文收集模块测试")
    print("请通过run.py的命令行接口来运行论文收集功能")
