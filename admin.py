"""
Admin module - Dashboard and post editor
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from models import db, Post, User, Comment, Like, ReadEvent
from auth import admin_required
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with overview stats"""
    # Get overall stats
    total_posts = Post.query.filter_by(status='published').count()
    total_users = User.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    # Get recent posts with stats
    posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    
    post_stats = []
    for post in posts:
        views = db.session.query(ReadEvent.user_id).filter_by(post_id=post.id).distinct().count()
        likes = Like.query.filter_by(post_id=post.id).count()
        comments = Comment.query.filter_by(post_id=post.id).count()
        
        # Calculate average completion
        avg_completion = db.session.query(func.avg(ReadEvent.percent)).filter_by(post_id=post.id).scalar() or 0
        
        post_stats.append({
            'post': post,
            'views': views,
            'likes': likes,
            'comments': comments,
            'avg_completion': round(avg_completion, 1)
        })
    
    return render_template('admin/dashboard.html', 
                          total_posts=total_posts,
                          total_users=total_users,
                          total_comments=total_comments,
                          total_likes=total_likes,
                          post_stats=post_stats)


@admin_bp.route('/posts')
@admin_required
def posts_list():
    """List all posts"""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts_list.html', posts=posts)


@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@admin_required
def post_new():
    """Create new post"""
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip()
            month_key = request.form.get('month_key', '').strip()
            status = request.form.get('status', 'draft')
            html_content = request.form.get('html_content', '')
            excerpt = request.form.get('excerpt', '').strip()
            category = request.form.get('category', '').strip()
            read_time = request.form.get('read_time', 0)
            is_featured = request.form.get('is_featured') == 'on'  # Checkbox value
            
            # Validate required fields
            if not title or not slug or not month_key:
                flash('Title, slug, and month are required', 'error')
                return redirect(url_for('admin.post_new'))
            
            # Check if slug exists
            existing = Post.query.filter_by(slug=slug).first()
            if existing:
                flash('Slug already exists', 'error')
                return redirect(url_for('admin.post_new'))
            
            # Handle published date
            published_at = None
            if status == 'published':
                published_date = request.form.get('published_date')
                published_time = request.form.get('published_time', '00:00')
                if published_date:
                    published_at = datetime.strptime(f"{published_date} {published_time}", "%Y-%m-%d %H:%M")
                else:
                    published_at = datetime.utcnow()
            
            # Handle hero image upload
            hero_image_path = None
            if 'hero_image' in request.files:
                file = request.files['hero_image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid conflicts
                    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    # Use forward slashes for web URLs
                    hero_image_path = f"/{filepath.replace(chr(92), '/')}"  # chr(92) is backslash
            
            # Handle related posts
            related_posts = request.form.getlist('related_posts')
            
            # Create post
            post = Post(
                title=title,
                slug=slug,
                month_key=month_key,
                status=status,
                html_content=html_content,
                excerpt=excerpt,
                category=category,
                read_time=read_time,
                is_featured=is_featured,
                hero_image_path=hero_image_path,
                published_at=published_at
            )
            
            # Set related posts
            if related_posts:
                post.set_related_posts(related_posts)
            
            db.session.add(post)
            db.session.commit()
            
            flash('Post created successfully', 'success')
            return redirect(url_for('admin.posts_list'))
            
        except Exception as e:
            current_app.logger.error(f"Post creation error: {e}")
            flash('Failed to create post', 'error')
            return redirect(url_for('admin.post_new'))
    
    all_posts = Post.query.filter_by(status='published').order_by(Post.published_at.desc()).all()
    return render_template('admin/post_edit.html', post=None, all_posts=all_posts)


@admin_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def post_edit(post_id):
    """Edit existing post"""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        try:
            post.title = request.form.get('title', '').strip()
            post.slug = request.form.get('slug', '').strip()
            post.month_key = request.form.get('month_key', '').strip()
            post.status = request.form.get('status', 'draft')
            post.html_content = request.form.get('html_content', '')
            post.excerpt = request.form.get('excerpt', '').strip()
            post.category = request.form.get('category', '').strip()
            post.read_time = request.form.get('read_time', 0)
            post.is_featured = request.form.get('is_featured') == 'on'  # Checkbox value
            
            # Debug logging
            print(f"📝 [DEBUG] Received html_content with {len(post.html_content)} characters")
            print(f"📝 [DEBUG] Content preview: {post.html_content[:200] if post.html_content else 'EMPTY'}")
            print(f"📝 [DEBUG] Post title: {post.title}")
            print(f"📝 [DEBUG] Post slug: {post.slug}")
            
            # Validate required fields
            if not post.title or not post.slug or not post.month_key:
                flash('Title, slug, and month are required', 'error')
                return redirect(url_for('admin.post_edit', post_id=post_id))
            
            # Check if slug exists (excluding current post)
            existing = Post.query.filter(Post.slug == post.slug, Post.id != post_id).first()
            if existing:
                flash('Slug already exists', 'error')
                return redirect(url_for('admin.post_edit', post_id=post_id))
            
            # Handle published date
            if post.status == 'published':
                published_date = request.form.get('published_date')
                published_time = request.form.get('published_time', '00:00')
                if published_date:
                    post.published_at = datetime.strptime(f"{published_date} {published_time}", "%Y-%m-%d %H:%M")
                elif not post.published_at:
                    post.published_at = datetime.utcnow()
            
            # Handle hero image upload
            if 'hero_image' in request.files:
                file = request.files['hero_image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    # Use forward slashes for web URLs
                    post.hero_image_path = f"/{filepath.replace(chr(92), '/')}"  # chr(92) is backslash
            
            # Handle related posts
            related_posts = request.form.getlist('related_posts')
            post.set_related_posts(related_posts if related_posts else None)
            
            post.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Post updated successfully', 'success')
            return redirect(url_for('admin.posts_list'))
            
        except Exception as e:
            current_app.logger.error(f"Post update error: {e}")
            flash('Failed to update post', 'error')
            return redirect(url_for('admin.post_edit', post_id=post_id))
    
    all_posts = Post.query.filter_by(status='published').order_by(Post.published_at.desc()).all()
    return render_template('admin/post_edit.html', post=post, all_posts=all_posts)


@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def post_delete(post_id):
    """Delete a post"""
    try:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Post delete error: {e}")
        flash('Failed to delete post', 'error')
    
    return redirect(url_for('admin.posts_list'))


@admin_bp.route('/posts/<int:post_id>/stats')
@admin_required
def post_stats(post_id):
    """Detailed stats for a specific post"""
    post = Post.query.get_or_404(post_id)
    
    # Get unique viewers
    viewers = db.session.query(User).join(ReadEvent).filter(ReadEvent.post_id == post_id).distinct().all()
    
    # Get all read events
    read_events = ReadEvent.query.filter_by(post_id=post_id).order_by(ReadEvent.created_at.desc()).all()
    
    # Calculate stats
    total_views = len(viewers)
    avg_completion = db.session.query(func.avg(ReadEvent.percent)).filter_by(post_id=post_id).scalar() or 0
    avg_time = db.session.query(func.avg(ReadEvent.seconds)).filter_by(post_id=post_id).scalar() or 0
    
    # Get likes and comments
    likes = Like.query.filter_by(post_id=post_id).all()
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    
    return render_template('admin/post_stats.html',
                          post=post,
                          viewers=viewers,
                          total_views=total_views,
                          avg_completion=round(avg_completion, 1),
                          avg_time=round(avg_time / 60, 1) if avg_time else 0,
                          likes=likes,
                          comments=comments)


@admin_bp.route('/users')
@admin_required
def users_list():
    """List all users"""
    users = User.query.order_by(User.last_login_at.desc()).all()
    return render_template('admin/users_list.html', users=users)


@admin_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Upload image for editor"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Use forward slashes for web URLs
            web_path = f"/{filepath.replace(chr(92), '/')}"  # chr(92) is backslash
            
            return jsonify({
                'success': True,
                'url': web_path
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Image upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

