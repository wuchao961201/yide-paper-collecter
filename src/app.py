#!/usr/bin/env python3
"""
论文收集器应用
使用Flask创建Web应用
"""

import os
from flask import Flask
from flask_login import LoginManager
from datetime import datetime

from .models import db, User
from .routes import auth_bp, user_bp, main_bp

def create_app(test_config=None):
    """创建并配置Flask应用"""
    # 创建应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object('src.config.settings')
    
    # 如果提供了测试配置，则使用测试配置
    if test_config:
        app.config.update(test_config)
    
    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # 初始化扩展
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录后再访问此页面。'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        """加载用户"""
        return User.query.get(int(user_id))
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # 在请求处理前记录最后访问时间
    @app.before_request
    def before_request():
        from flask_login import current_user
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
    
    # 使用APP上下文初始化数据库
    with app.app_context():
        db.create_all()
    
    return app 