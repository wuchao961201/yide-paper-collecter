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
        
        total, new = collect_papers()
        
        logger.info(f"论文收集脚本执行成功：共收集 {total} 篇论文，其中 {new} 篇为新论文")
        return jsonify({
            "status": "success",
            "message": "论文收集脚本执行成功",
            "data": {
                "total_papers": total,
                "new_papers": new
            }
        })
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
            {"path": "/trigger", "method": "GET", "description": "触发论文收集"},
            {"path": "/health", "method": "GET", "description": "健康检查"}
        ]
    })

def run_server():
    """启动API服务器"""
    logger.info(f"启动API服务器于 {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT)

if __name__ == '__main__':
    run_server() 