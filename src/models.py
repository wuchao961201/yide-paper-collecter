#!/usr/bin/env python3
"""
数据库模型定义
包含用户和订阅信息的模型
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """用户模型，用于存储用户信息和身份验证"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # 发送邮件的时间，格式为"HH:MM"
    send_time = db.Column(db.String(5), default="08:00")
    # 用户是否激活
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联到该用户的订阅
    rss_feeds = db.relationship('RssFeed', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    keywords = db.relationship('Keyword', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码散列"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码散列"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class RssFeed(db.Model):
    """RSS订阅源模型"""
    __tablename__ = 'rss_feeds'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(128))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<RssFeed {self.url}>'


class Keyword(db.Model):
    """关键词模型"""
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Keyword {self.text}>'


class SentPaper(db.Model):
    """已发送的论文模型，用于避免重复发送"""
    __tablename__ = 'sent_papers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paper_url = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(256))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 创建联合唯一约束，确保同一篇论文不会发送给同一用户两次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'paper_url', name='user_paper_uc'),
    )
    
    user = db.relationship('User', backref=db.backref('sent_papers', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SentPaper {self.title}>' 