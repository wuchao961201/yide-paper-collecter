#!/usr/bin/env python3
"""
论文收集器主入口点
可以作为API服务器启动，或者运行一次性的论文收集任务
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src import __version__

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='论文收集器')
    parser.add_argument('--version', action='version', version=f'论文收集器 v{__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 运行Web应用的子命令
    web_parser = subparsers.add_parser('web', help='启动Web应用')
    web_parser.add_argument('--host', help='监听地址 (默认: 0.0.0.0)')
    web_parser.add_argument('--port', type=int, help='监听端口 (默认: 5000)')
    web_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    # 添加收集论文子命令
    collect_parser = subparsers.add_parser('collect', help='收集论文')
    collect_parser.add_argument('--user-id', type=int, help='为指定用户ID收集论文')
    collect_parser.add_argument('--all-users', action='store_true', help='为所有用户收集论文')
    
    # 数据库初始化子命令
    db_parser = subparsers.add_parser('init-db', help='初始化数据库')
    db_parser.add_argument('--force', action='store_true', help='强制重新创建所有表')
    
    args = parser.parse_args()
    
    # 根据命令执行相应操作
    if args.command == 'web':
        from src.app import create_app
        
        # 创建应用实例
        app = create_app()
        
        # 处理命令行选项
        host = args.host or app.config.get('API_HOST', '0.0.0.0')
        port = args.port or app.config.get('API_PORT', 5000)
        debug = args.debug
        
        # 启动应用
        app.run(host=host, port=port, debug=debug)
    
    elif args.command == 'collect':
        # 创建应用上下文
        from src.app import create_app
        app = create_app()
        
        with app.app_context():
            if args.all_users:
                from src.core.paper_collector import collect_papers_for_all_users
                success_count, total_count, errors = collect_papers_for_all_users()
                
                print(f"为用户执行论文收集：成功 {success_count}/{total_count} 个用户")
                if errors:
                    print("错误信息:")
                    for error in errors:
                        print(f"  - {error}")
            
            elif args.user_id:
                from src.models import User
                from src.core.paper_collector import collect_papers_for_user
                
                user = User.query.get(args.user_id)
                if not user:
                    print(f"错误：找不到ID为 {args.user_id} 的用户")
                    return
                
                success, total, new, message = collect_papers_for_user(user)
                if success:
                    print(f"为用户 {user.email} 收集成功: 共 {total} 篇论文，其中 {new} 篇为新论文")
                else:
                    print(f"为用户 {user.email} 收集失败: {message}")
            else:
                print("错误：需要指定用户ID或为所有用户收集论文")
    elif args.command == 'init-db':
        # 初始化数据库
        from src.app import create_app
        app = create_app()
        
        with app.app_context():
            from src.models import db
            
            if args.force:
                print("警告：即将删除并重新创建所有数据库表...")
                confirm = input("确定要继续吗？这将删除所有数据！(y/n): ").lower()
                if confirm != 'y':
                    print("操作已取消")
                    return
                
                # 删除所有表并重新创建
                db.drop_all()
                print("所有表已删除")
            
            # 创建表
            db.create_all()
            print("数据库初始化完成")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 