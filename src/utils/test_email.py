#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 测试邮件发送功能
# 该脚本用于测试腾讯SES邮件发送是否正常工作
# 作者: Liu Yide

import os
import sys
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import logging

# 设置路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 然后再导入配置
from src.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_email_connection(verbose=False):
    """测试邮件连接是否正常"""
    
    # 获取SMTP配置
    smtp_host = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    use_ssl = getattr(settings, 'SMTP_USE_SSL', smtp_port in [465, 587])
    
    logger.info(f"测试连接到 {smtp_host}:{smtp_port}，使用SSL: {use_ssl}")
    if verbose:
        print(f"测试连接到 {smtp_host}:{smtp_port}，使用SSL: {use_ssl}")
    
    try:
        if use_ssl:
            # 创建SSL上下文，使用默认密码套件
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT')
            # 如果需要禁用TLSv1.3（服务端不支持时）
            # context.options |= ssl.OP_NO_TLSv1_3
            
            # 使用SSL连接
            logger.info("使用SSL连接")
            logger.info(context)
            logger.info(smtp_host)
            logger.info(smtp_port)
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
        else:
            # 使用普通连接
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()  # 使用TLS加密
        
        logger.info("成功连接到SMTP服务器")
        if verbose:
            print("成功连接到SMTP服务器")
        
        # 尝试登录
        logger.info(f"登录用户: {settings.SENDER_EMAIL}")
        logger.info(f"登录密码: {settings.SENDER_PASSWORD}")
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        logger.info("登录成功!")
        if verbose:
            print("登录成功!")
        
        server.quit()
        return True, "连接和登录测试通过"
    except smtplib.SMTPConnectError as e:
        error_msg = f"连接SMTP服务器失败: {e.smtp_code} {e.smtp_error}"
        logger.error(error_msg)
        if verbose:
            print(error_msg)
        return False, error_msg
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP认证失败: {e.smtp_code} {e.smtp_error}"
        logger.error(error_msg)
        if verbose:
            print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"连接测试失败: {str(e)}"
        logger.error(error_msg)
        if verbose:
            print(error_msg)
        return False, error_msg

def send_test_email():
    """发送测试邮件"""
    
    # 准备邮件
    message = MIMEMultipart('alternative')
    
    # 设置发件人别名
    sender_alias = getattr(settings, 'SENDER_ALIAS', "论文收集器")
    message['From'] = formataddr([sender_alias, settings.SENDER_EMAIL])
    
    # 处理收件人
    recipients = settings.RECIPIENT_EMAIL
    if isinstance(recipients, str):
        recipients = [recipients]
    message['To'] = ', '.join(recipients)
    
    # 设置邮件主题
    subject = "测试邮件 - 腾讯SES服务"
    message['Subject'] = Header(subject, 'UTF-8')
    
    # HTML邮件内容
    html_body = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>测试邮件</title>
</head>
<body>
<h1>测试邮件</h1>
<p>这是一封测试邮件。</p>
<p>如果您收到这封邮件，说明腾讯SES服务配置正确，可以正常发送邮件。</p>
<hr/>
<p><em>论文收集器</em></p>
</body>
</html>"""
    
    # 添加HTML内容
    mime_text = MIMEText(html_body, _subtype='html', _charset='UTF-8')
    message.attach(mime_text)
    
    # 添加纯文本内容作为备用
    plain_text = """
这是一封测试邮件。

如果您收到这封邮件，说明腾讯SES服务配置正确，可以正常发送邮件。

---
论文收集器
"""
    plain_part = MIMEText(plain_text, _subtype='plain', _charset='UTF-8')
    message.attach(plain_part)
    
    # 腾讯SES SMTP配置
    smtp_host = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    use_ssl = getattr(settings, 'SMTP_USE_SSL', smtp_port in [465, 587])
    
    # 发送邮件
    try:
        if use_ssl:
            # 创建SSL上下文，使用默认密码套件
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT')
            # 如果需要禁用TLSv1.3（服务端不支持时）
            # context.options |= ssl.OP_NO_TLSv1_3
            
            # 使用SSL连接
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
        else:
            # 使用普通连接
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()  # 使用TLS加密
        
        # 登录和发送
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, recipients, message.as_string())
        server.quit()
        
        logger.info(f"测试邮件已成功发送给 {', '.join(recipients)}")
        return True, "测试邮件发送成功"
    except smtplib.SMTPConnectError as e:
        error_msg = f"连接SMTP服务器失败: {e.smtp_code} {e.smtp_error}"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP认证失败: {e.smtp_code} {e.smtp_error}"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPSenderRefused as e:
        error_msg = f"发送方地址被拒绝: {e.smtp_code} {e.smtp_error}"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f"接收方地址被拒绝: {e.recipients}"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPDataError as e:
        error_msg = f"SMTP数据错误: {e.smtp_code} {e.smtp_error}"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP通用错误: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"发送测试邮件失败: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

if __name__ == "__main__":
    # 首先测试连接
    connection_result, connection_msg = test_email_connection(verbose=True)
    print(f"连接测试结果: {'成功' if connection_result else '失败'} - {connection_msg}")
    
    if connection_result:
        # 连接成功后测试发送
        email_result, email_msg = send_test_email()
        print(f"邮件发送测试结果: {'成功' if email_result else '失败'} - {email_msg}")
    else:
        print("由于连接测试失败，跳过邮件发送测试") 