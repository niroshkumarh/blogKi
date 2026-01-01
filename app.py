"""
Wide Angle Blog - Flask Application
Tenant-only blog with Entra ID authentication
"""
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blogsite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Entra ID Configuration
app.config['ENTRA_CLIENT_ID'] = os.environ.get('CLIENT_ID', '423dd38a-439a-4b99-a313-9472d2c0dad6')
app.config['ENTRA_CLIENT_SECRET'] = os.environ.get('CLIENT_SECRET', '')
app.config['ENTRA_TENANT_ID'] = os.environ.get('TENANT_ID', '6b8b8296-bdff-4ad8-93ad-84bcbf3842f5')
app.config['ENTRA_REDIRECT_URI'] = os.environ.get('REDIRECT_URI', 'http://localhost:5000/auth/callback')

# Admin email allowlist
admin_emails_str = os.environ.get('ADMIN_EMAILS', '')
app.config['ADMIN_EMAILS'] = [email.strip() for email in admin_emails_str.split(',') if email.strip()]

# Initialize database
from models import db
db.init_app(app)

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import models after db init
from models import User, Post, Comment, Like, ReadEvent

# Register blueprints
from auth import auth_bp
from api import api_bp
from admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Make login_required available
from auth import login_required

# Import models - must be after db init
import models

# Register blueprints
from auth import auth_bp
from api import api_bp
from admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Make login_required available
from auth import login_required


# Routes
@app.route('/')
def index():
    """Redirect to latest month archive"""
    latest_post = Post.query.filter_by(status='published').order_by(Post.published_at.desc()).first()
    if latest_post:
        return redirect(url_for('archive', month_key=latest_post.month_key))
    
    # Get all available months
    months = db.session.query(Post.month_key).filter_by(status='published').distinct().order_by(Post.month_key.desc()).all()
    months = [m[0] for m in months]
    
    return render_template('archive.html', posts=[], month_key=None, months=months)


@app.route('/archive/<month_key>')
@login_required
def archive(month_key):
    """Show posts for a specific month"""
    posts = Post.query.filter_by(month_key=month_key, status='published').order_by(Post.published_at.desc()).all()
    
    # Get all available months
    months = db.session.query(Post.month_key).filter_by(status='published').distinct().order_by(Post.month_key.desc()).all()
    months = [m[0] for m in months]
    
    return render_template('archive.html', posts=posts, month_key=month_key, months=months)


@app.route('/post/<slug>')
@login_required
def post_detail(slug):
    """Show full post with comments and likes"""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Get comments
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    
    # Get like count
    like_count = Like.query.filter_by(post_id=post.id).count()
    
    # Check if current user liked
    user_liked = False
    if 'user_id' in session:
        user_liked = Like.query.filter_by(post_id=post.id, user_id=session['user_id']).first() is not None
    
    # Get all available months for menu
    months = db.session.query(Post.month_key).filter_by(status='published').distinct().order_by(Post.month_key.desc()).all()
    months = [m[0] for m in months]
    
    return render_template('post.html', post=post, comments=comments, like_count=like_count, 
                          user_liked=user_liked, months=months)


@app.context_processor
def inject_now():
    """Make current year available in all templates"""
    return {'now': datetime.utcnow()}


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

