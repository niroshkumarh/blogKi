"""
Authentication module - Microsoft Entra ID (Azure AD) OIDC integration
"""
import os
from functools import wraps
from flask import Blueprint, session, redirect, url_for, request, flash, current_app
from authlib.integrations.flask_client import OAuth
from datetime import datetime
from models import User, db

auth_bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with app context"""
    oauth.init_app(app)
    
    oauth.register(
        name='entra',
        client_id=app.config['ENTRA_CLIENT_ID'],
        client_secret=app.config['ENTRA_CLIENT_SECRET'],
        server_metadata_url=f"https://login.microsoftonline.com/{app.config['ENTRA_TENANT_ID']}/v2.0/.well-known/openid-configuration",
        client_kwargs={
            'scope': 'openid profile email'
        }
    )


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin(current_app.config['ADMIN_EMAILS']):
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login')
def login():
    """Initiate Entra ID login"""
    redirect_uri = current_app.config['ENTRA_REDIRECT_URI']
    return oauth.entra.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """Handle Entra ID callback"""
    try:
        token = oauth.entra.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            flash('Failed to get user information', 'error')
            return redirect(url_for('index'))
        
        # Extract user data
        entra_oid = user_info.get('oid')
        email = user_info.get('email') or user_info.get('preferred_username')
        name = user_info.get('name')
        
        if not entra_oid or not email:
            flash('Invalid user information received', 'error')
            return redirect(url_for('index'))
        
        # Find or create user
        user = User.query.filter_by(entra_oid=entra_oid).first()
        
        if not user:
            user = User(
                entra_oid=entra_oid,
                email=email,
                name=name
            )
            db.session.add(user)
        else:
            # Update user info
            user.email = email
            user.name = name
            user.last_login_at = datetime.utcnow()
        
        db.session.commit()
        
        # Set session
        session.permanent = True
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['is_admin'] = user.is_admin(current_app.config['ADMIN_EMAILS'])
        
        # Redirect to next URL or home
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        
        return redirect(url_for('index'))
        
    except Exception as e:
        current_app.logger.error(f"Auth callback error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('index'))


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    
    # Redirect to Entra ID logout
    tenant_id = current_app.config['ENTRA_TENANT_ID']
    post_logout_redirect = request.host_url
    
    logout_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout?post_logout_redirect_uri={post_logout_redirect}"
    
    return redirect(logout_url)


# Initialize oauth when blueprint is registered
@auth_bp.record_once
def on_load(state):
    """Initialize OAuth when blueprint is loaded"""
    init_oauth(state.app)

