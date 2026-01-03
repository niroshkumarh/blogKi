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
        # Count unique viewers (logged-in + anonymous)
        unique_users = db.session.query(ReadEvent.user_id).filter(
            ReadEvent.post_id == post.id,
            ReadEvent.user_id.isnot(None)
        ).distinct().count()
        
        unique_anon = db.session.query(ReadEvent.anon_id).filter(
            ReadEvent.post_id == post.id,
            ReadEvent.anon_id.isnot(None)
        ).distinct().count()
        
        views = unique_users + unique_anon
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
    from models import CommentLike
    from sqlalchemy import func
    
    post = Post.query.get_or_404(post_id)
    
    # Get unique viewers (logged-in + anonymous)
    # Count distinct user_id (for logged-in) and anon_id (for anonymous)
    unique_users = db.session.query(ReadEvent.user_id).filter(
        ReadEvent.post_id == post_id,
        ReadEvent.user_id.isnot(None)
    ).distinct().count()
    
    unique_anon = db.session.query(ReadEvent.anon_id).filter(
        ReadEvent.post_id == post_id,
        ReadEvent.anon_id.isnot(None)
    ).distinct().count()
    
    total_views = unique_users + unique_anon
    
    # Get logged-in viewers
    viewers = db.session.query(User).join(ReadEvent).filter(ReadEvent.post_id == post_id).distinct().all()
    
    # Get all read events
    read_events = ReadEvent.query.filter_by(post_id=post_id).order_by(ReadEvent.created_at.desc()).all()
    avg_completion = db.session.query(func.avg(ReadEvent.percent)).filter_by(post_id=post_id).scalar() or 0
    avg_time = db.session.query(func.avg(ReadEvent.seconds)).filter_by(post_id=post_id).scalar() or 0
    
    # Get likes
    likes = Like.query.filter_by(post_id=post_id).all()
    
    # Get all comments (including nested)
    all_comments = Comment.query.filter_by(post_id=post_id).all()
    top_level_comments = [c for c in all_comments if c.parent_id is None]
    reply_comments = [c for c in all_comments if c.parent_id is not None]
    
    # Get comment likes for this post
    comment_ids = [c.id for c in all_comments]
    comment_likes_count = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids)).count() if comment_ids else 0
    
    # Build comment data with nested structure
    comment_data = []
    for comment in sorted(top_level_comments, key=lambda x: x.created_at, reverse=True):
        data = {
            'comment': comment,
            'user': comment.user,
            'like_count': comment.get_like_count(),
            'reply_count': comment.get_reply_count(),
            'replies': []
        }
        
        # Get replies
        for reply in comment.get_all_replies():
            reply_data = {
                'comment': reply,
                'user': reply.user,
                'like_count': reply.get_like_count()
            }
            data['replies'].append(reply_data)
        
        comment_data.append(data)
    
    # Calculate engagement rate
    engagement_rate = 0
    if total_views > 0:
        total_interactions = len(likes) + len(all_comments) + comment_likes_count
        engagement_rate = round((total_interactions / total_views) * 100, 1)
    
    return render_template('admin/post_stats.html',
                          post=post,
                          viewers=viewers,
                          total_views=total_views,
                          avg_completion=round(avg_completion, 1),
                          avg_time=round(avg_time / 60, 1) if avg_time else 0,
                          likes=likes,
                          comment_data=comment_data,
                          total_comments=len(all_comments),
                          top_level_count=len(top_level_comments),
                          reply_count=len(reply_comments),
                          comment_likes_count=comment_likes_count,
                          engagement_rate=engagement_rate)


@admin_bp.route('/posts/<int:post_id>/readers')
@admin_required
def post_readers(post_id):
    """Detailed reader log for a specific post"""
    post = Post.query.get_or_404(post_id)
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get filters
    reader_type = request.args.get('reader_type', 'all')  # all, logged_in, anonymous
    
    # Build query
    query = ReadEvent.query.filter_by(post_id=post_id).order_by(ReadEvent.created_at.desc())
    
    if reader_type == 'logged_in':
        query = query.filter(ReadEvent.user_id.isnot(None))
    elif reader_type == 'anonymous':
        query = query.filter(ReadEvent.anon_id.isnot(None))
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    read_events = pagination.items
    
    # Calculate stats
    total_events = query.count()
    unique_users = db.session.query(ReadEvent.user_id).filter(
        ReadEvent.post_id == post_id,
        ReadEvent.user_id.isnot(None)
    ).distinct().count()
    
    unique_anon = db.session.query(ReadEvent.anon_id).filter(
        ReadEvent.post_id == post_id,
        ReadEvent.anon_id.isnot(None)
    ).distinct().count()
    
    return render_template('admin/post_readers.html',
                          post=post,
                          read_events=read_events,
                          pagination=pagination,
                          total_events=total_events,
                          unique_users=unique_users,
                          unique_anon=unique_anon,
                          reader_type=reader_type)


@admin_bp.route('/users')
@admin_required
def users_list():
    """List all users"""
    users = User.query.order_by(User.last_login_at.desc()).all()
    return render_template('admin/users_list.html', users=users)


@admin_bp.route('/readers')
@admin_required
def readers_list():
    """Global readers view with aggregation"""
    from sqlalchemy import func, case
    
    # Get pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get filters
    post_filter = request.args.get('post_id', type=int)
    
    # Build reader aggregation query
    # We need to group by either user_id or anon_id
    
    # Get logged-in users with stats
    logged_in_readers = db.session.query(
        User.id.label('user_id'),
        User.email.label('email'),
        User.name.label('name'),
        func.count(func.distinct(ReadEvent.post_id)).label('posts_read'),
        func.count(ReadEvent.id).label('total_events'),
        func.max(ReadEvent.created_at).label('last_seen'),
        func.min(ReadEvent.created_at).label('first_seen')
    ).join(ReadEvent, ReadEvent.user_id == User.id)
    
    if post_filter:
        logged_in_readers = logged_in_readers.filter(ReadEvent.post_id == post_filter)
    
    logged_in_readers = logged_in_readers.group_by(User.id, User.email, User.name).all()
    
    # Get anonymous readers with stats
    anon_readers = db.session.query(
        ReadEvent.anon_id.label('anon_id'),
        func.count(func.distinct(ReadEvent.post_id)).label('posts_read'),
        func.count(ReadEvent.id).label('total_events'),
        func.max(ReadEvent.created_at).label('last_seen'),
        func.min(ReadEvent.created_at).label('first_seen'),
        func.max(ReadEvent.ip_address).label('ip_address')
    ).filter(ReadEvent.anon_id.isnot(None))
    
    if post_filter:
        anon_readers = anon_readers.filter(ReadEvent.post_id == post_filter)
    
    anon_readers = anon_readers.group_by(ReadEvent.anon_id).all()
    
    # Combine and format
    readers = []
    
    for reader in logged_in_readers:
        readers.append({
            'type': 'logged_in',
            'user_id': reader.user_id,
            'label': reader.name or reader.email,
            'email': reader.email,
            'posts_read': reader.posts_read,
            'total_events': reader.total_events,
            'last_seen': reader.last_seen,
            'first_seen': reader.first_seen,
            'ip_address': None
        })
    
    for reader in anon_readers:
        readers.append({
            'type': 'anonymous',
            'anon_id': reader.anon_id,
            'label': f'Anon ({reader.anon_id[:8]}...)',
            'posts_read': reader.posts_read,
            'total_events': reader.total_events,
            'last_seen': reader.last_seen,
            'first_seen': reader.first_seen,
            'ip_address': reader.ip_address
        })
    
    # Sort by last_seen desc
    readers.sort(key=lambda x: x['last_seen'], reverse=True)
    
    # Manual pagination
    total = len(readers)
    start = (page - 1) * per_page
    end = start + per_page
    readers_page = readers[start:end]
    
    # Get all posts for filter dropdown
    all_posts = Post.query.filter_by(status='published').order_by(Post.published_at.desc()).all()
    
    return render_template('admin/readers.html',
                          readers=readers_page,
                          page=page,
                          per_page=per_page,
                          total=total,
                          all_posts=all_posts,
                          post_filter=post_filter)


@admin_bp.route('/readers/<reader_type>/<reader_id>')
@admin_required
def reader_detail(reader_type, reader_id):
    """Detailed view of what a specific reader has read"""
    if reader_type == 'user':
        user = User.query.get_or_404(reader_id)
        reader_label = user.name or user.email
        read_events = ReadEvent.query.filter_by(user_id=reader_id).order_by(ReadEvent.created_at.desc()).all()
    else:  # anonymous
        reader_label = f'Anonymous ({reader_id[:8]}...)'
        read_events = ReadEvent.query.filter_by(anon_id=reader_id).order_by(ReadEvent.created_at.desc()).all()
    
    # Group by post
    posts_read = {}
    for event in read_events:
        if event.post_id not in posts_read:
            posts_read[event.post_id] = {
                'post': event.post,
                'events': [],
                'max_percent': 0,
                'total_time': 0
            }
        posts_read[event.post_id]['events'].append(event)
        posts_read[event.post_id]['max_percent'] = max(posts_read[event.post_id]['max_percent'], event.percent or 0)
        posts_read[event.post_id]['total_time'] += event.seconds or 0
    
    return render_template('admin/reader_detail.html',
                          reader_type=reader_type,
                          reader_id=reader_id,
                          reader_label=reader_label,
                          posts_read=posts_read,
                          total_events=len(read_events))


@admin_bp.route('/comments')
@admin_required
def comments_list():
    """List all comments with nested structure and moderation options"""
    from models import Comment, CommentLike
    
    # Get all top-level comments (no parent)
    comments = Comment.query.filter_by(parent_id=None).order_by(Comment.created_at.desc()).all()
    
    # Build comment data with stats
    comment_data = []
    for comment in comments:
        data = {
            'comment': comment,
            'user': comment.user,
            'post': comment.post,
            'like_count': comment.get_like_count(),
            'reply_count': comment.get_reply_count(),
            'replies': []
        }
        
        # Get all replies
        for reply in comment.get_all_replies():
            reply_data = {
                'comment': reply,
                'user': reply.user,
                'like_count': reply.get_like_count()
            }
            data['replies'].append(reply_data)
        
        comment_data.append(data)
    
    # Get stats
    total_comments = Comment.query.count()
    total_likes = CommentLike.query.count()
    
    return render_template('admin/comments_list.html', 
                         comment_data=comment_data,
                         total_comments=total_comments,
                         total_likes=total_likes)


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@admin_required
def delete_comment_admin(comment_id):
    """Delete a comment (admin action)"""
    try:
        from models import Comment
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting comment: {str(e)}', 'error')
    
    return redirect(url_for('admin.comments_list'))


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

