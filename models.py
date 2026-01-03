"""
Database models for HORIZON Blog
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# Use timezone-aware datetime for PostgreSQL compatibility
def utcnow():
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)

db = SQLAlchemy()


class User(db.Model):
    """User model - stores Entra ID authenticated users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    entra_oid = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255))
    last_login_at = db.Column(db.DateTime, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comment_likes = db.relationship('CommentLike', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    read_events = db.relationship('ReadEvent', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_admin(self, admin_emails):
        """Check if user is admin"""
        return self.email in admin_emails


class Post(db.Model):
    """Post model - blog articles"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    month_key = db.Column(db.String(7), nullable=False, index=True)  # e.g., '2026-01'
    published_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)
    status = db.Column(db.String(20), default='draft', index=True)  # draft, published
    is_featured = db.Column(db.Boolean, default=False, index=True)  # Featured posts shown in carousel
    hero_image_path = db.Column(db.String(500))
    html_content = db.Column(db.Text)
    excerpt = db.Column(db.String(500))
    category = db.Column(db.String(100))
    read_time = db.Column(db.Integer)  # estimated read time in minutes
    # related_posts_json = db.Column(db.Text)  # JSON array of related post slugs - TEMPORARILY DISABLED
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    read_events = db.relationship('ReadEvent', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def get_like_count(self):
        """Get total likes for this post"""
        return self.likes.count()
    
    def get_comment_count(self):
        """Get total comments for this post"""
        return self.comments.count()
    
    def get_related_posts(self):
        """Get related posts as Post objects - TEMPORARILY DISABLED"""
        return []  # TODO: Re-enable when related_posts_json column is working
        # import json
        # if not self.related_posts_json:
        #     return []
        # try:
        #     slugs = json.loads(self.related_posts_json)
        #     return Post.query.filter(Post.slug.in_(slugs), Post.status == 'published').all()
        # except:
        #     return []
    
    def set_related_posts(self, post_slugs):
        """Set related posts from list of slugs - TEMPORARILY DISABLED"""
        pass  # TODO: Re-enable when related_posts_json column is working
        # import json
        # self.related_posts_json = json.dumps(post_slugs) if post_slugs else None
    
    def get_view_count(self):
        """Get unique viewers count (logged-in + anonymous)"""
        unique_users = db.session.query(ReadEvent.user_id).filter(
            ReadEvent.post_id == self.id,
            ReadEvent.user_id.isnot(None)
        ).distinct().count()
        
        unique_anon = db.session.query(ReadEvent.anon_id).filter(
            ReadEvent.post_id == self.id,
            ReadEvent.anon_id.isnot(None)
        ).distinct().count()
        
        return unique_users + unique_anon


class Comment(db.Model):
    """Comment model - user comments on posts (supports nested replies)"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True, index=True)  # For nested replies
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    
    # Self-referential relationship for nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade='all, delete-orphan')
    
    # Relationship with comment likes
    comment_likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_like_count(self):
        """Get total likes for this comment"""
        return self.comment_likes.count()
    
    def get_reply_count(self):
        """Get total direct replies to this comment"""
        return self.replies.count()
    
    def get_all_replies(self):
        """Get all replies sorted by creation date"""
        return self.replies.order_by(Comment.created_at.asc()).all()
    
    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'


class Like(db.Model):
    """Like model - user likes on posts"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    # Unique constraint - one like per user per post
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_user_like'),
    )
    
    def __repr__(self):
        return f'<Like {self.id} on Post {self.post_id}>'


class CommentLike(db.Model):
    """CommentLike model - user likes on comments"""
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    # Unique constraint - one like per user per comment
    __table_args__ = (
        db.UniqueConstraint('comment_id', 'user_id', name='unique_comment_user_like'),
    )
    
    def __repr__(self):
        return f'<CommentLike {self.id} on Comment {self.comment_id}>'


class ReadEvent(db.Model):
    """ReadEvent model - tracking reading progress and time (logged-in + anonymous)"""
    __tablename__ = 'read_events'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Nullable for anonymous
    anon_id = db.Column(db.String(255), nullable=True, index=True)  # Cookie-based anonymous ID
    ip_address = db.Column(db.String(45), nullable=True, index=True)  # IPv4/IPv6
    user_agent = db.Column(db.String(500), nullable=True)  # Browser user agent
    percent = db.Column(db.Integer)  # scroll depth percentage (0-100)
    seconds = db.Column(db.Integer)  # time spent in seconds
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    
    def get_reader_label(self):
        """Get a human-readable label for the reader"""
        if self.user_id:
            user = User.query.get(self.user_id)
            return user.name or user.email if user else f'User {self.user_id}'
        elif self.anon_id:
            return f'Anon ({self.anon_id[:8]}...)'
        else:
            return 'Unknown'
    
    def __repr__(self):
        return f'<ReadEvent {self.id} Post {self.post_id}>'

