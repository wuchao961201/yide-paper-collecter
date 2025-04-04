#!/usr/bin/env python3
"""
认证相关路由
包含登录、注册和登出功能
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from ..models import db, User
from ..forms import LoginForm, RegistrationForm

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    # 如果用户已经登录，重定向到仪表盘
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember_me.data
        
        # 查找用户
        user = User.query.filter_by(email=email).first()
        
        # 验证密码
        if user and user.check_password(password):
            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # 登录用户
            login_user(user, remember=remember)
            flash('登录成功！', 'success')
            
            # 如果请求中有next参数，则重定向到该页面
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('user.dashboard'))
        else:
            flash('邮箱或密码错误，请重试。', 'danger')
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    return render_template('auth/login.html', form=form, now=now)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    # 如果用户已经登录，重定向到仪表盘
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # 创建新用户
        user = User(
            email=form.email.data,
            username=form.username.data,
            created_at=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        # 保存到数据库
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('auth.login'))
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    return render_template('auth/register.html', form=form, now=now)

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('main.index')) 