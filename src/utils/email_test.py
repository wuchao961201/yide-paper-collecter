#!/usr/bin/env python3
"""
邮件发送测试工具
用于验证SMTP设置是否正确
"""

import os
import sys
import smtplib
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT

def test_email_connection(sender=None, password=None, recipient=None, server=None, port=None, verbose=False):
    """
    测试邮件连接和发送功能
    
    参数:
        sender: 发件人邮箱（如果为None则使用配置中的值）
        password: 发件人密码（如果为None则使用配置中的值）
        recipient: 收件人邮箱（如果为None则使用配置中的值）
        server: SMTP服务器（如果为None则使用配置中的值）
        port: SMTP端口（如果为None则使用配置中的值）
        verbose: 是否显示详细信息
    
    返回:
        成功返回True，失败返回False
    """
    # 使用传入的参数或配置文件中的默认值
    sender = sender or SENDER_EMAIL
    password = password or SENDER_PASSWORD
    recipient = recipient or RECIPIENT_EMAIL
    server = server or SMTP_SERVER
    port = port or SMTP_PORT
    
    # 准备邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "论文收集器邮件发送测试"
    
    body = "这是一封测试邮件，用于验证论文收集器的邮件发送功能是否正常。"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # 连接到SMTP服务器
        if verbose:
            print(f"正在连接到SMTP服务器: {server}:{port}")
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()  # 启用安全连接
        
        # 登录
        if verbose:
            print("正在尝试登录...")
        smtp.login(sender, password)
        
        # 发送邮件
        if verbose:
            print("正在发送邮件...")
        text = msg.as_string()
        smtp.sendmail(sender, recipient, text)
        
        # 关闭连接
        smtp.quit()
        
        print("✓ 邮件发送成功！")
        print(f"  从 {sender}")
        print(f"  发送到 {recipient}")
        return True
    
    except Exception as e:
        print(f"✗ 邮件发送失败: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        # 提供常见错误的解决方案
        if "Authentication" in str(e):
            print("\n可能的解决方案:")
            print("1. 检查邮箱密码是否正确")
            print("2. 对于Gmail等服务，您可能需要使用应用专用密码")
            print("3. 确认您的邮箱服务商允许SMTP访问")
        
        elif "ConnectionRefused" in str(e) or "Connection refused" in str(e):
            print("\n可能的解决方案:")
            print("1. 检查SMTP服务器地址和端口是否正确")
            print("2. 确认网络连接正常，没有防火墙阻止")
            print("3. 尝试使用不同的端口（通常为25、465或587）")
        
        return False

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='测试邮件发送功能')
    parser.add_argument('--sender', help='发件人邮箱')
    parser.add_argument('--password', help='发件人密码')
    parser.add_argument('--recipient', help='收件人邮箱')
    parser.add_argument('--server', help='SMTP服务器地址')
    parser.add_argument('--port', type=int, help='SMTP服务器端口')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    test_email_connection(
        sender=args.sender,
        password=args.password,
        recipient=args.recipient,
        server=args.server,
        port=args.port,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main() 