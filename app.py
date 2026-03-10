"""
HORIZON Blog - Flask Application
Tenant-only blog with Entra ID authentication
"""
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, send_from_directory, flash, abort, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
# from flask_session import Session  # Not needed - using Flask's built-in session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# Apply ProxyFix middleware to handle X-Forwarded-* headers from Nginx/Cloudflare
# This is critical for OAuth to work correctly behind a reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - support both PostgreSQL and SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///blogsite.db')
# Fix for PostgreSQL URL from some platforms (they use postgres:// instead of postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Session configuration for OAuth - use Flask's built-in signed cookie sessions
# Detect if we're in production (behind HTTPS proxy)
is_production = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_SECURE'] = is_production  # Only send cookies over HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['PREFERRED_URL_SCHEME'] = 'https' if is_production else 'http'

# Entra ID Configuration
app.config['ENTRA_CLIENT_ID'] = os.environ.get('CLIENT_ID', '423dd38a-439a-4b99-a313-9472d2c0dad6')
app.config['ENTRA_CLIENT_SECRET'] = os.environ.get('CLIENT_SECRET', '')
app.config['ENTRA_TENANT_ID'] = os.environ.get('TENANT_ID', '6b8b8296-bdff-4ad8-93ad-84bcbf3842f5')
app.config['ENTRA_REDIRECT_URI'] = os.environ.get('REDIRECT_URI', 'http://localhost:4343/auth/callback')

# Admin email allowlist
admin_emails_str = os.environ.get('ADMIN_EMAILS', '')
app.config['ADMIN_EMAILS'] = [email.strip() for email in admin_emails_str.split(',') if email.strip()]

# Initialize database
from models import db
db.init_app(app)

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import models after db init
from models import User, Post, Comment, Like, ReadEvent, MonthVisibility

# Register blueprints
from auth import auth_bp, login_required
from api import api_bp
from admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')


def get_visible_months():
    """Get months visible to the current user based on their role.
    Admin/PreRelease: all months with published posts.
    Regular users: only months with visibility='public'.
    Months with no MonthVisibility record default to 'prerelease' (hidden from public).
    """
    all_months = db.session.query(Post.month_key).filter_by(
        status='published'
    ).distinct().all()
    all_month_keys = [m[0] for m in all_months]

    is_prerelease = session.get('is_prerelease', False)

    if is_prerelease:
        # PreRelease users see all months (public + prerelease)
        return sorted(all_month_keys, reverse=True)

    # Everyone else (including admins not in prerelease group): only public months
    public_months = db.session.query(MonthVisibility.month_key).filter_by(
        visibility='public'
    ).all()
    public_month_keys = set(m[0] for m in public_months)

    visible = [mk for mk in all_month_keys if mk in public_month_keys]
    return sorted(visible, reverse=True)


@app.context_processor
def inject_month_navigation():
    """Inject navbar months and archive months into all templates"""
    if 'user_id' not in session:
        return {'nav_months': [], 'archive_months': [], 'months': []}

    visible = get_visible_months()
    return {
        'nav_months': visible[:3],
        'archive_months': visible[3:],
        'months': visible,
    }


# Routes
@app.route('/')
@login_required
def index():
    """Redirect to latest visible month archive"""
    visible_months = get_visible_months()

    if visible_months:
        return redirect(url_for('archive', month_key=visible_months[0]))

    # No visible months — show empty archive with current month
    current_month = datetime.now().strftime('%Y-%m')
    return render_template('archive.html', posts=[], month_key=current_month)


@app.route('/test')
def test():
    """Test route to check if app is working"""
    return """
    <h1>Flask App is Running!</h1>
    <p>Database posts: """ + str(Post.query.count()) + """</p>
    <p>Auth config check:</p>
    <ul>
        <li>CLIENT_ID: """ + str(app.config['ENTRA_CLIENT_ID'][:20]) + """...</li>
        <li>CLIENT_SECRET configured: """ + str(bool(app.config['ENTRA_CLIENT_SECRET'])) + """</li>
        <li>TENANT_ID: """ + str(app.config['ENTRA_TENANT_ID'][:20]) + """...</li>
    </ul>
    <p><a href="/auth/login">Try Login</a></p>
    """


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/archive/<month_key>')
@login_required
def archive(month_key):
    """Show posts for a specific month"""
    visible_months = get_visible_months()
    if month_key not in visible_months:
        flash('This content is not available yet.', 'warning')
        return redirect(url_for('index'))

    posts = Post.query.filter_by(month_key=month_key, status='published').order_by(Post.published_at.desc()).all()

    # Get only posts marked as featured
    featured_posts = Post.query.filter_by(month_key=month_key, status='published', is_featured=True).order_by(Post.published_at.desc()).limit(5).all()

    return render_template('archive.html', posts=posts, featured_posts=featured_posts, month_key=month_key)


@app.route('/post/<slug>')
@login_required
def post_detail(slug):
    """Show full post with comments and likes"""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()

    # Check month visibility
    visible_months = get_visible_months()
    if post.month_key not in visible_months:
        abort(404)

    # Get comments
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()

    # Get like count
    like_count = Like.query.filter_by(post_id=post.id).count()

    # Check if current user liked
    user_liked = False
    if 'user_id' in session:
        user_liked = Like.query.filter_by(post_id=post.id, user_id=session['user_id']).first() is not None

    return render_template('post.html', post=post, comments=comments, like_count=like_count,
                          user_liked=user_liked)


@app.template_filter('format_month')
def format_month_filter(month_key):
    """Convert month_key (YYYY-MM) to 'Month YYYY' format"""
    try:
        year, month = month_key.split('-')
        month_names = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        return f"{month_names.get(month, month)} {year}"
    except:
        return month_key


@app.context_processor
def inject_now():
    """Make current year available in all templates"""
    from datetime import timezone
    return {'now': datetime.now(timezone.utc)}


@app.route('/archives')
@login_required
def archives():
    """Show all older months not displayed in navbar"""
    visible_months = get_visible_months()
    older_months = visible_months[3:]  # Months beyond the top 3 in navbar

    months_data = []
    for mk in older_months:
        post_count = Post.query.filter_by(month_key=mk, status='published').count()
        months_data.append({
            'month_key': mk,
            'post_count': post_count,
        })

    return render_template('archives.html', months_data=months_data)


@app.errorhandler(413)
def request_entity_too_large(e):
    flash('Upload failed: File size exceeds the 16MB limit. Please reduce the image size and try again.', 'error')
    return redirect(request.url), 302


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Database is already created - don't recreate it
    # with app.app_context():
    #     db.create_all()
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

