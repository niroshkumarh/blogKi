"""
API endpoints for comments, likes, and read tracking
"""
from flask import Blueprint, request, jsonify, session, current_app
from models import db, Post, Comment, Like, ReadEvent, User, CommentLike
from auth import login_required
from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import socket
import ipaddress
from functools import lru_cache
import hashlib

api_bp = Blueprint('api', __name__)

# Simple in-memory cache for link previews (TTL: 1 hour)
LINK_PREVIEW_CACHE = {}
CACHE_TTL = 3600

# SSRF Protection: Block these IP ranges
BLOCKED_IP_RANGES = [
    ipaddress.ip_network('127.0.0.0/8'),      # Loopback
    ipaddress.ip_network('10.0.0.0/8'),       # Private
    ipaddress.ip_network('172.16.0.0/12'),    # Private
    ipaddress.ip_network('192.168.0.0/16'),   # Private
    ipaddress.ip_network('169.254.0.0/16'),   # Link-local
    ipaddress.ip_network('::1/128'),          # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),         # IPv6 private
    ipaddress.ip_network('fe80::/10'),        # IPv6 link-local
]

# Known oEmbed providers
OEMBED_PROVIDERS = {
    'youtube.com': 'https://www.youtube.com/oembed?url={url}&format=json',
    'youtu.be': 'https://www.youtube.com/oembed?url={url}&format=json',
    'vimeo.com': 'https://vimeo.com/api/oembed.json?url={url}',
    'twitter.com': 'https://publish.twitter.com/oembed?url={url}',
    'x.com': 'https://publish.twitter.com/oembed?url={url}',
    'instagram.com': 'https://graph.facebook.com/v12.0/instagram_oembed?url={url}',
}


def is_safe_url(url):
    """Validate URL and check for SSRF attacks"""
    try:
        parsed = urlparse(url)
        
        # Only allow http/https
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP/HTTPS URLs are allowed"
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid hostname"
        
        # Resolve hostname to IP
        try:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            
            # Check against blocked ranges
            for blocked_range in BLOCKED_IP_RANGES:
                if ip_obj in blocked_range:
                    return False, f"Access to {hostname} ({ip}) is blocked"
            
        except socket.gaierror:
            return False, "Cannot resolve hostname"
        except ValueError:
            return False, "Invalid IP address"
        
        return True, None
        
    except Exception as e:
        return False, f"URL validation error: {str(e)}"


def get_oembed_data(url):
    """Try to fetch oEmbed data from known providers"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        # Check if domain has oEmbed support
        for provider_domain, oembed_url in OEMBED_PROVIDERS.items():
            if provider_domain in domain:
                try:
                    response = requests.get(
                        oembed_url.format(url=url),
                        timeout=5,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'type': data.get('type', 'video'),
                            'url': url,
                            'title': data.get('title', ''),
                            'description': data.get('description', ''),
                            'image': data.get('thumbnail_url', ''),
                            'site_name': data.get('provider_name', ''),
                            'embed_html': data.get('html', ''),
                            'provider': provider_domain
                        }
                except Exception as e:
                    current_app.logger.warning(f"oEmbed fetch failed for {url}: {e}")
                    continue
        
        return None
        
    except Exception as e:
        current_app.logger.error(f"oEmbed error: {e}")
        return None


def parse_og_tags(html, url):
    """Parse Open Graph and Twitter Card meta tags from HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        og_data = {
            'type': 'link',
            'url': url,
            'title': '',
            'description': '',
            'image': '',
            'site_name': '',
            'embed_html': None,
            'provider': None
        }
        
        # Try Open Graph tags
        og_tags = {
            'og:type': 'type',
            'og:url': 'url',
            'og:title': 'title',
            'og:description': 'description',
            'og:image': 'image',
            'og:site_name': 'site_name',
        }
        
        for og_tag, key in og_tags.items():
            tag = soup.find('meta', property=og_tag) or soup.find('meta', attrs={'name': og_tag})
            if tag and tag.get('content'):
                og_data[key] = tag['content']
        
        # Fallback to Twitter Card tags
        if not og_data['title']:
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                og_data['title'] = twitter_title['content']
        
        if not og_data['description']:
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc and twitter_desc.get('content'):
                og_data['description'] = twitter_desc['content']
        
        if not og_data['image']:
            twitter_img = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_img and twitter_img.get('content'):
                og_data['image'] = twitter_img['content']
        
        # Fallback to HTML tags
        if not og_data['title']:
            title_tag = soup.find('title')
            if title_tag:
                og_data['title'] = title_tag.get_text().strip()
        
        if not og_data['description']:
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                og_data['description'] = desc_tag['content']
        
        # Extract domain as site_name if not provided
        if not og_data['site_name']:
            parsed = urlparse(url)
            og_data['site_name'] = parsed.netloc.replace('www.', '')
        
        return og_data
        
    except Exception as e:
        current_app.logger.error(f"OG parsing error: {e}")
        return None


@api_bp.route('/link-preview', methods=['GET'])
@login_required
def link_preview():
    """Fetch link preview metadata (Open Graph + oEmbed)"""
    try:
        url = request.args.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        # Validate URL for SSRF
        is_safe, error_msg = is_safe_url(url)
        if not is_safe:
            return jsonify({'error': f'Invalid URL: {error_msg}'}), 400
        
        # Check cache
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in LINK_PREVIEW_CACHE:
            cached_data, cached_time = LINK_PREVIEW_CACHE[cache_key]
            if (datetime.now().timestamp() - cached_time) < CACHE_TTL:
                return jsonify({'success': True, 'data': cached_data})
        
        # Try oEmbed first (best for videos)
        oembed_data = get_oembed_data(url)
        if oembed_data:
            LINK_PREVIEW_CACHE[cache_key] = (oembed_data, datetime.now().timestamp())
            return jsonify({'success': True, 'data': oembed_data})
        
        # Fallback to Open Graph scraping
        try:
            response = requests.get(
                url,
                timeout=8,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                allow_redirects=True,
                stream=True
            )
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                return jsonify({'error': 'URL does not point to an HTML page'}), 400
            
            # Limit download size (max 2MB)
            max_size = 2 * 1024 * 1024
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > max_size:
                    break
            
            html = content.decode('utf-8', errors='ignore')
            
            og_data = parse_og_tags(html, url)
            if og_data:
                LINK_PREVIEW_CACHE[cache_key] = (og_data, datetime.now().timestamp())
                return jsonify({'success': True, 'data': og_data})
            else:
                return jsonify({'error': 'Could not extract metadata from URL'}), 400
                
        except requests.Timeout:
            return jsonify({'error': 'Request timeout'}), 408
        except requests.RequestException as e:
            return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Link preview error: {e}")
        return jsonify({'error': 'Failed to generate preview'}), 500


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
    """Add a comment to a post or reply to an existing comment"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        body = data.get('body', '').strip()
        parent_id = data.get('parent_id', None)  # For nested replies
        
        if not body:
            return jsonify({'error': 'Comment body is required'}), 400
        
        if len(body) > 2000:
            return jsonify({'error': 'Comment too long (max 2000 characters)'}), 400
        
        post = Post.query.get_or_404(post_id)
        
        # If parent_id provided, validate it exists and belongs to this post
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if not parent_comment or parent_comment.post_id != post_id:
                return jsonify({'error': 'Invalid parent comment'}), 400
        
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            body=body,
            parent_id=parent_id
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
                'user_name': user.name or user.email,
                'parent_id': parent_id,
                'like_count': 0,
                'reply_count': 0
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


@api_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def toggle_comment_like(comment_id):
    """Toggle like on a comment"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        comment = Comment.query.get_or_404(comment_id)
        
        # Check if already liked
        existing_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user_id).first()
        
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            db.session.commit()
            liked = False
        else:
            # Like
            new_like = CommentLike(comment_id=comment_id, user_id=user_id)
            db.session.add(new_like)
            db.session.commit()
            liked = True
        
        # Get updated count
        like_count = CommentLike.query.filter_by(comment_id=comment_id).count()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': like_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Comment like toggle error: {e}")
        return jsonify({'error': 'Failed to toggle comment like'}), 500


@api_bp.route('/read-event/<int:post_id>', methods=['POST'])
def track_read_event(post_id):
    """Track reading progress (logged-in users + anonymous visitors)"""
    try:
        data = request.get_json()
        percent = data.get('percent', 0)
        seconds = data.get('seconds', 0)
        
        # Validate data
        percent = max(0, min(100, int(percent)))
        seconds = max(0, int(seconds))
        
        post = Post.query.get_or_404(post_id)
        
        # Determine identity: logged-in user or anonymous
        user_id = session.get('user_id')
        anon_id = data.get('anon_id')  # Always capture anon_id (for cross-session tracking)
        
        # Log what we're tracking
        current_app.logger.info(f"📊 Read event: post_id={post_id}, user_id={user_id}, anon_id={anon_id[:8] if anon_id else None}..., percent={percent}%, seconds={seconds}s")
        
        if not user_id and not anon_id:
            # Need at least one identifier
            return jsonify({'error': 'Missing user_id or anon_id for tracking'}), 400
        
        # Capture IP address (handle reverse proxy)
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            # X-Forwarded-For can contain multiple IPs, take the first (client)
            ip_address = ip_address.split(',')[0].strip()
        
        # Capture user agent
        user_agent = request.headers.get('User-Agent', '')[:500]  # Limit to column size
        
        # Create read event
        read_event = ReadEvent(
            post_id=post_id,
            user_id=user_id,
            anon_id=anon_id,
            ip_address=ip_address,
            user_agent=user_agent,
            percent=percent,
            seconds=seconds
        )
        
        db.session.add(read_event)
        db.session.commit()
        
        # Return user info for debugging
        return jsonify({
            'success': True,
            'tracked_as': 'logged_in' if user_id else 'anonymous',
            'user_id': user_id,
            'anon_id': anon_id[:8] + '...' if anon_id else None
        })
        
    except Exception as e:
        current_app.logger.error(f"Read event error: {e}")
        return jsonify({'error': 'Failed to track read event'}), 500


@api_bp.route('/comments/<int:post_id>', methods=['GET'])
@login_required
def get_comments(post_id):
    """Get all comments for a post (nested structure with likes)"""
    try:
        post = Post.query.get_or_404(post_id)
        user_id = session.get('user_id')
        
        # Get all top-level comments (no parent)
        comments = Comment.query.filter_by(post_id=post_id, parent_id=None).order_by(Comment.created_at.desc()).all()
        
        def format_comment(comment):
            """Format a comment with all its details"""
            user = User.query.get(comment.user_id)
            
            # Check if current user liked this comment
            user_liked = False
            if user_id:
                user_liked = CommentLike.query.filter_by(comment_id=comment.id, user_id=user_id).first() is not None
            
            # Get replies
            replies = comment.get_all_replies()
            formatted_replies = [format_comment(reply) for reply in replies]
            
            return {
                'id': comment.id,
                'body': comment.body,
                'created_at': comment.created_at.isoformat(),
                'user_name': user.name or user.email,
                'like_count': comment.get_like_count(),
                'reply_count': comment.get_reply_count(),
                'user_liked': user_liked,
                'replies': formatted_replies,
                'can_delete': user_id == comment.user_id or session.get('is_admin', False),
                'parent_id': comment.parent_id
            }
        
        comment_list = [format_comment(comment) for comment in comments]
        
        return jsonify({
            'success': True,
            'comments': comment_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Get comments error: {e}")
        return jsonify({'error': 'Failed to fetch comments'}), 500


