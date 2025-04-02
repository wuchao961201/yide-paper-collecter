#!/usr/bin/env python3
"""
API服务器模块
用于接收触发请求并执行论文收集任务
"""

import os
import sys
import logging
import subprocess
from flask import Flask, jsonify

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.config import API_HOST, API_PORT, LOGS_DIR

# 初始化Flask应用
app = Flask(__name__)
app.json.ensure_ascii = False # 解决中文乱码问题

# 设置日志
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'api_server.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/trigger', methods=['GET'])
def trigger_collection():
    """触发论文收集脚本执行"""
    logger.info("收到触发请求，开始执行论文收集脚本")
    
    try:
        # 导入核心模块并执行论文收集
        from src.core.paper_collector import collect_papers
        
        total, new, email_success, email_message = collect_papers()
        
        # 构建响应
        response = {
            "status": "success",
            "message": "论文收集脚本执行成功",
            "data": {
                "total_papers": total,
                "new_papers": new,
                "email": {
                    "success": email_success,
                    "message": email_message
                }
            }
        }
        
        # 记录结果
        if email_success:
            logger.info(f"论文收集脚本执行成功：共收集 {total} 篇论文，其中 {new} 篇为新论文，邮件已成功发送")
        else:
            logger.warning(f"论文收集脚本执行成功：共收集 {total} 篇论文，其中 {new} 篇为新论文，但邮件发送失败: {email_message}")
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"论文收集脚本执行失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "论文收集脚本执行失败",
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "ok"})

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return jsonify({
        "name": "论文收集器API",
        "version": "2.0",
        "author": "Liu Yide",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "首页"},
            {"path": "/trigger", "method": "GET", "description": "触发论文收集和邮件发送"},
            {"path": "/send-email", "method": "GET", "description": "仅发送邮件（使用最新收集的数据）"},
            {"path": "/health", "method": "GET", "description": "健康检查"}
        ]
    })

@app.route('/send-email', methods=['GET'])
def send_email_only():
    """单独触发邮件发送（使用已收集的最新数据）"""
    logger.info("收到邮件发送请求")
    
    try:
        # 导入核心模块
        from src.core.paper_collector import collect_papers_without_email, send_email
        import os
        from datetime import datetime
        
        # 收集论文但不发送邮件
        all_papers, new_papers, total, new = collect_papers_without_email()
        
        # 生成邮件报告
        today_str = datetime.now().strftime("%Y-%m-%d")
        report_subject = f"[论文获取报告 - Yide Liu] [{today_str}]"
        
        # 发送邮件
        email_success, email_message = send_email(report_subject, new_papers, all_papers)
        
        # 构建响应
        response = {
            "status": "success",
            "message": "邮件处理完成",
            "data": {
                "email": {
                    "success": email_success,
                    "message": email_message
                },
                "papers": {
                    "total": total,
                    "new": new
                }
            }
        }
        
        # 记录结果
        if email_success:
            logger.info(f"邮件发送成功：包含 {total} 篇论文，其中 {new} 篇为新论文")
        else:
            logger.warning(f"邮件发送失败: {email_message}")
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "邮件发送失败",
            "error": str(e)
        }), 500

def run_server():
    """启动API服务器"""
    logger.info(f"启动API服务器于 {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT)

if __name__ == '__main__':
    run_server() 