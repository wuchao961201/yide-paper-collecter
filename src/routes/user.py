#!/usr/bin/env python3
"""
用户相关路由
包含用户仪表盘、设置和订阅管理功能
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from ..models import db, User, RssFeed, Keyword, SentPaper
from ..forms import (
    AddRssFeedForm, AddKeywordForm, 
    BatchRssFeedsForm, BatchKeywordsForm,
    UserSettingsForm, PasswordChangeForm
)
from ..core.paper_collector import collect_papers_for_user, collect_papers_for_all_users

# 创建蓝图
user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘"""
    # 获取用户的RSS源数量
    rss_count = RssFeed.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的关键词数量
    keyword_count = Keyword.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的已发送论文数量
    papers_count = SentPaper.query.filter_by(user_id=current_user.id).count()
    
    # 获取最近的5篇已发送论文
    recent_papers = SentPaper.query.filter_by(user_id=current_user.id)\
        .order_by(SentPaper.sent_at.desc())\
        .limit(5).all()
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    
    return render_template('user/dashboard.html', 
                          rss_count=rss_count, 
                          keyword_count=keyword_count, 
                          papers_count=papers_count,
                          recent_papers=recent_papers,
                          now=now)

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """用户设置"""
    # 个人信息表单
    form = UserSettingsForm(obj=current_user)
    
    # 密码修改表单
    password_form = PasswordChangeForm()
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    
    return render_template('user/settings.html', 
                          form=form, 
                          password_form=password_form,
                          now=now)

@user_bp.route('/update-settings', methods=['POST'])
@login_required
def update_settings():
    """更新用户设置"""
    form = UserSettingsForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.send_time = form.send_time.data
        db.session.commit()
        flash('设置已更新！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'设置更新失败: {error}', 'danger')
    
    return redirect(url_for('user.settings'))

@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    password_form = PasswordChangeForm()
    
    if password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('密码已修改！', 'success')
        else:
            flash('当前密码不正确，请重试。', 'danger')
    else:
        for field, errors in password_form.errors.items():
            for error in errors:
                flash(f'密码修改失败: {error}', 'danger')
    
    return redirect(url_for('user.settings'))

@user_bp.route('/rss-feeds', methods=['GET', 'POST'])
@login_required
def rss_feeds():
    """RSS源管理"""
    # 添加表单
    form = AddRssFeedForm()
    
    # 批量添加表单
    batch_form = BatchRssFeedsForm()
    
    # 获取用户的所有RSS源
    rss_feeds = RssFeed.query.filter_by(user_id=current_user.id).all()
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    
    return render_template('user/rss_feeds.html', 
                          form=form, 
                          batch_form=batch_form, 
                          rss_feeds=rss_feeds,
                          now=now)

@user_bp.route('/add-rss-feed', methods=['POST'])
@login_required
def add_rss_feed():
    """添加RSS源"""
    form = AddRssFeedForm()
    
    if form.validate_on_submit():
        # 检查是否已存在相同的RSS源
        existing = RssFeed.query.filter_by(user_id=current_user.id, url=form.url.data).first()
        if existing:
            flash('该RSS源已存在！', 'warning')
        else:
            # 创建新的RSS源
            feed = RssFeed(
                url=form.url.data,
                name=form.name.data or None,
                user_id=current_user.id
            )
            db.session.add(feed)
            db.session.commit()
            flash('RSS源添加成功！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'RSS源添加失败: {error}', 'danger')
    
    return redirect(url_for('user.rss_feeds'))

@user_bp.route('/batch-add-rss-feeds', methods=['POST'])
@login_required
def batch_add_rss_feeds():
    """批量添加RSS源"""
    batch_form = BatchRssFeedsForm()
    
    if batch_form.validate_on_submit():
        urls = [url.strip() for url in batch_form.feeds.data.split('\n') if url.strip()]
        
        if not urls:
            flash('没有有效的RSS源URL！', 'warning')
            return redirect(url_for('user.rss_feeds'))
        
        # 添加新的RSS源
        new_count = 0
        for url in urls:
            # 检查是否已存在
            existing = RssFeed.query.filter_by(user_id=current_user.id, url=url).first()
            if not existing:
                feed = RssFeed(
                    url=url,
                    user_id=current_user.id
                )
                db.session.add(feed)
                new_count += 1
        
        db.session.commit()
        
        if new_count > 0:
            flash(f'成功添加 {new_count} 个RSS源！', 'success')
        else:
            flash('所有RSS源都已存在！', 'warning')
    else:
        for field, errors in batch_form.errors.items():
            for error in errors:
                flash(f'批量添加失败: {error}', 'danger')
    
    return redirect(url_for('user.rss_feeds'))

@user_bp.route('/delete-rss-feed/<int:feed_id>', methods=['POST'])
@login_required
def delete_rss_feed(feed_id):
    """删除RSS源"""
    feed = RssFeed.query.get_or_404(feed_id)
    
    # 确保只能删除自己的RSS源
    if feed.user_id != current_user.id:
        flash('您没有权限执行此操作！', 'danger')
        return redirect(url_for('user.rss_feeds'))
    
    db.session.delete(feed)
    db.session.commit()
    
    flash('RSS源已删除！', 'success')
    return redirect(url_for('user.rss_feeds'))

@user_bp.route('/keywords', methods=['GET', 'POST'])
@login_required
def keywords():
    """关键词管理"""
    # 添加表单
    form = AddKeywordForm()
    
    # 批量添加表单
    batch_form = BatchKeywordsForm()
    
    # 获取用户的所有关键词
    keywords = Keyword.query.filter_by(user_id=current_user.id).all()
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    
    return render_template('user/keywords.html', 
                          form=form, 
                          batch_form=batch_form, 
                          keywords=keywords,
                          now=now)

@user_bp.route('/add-keyword', methods=['POST'])
@login_required
def add_keyword():
    """添加关键词"""
    form = AddKeywordForm()
    
    if form.validate_on_submit():
        # 检查是否已存在相同的关键词
        existing = Keyword.query.filter_by(user_id=current_user.id, text=form.text.data).first()
        if existing:
            flash('该关键词已存在！', 'warning')
        else:
            # 创建新的关键词
            keyword = Keyword(
                text=form.text.data,
                user_id=current_user.id
            )
            db.session.add(keyword)
            db.session.commit()
            flash('关键词添加成功！', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'关键词添加失败: {error}', 'danger')
    
    return redirect(url_for('user.keywords'))

@user_bp.route('/batch-add-keywords', methods=['POST'])
@login_required
def batch_add_keywords():
    """批量添加关键词"""
    batch_form = BatchKeywordsForm()
    
    if batch_form.validate_on_submit():
        keywords = [kw.strip() for kw in batch_form.keywords.data.split('\n') if kw.strip()]
        
        if not keywords:
            flash('没有有效的关键词！', 'warning')
            return redirect(url_for('user.keywords'))
        
        # 添加新的关键词
        new_count = 0
        for text in keywords:
            # 检查是否已存在
            existing = Keyword.query.filter_by(user_id=current_user.id, text=text).first()
            if not existing:
                keyword = Keyword(
                    text=text,
                    user_id=current_user.id
                )
                db.session.add(keyword)
                new_count += 1
        
        db.session.commit()
        
        if new_count > 0:
            flash(f'成功添加 {new_count} 个关键词！', 'success')
        else:
            flash('所有关键词都已存在！', 'warning')
    else:
        for field, errors in batch_form.errors.items():
            for error in errors:
                flash(f'批量添加失败: {error}', 'danger')
    
    return redirect(url_for('user.keywords'))

@user_bp.route('/delete-keyword/<int:keyword_id>', methods=['POST'])
@login_required
def delete_keyword(keyword_id):
    """删除关键词"""
    keyword = Keyword.query.get_or_404(keyword_id)
    
    # 确保只能删除自己的关键词
    if keyword.user_id != current_user.id:
        flash('您没有权限执行此操作！', 'danger')
        return redirect(url_for('user.keywords'))
    
    db.session.delete(keyword)
    db.session.commit()
    
    flash('关键词已删除！', 'success')
    return redirect(url_for('user.keywords'))

@user_bp.route('/trigger-collection', methods=['POST'])
@login_required
def trigger_collection():
    """手动触发论文收集"""
    try:
        # 调用论文收集函数，只为当前用户收集
        success, total, new, message = collect_papers_for_user(current_user)
        
        if success:
            flash(f'论文收集成功！共收集 {total} 篇论文，其中 {new} 篇为新论文。', 'success')
        else:
            flash(f'论文收集失败：{message}', 'danger')
    except Exception as e:
        flash(f'论文收集过程中出错：{str(e)}', 'danger')
    
    return redirect(url_for('user.dashboard'))

# 新增API路由，用于定时任务调用
@user_bp.route('/api/trigger-all-collection', methods=['POST'])
def api_trigger_all_collection():
    """API接口：触发为所有用户收集论文（用于定时任务）"""
    from flask import current_app, jsonify
    
    # 检查访问密钥是否正确
    access_key = request.form.get('secret_key') or request.headers.get('X-API-Key')
    
    if not access_key or access_key != current_app.config['SECRET_KEY']:
        return jsonify({
            'success': False,
            'message': '访问密钥无效，没有授权'
        }), 403
    
    try:
        # 调用为所有用户收集论文的函数
        success_count, total_count, errors = collect_papers_for_all_users()
        
        return jsonify({
            'success': True,
            'total_users': total_count,
            'success_users': success_count,
            'errors_count': len(errors),
            'errors': errors[:10] if errors else []  # 只返回前10个错误
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'收集论文过程中出错：{str(e)}'
        }), 500

@user_bp.route('/papers')
@login_required
def papers():
    """用户的所有已发送论文"""
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页显示15篇论文
    
    # 获取用户的所有已发送论文，按发送时间降序排序
    pagination = SentPaper.query.filter_by(user_id=current_user.id)\
        .order_by(SentPaper.sent_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    papers = pagination.items
    
    # 添加now变量用于模板中显示年份
    now = datetime.now()
    
    return render_template('user/papers.html', 
                          papers=papers,
                          pagination=pagination,
                          now=now) 