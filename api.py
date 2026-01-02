"""
API endpoints for comments, likes, and read tracking
"""
from flask import Blueprint, request, jsonify, session, current_app
from models import db, Post, Comment, Like, ReadEvent, User
from auth import login_required
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Toggle like on a post"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        post = Post.query.get_or_404(post_id)
        
        # Check if already liked
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            db.session.commit()
            liked = False
        else:
            # Like
            new_like = Like(post_id=post_id, user_id=user_id)
            db.session.add(new_like)
            db.session.commit()
            liked = True
        
        # Get updated count
        like_count = Like.query.filter_by(post_id=post_id).count()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': like_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Like toggle error: {e}")
        return jsonify({'error': 'Failed to toggle like'}), 500


@api_bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        body = data.get('body', '').strip()
        
        if not body:
            return jsonify({'error': 'Comment body is required'}), 400
        
        if len(body) > 2000:
            return jsonify({'error': 'Comment too long (max 2000 characters)'}), 400
        
        post = Post.query.get_or_404(post_id)
        
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            body=body
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Get user info
        user = User.query.get(user_id)
        
        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'body': comment.body,
                'created_at': comment.created_at.isoformat(),
                'user_name': user.name or user.email
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Comment add error: {e}")
        return jsonify({'error': 'Failed to add comment'}), 500


@api_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (own comments or admin)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        comment = Comment.query.get_or_404(comment_id)
        user = User.query.get(user_id)
        
        # Check if user owns the comment or is admin
        if comment.user_id != user_id and not user.is_admin(current_app.config['ADMIN_EMAILS']):
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Comment delete error: {e}")
        return jsonify({'error': 'Failed to delete comment'}), 500


@api_bp.route('/read-event/<int:post_id>', methods=['POST'])
@login_required
def track_read_event(post_id):
    """Track reading progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        percent = data.get('percent', 0)
        seconds = data.get('seconds', 0)
        
        # Validate data
        percent = max(0, min(100, int(percent)))
        seconds = max(0, int(seconds))
        
        post = Post.query.get_or_404(post_id)
        
        # Create read event
        read_event = ReadEvent(
            post_id=post_id,
            user_id=user_id,
            percent=percent,
            seconds=seconds
        )
        
        db.session.add(read_event)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Read event error: {e}")
        return jsonify({'error': 'Failed to track read event'}), 500


@api_bp.route('/comments/<int:post_id>', methods=['GET'])
@login_required
def get_comments(post_id):
    """Get all comments for a post"""
    try:
        post = Post.query.get_or_404(post_id)
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        
        comment_list = []
        for comment in comments:
            user = User.query.get(comment.user_id)
            comment_list.append({
                'id': comment.id,
                'body': comment.body,
                'created_at': comment.created_at.isoformat(),
                'user_name': user.name or user.email,
                'can_delete': session.get('user_id') == comment.user_id or session.get('is_admin', False)
            })
        
        return jsonify({
            'success': True,
            'comments': comment_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Get comments error: {e}")
        return jsonify({'error': 'Failed to fetch comments'}), 500


