#!/usr/bin/env python3
"""
表单定义
包含用户注册、登录和订阅管理的表单
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, TimeField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional
from .models import User

class LoginForm(FlaskForm):
    """用户登录表单"""
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    """用户注册表单"""
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=64)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')
    
    def validate_email(self, field):
        """验证邮箱是否已被注册"""
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱。')

class AddRssFeedForm(FlaskForm):
    """添加RSS订阅源表单"""
    url = StringField('RSS源URL', validators=[DataRequired(), URL()])
    name = StringField('名称', validators=[Optional(), Length(max=128)])
    submit = SubmitField('添加')

class AddKeywordForm(FlaskForm):
    """添加关键词表单"""
    text = StringField('关键词', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('添加')

class UserSettingsForm(FlaskForm):
    """用户设置表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=64)])
    send_time = StringField('每日邮件发送时间 (格式: HH:MM)', validators=[DataRequired()], 
                           render_kw={"placeholder": "08:00"})
    submit = SubmitField('保存设置')

class PasswordChangeForm(FlaskForm):
    """修改密码表单"""
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('修改密码')

class BatchKeywordsForm(FlaskForm):
    """批量添加关键词表单"""
    keywords = TextAreaField('关键词列表 (每行一个)', validators=[DataRequired()])
    submit = SubmitField('批量添加')

class BatchRssFeedsForm(FlaskForm):
    """批量添加RSS源表单"""
    feeds = TextAreaField('RSS源列表 (每行一个URL)', validators=[DataRequired()])
    submit = SubmitField('批量添加') 