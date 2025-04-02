#!/usr/bin/env python3
"""
论文收集器主入口点
可以作为API服务器启动，或者运行一次性的论文收集任务
"""

import os
import sys
import argparse

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src import __version__

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='论文收集器')
    parser.add_argument('--version', action='version', version=f'论文收集器 v{__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 运行服务器的子命令
    server_parser = subparsers.add_parser('server', help='启动API服务器')
    server_parser.add_argument('--host', help='监听地址 (默认: 0.0.0.0)')
    server_parser.add_argument('--port', type=int, help='监听端口 (默认: 5000)')
    
    # 收集论文的子命令
    collect_parser = subparsers.add_parser('collect', help='执行一次性论文收集')
    collect_parser.add_argument('--no-email', action='store_true', help='不发送邮件报告')
    
    # 测试邮件的子命令
    email_parser = subparsers.add_parser('test-email', help='测试邮件发送功能')
    email_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 根据命令执行相应操作
    if args.command == 'server':
        from src.api.server import run_server
        # 导入配置以覆盖默认值
        if args.host or args.port:
            from src.config import settings
            if args.host:
                settings.API_HOST = args.host
            if args.port:
                settings.API_PORT = args.port
        run_server()
    
    elif args.command == 'collect':
        from src.core.paper_collector import collect_papers
        total_count, new_count, email_success, email_message= collect_papers()
        print(f"收集完成: 共{total_count}篇论文，其中{new_count}篇为新论文")
    
    elif args.command == 'test-email':
        from src.utils.email_test import test_email_connection
        test_email_connection(verbose=args.verbose)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 