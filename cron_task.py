#!/usr/bin/env python3
"""
论文收集定时任务
用于配置为cron作业，根据用户设置的时间发送论文
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置日志
LOG_FILE = os.path.join(project_root, 'logs', 'cron_task.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        logger.info("=== 开始执行定时论文收集任务 ===")
        current_time = datetime.now().strftime("%H:%M")
        logger.info(f"当前时间: {current_time}")
        
        # 创建应用上下文
        from src.app import create_app
        app = create_app()
        
        with app.app_context():
            from src.core.paper_collector import collect_papers_for_all_users
            
            # 收集指定时间的用户论文
            success_count, total_count, errors = collect_papers_for_all_users()
            
            if total_count == 0:
                logger.info(f"当前时间 {current_time} 没有需要发送邮件的用户")
            else:
                logger.info(f"为用户执行论文收集: 成功 {success_count}/{total_count} 个用户")
                
                if errors:
                    logger.error("收集过程中出现以下错误:")
                    for error in errors:
                        logger.error(f"  - {error}")
            
        logger.info("=== 论文收集任务执行完毕 ===")
    
    except Exception as e:
        logger.error(f"执行论文收集任务时出错: {e}", exc_info=True)

if __name__ == "__main__":
    main() 