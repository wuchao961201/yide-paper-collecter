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

# 添加src目录到Python路径
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# 导入配置模块
from config import settings

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
            if is_relevant_paper(title, summary, settings.KEYWORDS):
                all_papers.append((title, summary, link))
    except requests.exceptions.RequestException as e:
        logger.error(f"从arXiv获取关键词'{keyword}'的论文时出错: {e}")
    
    return all_papers

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

def save_reading_list(papers, output_folder, date_str):
    """
    将阅读列表保存到指定文件夹中的文本文件
    只保存每篇论文的链接
    """
    file_name = os.path.join(output_folder, f'reading_list_{date_str}.txt')
    tick = 1
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            for paper in papers:
                title, summary, link = paper
                f.write(f"[{tick}] {title} \n{link}\n\n")
                tick += 1
        logger.info(f'阅读列表已保存到 {file_name}')
        return file_name
    except Exception as e:
        logger.error(f"保存阅读列表时出错: {e}")
        return None

def read_previous_list(date_str, output_folder):
    """
    读取前一天的阅读列表并返回URL集合
    """
    previous_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    previous_file_name = os.path.join(output_folder, f'reading_list_{previous_date}.txt')

    # 检查前一天的文件是否存在
    if os.path.exists(previous_file_name):
        try:
            with open(previous_file_name, 'r', encoding='utf-8') as f:
                previous_papers = f.readlines()

            # 从前一天的文件中提取URL
            previous_urls = {line.split()[-1] for line in previous_papers if line.strip()}
            return previous_urls
        except Exception as e:
            logger.error(f"读取前一天的阅读列表时出错: {e}")
            return set()
    else:
        logger.info(f"未找到{previous_date}的阅读列表")
        return set()

def generate_new_papers_list(all_papers, previous_urls):
    """
    生成不在前一天阅读列表中的新论文列表
    """
    new_papers = [paper for paper in all_papers if paper[2] not in previous_urls]
    return new_papers

def save_new_papers_list(new_papers, output_folder):
    """
    将新论文列表保存到文本文件
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_name = os.path.join(output_folder, 'reading_list_new.txt')
    
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            tick = 1
            for paper in new_papers:
                title, summary, link = paper
                f.write(f"[{tick}] {title} \n{link}\n\n")
                tick += 1
        logger.info(f'新论文列表已保存到 {file_name}')
    except Exception as e:
        logger.error(f"保存新论文列表时出错: {e}")

def send_email(report_subject, new_papers, all_papers):
    """
    发送包含新论文和所有论文的邮件报告
    """
    # 第一部分：新项目
    if new_papers:
        new_items_section = "新项目:\n\n"
        new_items_section += "\n\n".join([f"{tick}. {paper[0]} \n{paper[2]}" for tick, paper in enumerate(new_papers, 1)])
    else:
        new_items_section = "新项目: 没有新内容。"

    # 第二部分：原始获取结果
    original_results_section = "\n\n\n\n原始获取结果:\n"
    original_results_section += "\n\n".join([f"{tick}. {paper[0]} \n{paper[2]}" for tick, paper in enumerate(all_papers, 1)])

    # 组合完整的报告正文
    report_body = new_items_section + original_results_section

    # 准备邮件
    msg = MIMEMultipart()
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = settings.RECIPIENT_EMAIL
    msg['Subject'] = report_subject

    msg.attach(MIMEText(report_body, 'plain'))

    # 发送邮件
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # 安全连接
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(settings.SENDER_EMAIL, settings.RECIPIENT_EMAIL, text)
        logger.info("邮件发送成功")
    except Exception as e:
        logger.error(f"发送邮件时出错: {e}")

def collect_papers():
    """收集论文的主函数"""
    logger.info("在Docker环境中开始论文收集过程")
    all_relevant_papers = []

    # 使用ThreadPoolExecutor并行获取源
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 并行获取RSS论文
        futures = [executor.submit(parse_rss_feed, url, settings.KEYWORDS) for url in settings.RSS_FEEDS]
        for future in concurrent.futures.as_completed(futures):
            relevant_papers = future.result()
            all_relevant_papers.extend(relevant_papers)
        
        # 并行获取arXiv论文
        arxiv_futures = [executor.submit(fetch_arxiv_papers, keyword) for keyword in settings.KEYWORDS]
        for future in concurrent.futures.as_completed(arxiv_futures):
            arxiv_papers = future.result()
            all_relevant_papers.extend(arxiv_papers)

    # 读取前一天的阅读列表
    output_folder = os.path.join(src_dir, '..', 'data', 'collected-articles')
    os.makedirs(output_folder, exist_ok=True)
    
    previous_urls = read_previous_list(datetime.now().strftime("%Y-%m-%d"), output_folder)

    # 筛选出新论文
    new_papers = generate_new_papers_list(all_relevant_papers, previous_urls)

    # 保存新论文列表
    save_new_papers_list(new_papers, output_folder)

    # 保存今天的阅读列表
    today_str = datetime.now().strftime("%Y-%m-%d")
    save_reading_list(all_relevant_papers, output_folder, today_str)

    # 生成邮件报告
    report_subject = f"[论文获取报告 - Yide Liu] [{today_str}]"
    send_email(report_subject, new_papers, all_relevant_papers)
    
    logger.info("论文收集过程完成")
    return len(all_relevant_papers), len(new_papers)

if __name__ == "__main__":
    total_papers, new_papers = collect_papers()
    print(f"收集完成: 共{total_papers}篇论文，其中{new_papers}篇为新论文") 