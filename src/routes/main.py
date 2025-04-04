#!/usr/bin/env python3
"""
主页路由
负责网站首页和其他公共页面
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """网站首页"""
    # 传递当前年份用于页脚版权信息
    now = datetime.now()
    return render_template('index.html', now=now)

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

@main_bp.context_processor
def inject_now():
    """将当前时间注入所有模板"""
    return {'now': datetime.now()} 