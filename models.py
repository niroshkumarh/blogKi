"""
Database models for Wide Angle Blog
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
    # is_featured = db.Column(db.Boolean, default=False, index=True)  # Featured posts shown in carousel - TEMPORARILY DISABLED
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
        """Get unique viewers count"""
        return db.session.query(ReadEvent.user_id).filter_by(post_id=self.id).distinct().count()


class Comment(db.Model):
    """Comment model - user comments on posts"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    
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


class ReadEvent(db.Model):
    """ReadEvent model - tracking reading progress and time"""
    __tablename__ = 'read_events'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    percent = db.Column(db.Integer)  # scroll depth percentage (0-100)
    seconds = db.Column(db.Integer)  # time spent in seconds
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    
    def __repr__(self):
        return f'<ReadEvent {self.id} User {self.user_id} Post {self.post_id}>'

