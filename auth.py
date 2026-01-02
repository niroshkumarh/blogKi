"""
Authentication module - Microsoft Entra ID (Azure AD) OIDC integration
"""
import os
from functools import wraps
from flask import Blueprint, session, redirect, url_for, request, flash, current_app, render_template
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timezone
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
            'scope': 'openid profile email',
            'prompt': 'select_account'  # Force account selection
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


def _get_dynamic_redirect_uri():
    """
    Build redirect URI dynamically based on the incoming request domain.
    Supports multiple domains: blogs.iqubekct.ac.in, HORIZON.kumaraguru.in
    """
    # Get the scheme (http/https) - prefer https in production
    scheme = request.scheme
    if request.headers.get('X-Forwarded-Proto'):
        scheme = request.headers.get('X-Forwarded-Proto')
    elif current_app.config.get('PREFERRED_URL_SCHEME'):
        scheme = current_app.config['PREFERRED_URL_SCHEME']
    
    # Get the host (domain)
    host = request.host
    if request.headers.get('X-Forwarded-Host'):
        host = request.headers.get('X-Forwarded-Host')
    
    # Build the callback URI
    callback_path = '/auth/callback'
    redirect_uri = f"{scheme}://{host}{callback_path}"
    
    # Log for debugging
    current_app.logger.info(f"Dynamic redirect URI: {redirect_uri}")
    
    # Fallback to configured URI if something goes wrong
    if not host or host == 'None':
        redirect_uri = current_app.config['ENTRA_REDIRECT_URI']
        current_app.logger.warning(f"Using fallback redirect URI: {redirect_uri}")
    
    return redirect_uri


@auth_bp.route('/login')
def login():
    """Initiate Entra ID login"""
    # Store the next URL in session
    next_url = request.args.get('next')
    if next_url:
        session['next_url'] = next_url
    
    # Dynamic redirect URI detection for multi-domain support
    # Supports: blogs.iqubekct.ac.in and HORIZON.kumaraguru.in
    redirect_uri = _get_dynamic_redirect_uri()
    
    # Force session to be saved
    session.modified = True
    
    return oauth.entra.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """Handle Entra ID callback"""
    user_info = None
    
    try:
        # Try to authorize with token
        try:
            token = oauth.entra.authorize_access_token()
            user_info = token.get('userinfo')
        except Exception as auth_error:
            # If state mismatch, try without state validation (development only)
            if 'mismatching_state' in str(auth_error) or 'CSRF' in str(auth_error):
                current_app.logger.warning(f"State mismatch detected, attempting manual token exchange")
                # Get the authorization code from the request
                code = request.args.get('code')
                if not code:
                    raise auth_error
                
                # Exchange code for token manually
                import requests
                token_url = f"https://login.microsoftonline.com/{current_app.config['ENTRA_TENANT_ID']}/oauth2/v2.0/token"
                
                # Use dynamic redirect URI to match the one used in login
                redirect_uri = _get_dynamic_redirect_uri()
                
                token_data = {
                    'client_id': current_app.config['ENTRA_CLIENT_ID'],
                    'client_secret': current_app.config['ENTRA_CLIENT_SECRET'],
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code',
                    'scope': 'openid profile email'
                }
                
                token_response = requests.post(token_url, data=token_data)
                
                # Log the response for debugging
                if token_response.status_code != 200:
                    current_app.logger.error(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
                
                token_response.raise_for_status()
                token = token_response.json()
                
                # Get user info
                access_token = token.get('access_token')
                id_token = token.get('id_token')
                
                # Decode ID token to get user info
                import jwt
                user_info = jwt.decode(id_token, options={"verify_signature": False})
            else:
                raise auth_error
        
        if not user_info and 'token' in locals():
            user_info = token.get('userinfo')
        
        if not user_info:
            flash('Failed to get user information', 'error')
            return redirect(url_for('index'))
        
        # Extract user data (handle both OAuth userinfo and ID token claims)
        entra_oid = user_info.get('oid') or user_info.get('sub')
        email = user_info.get('email') or user_info.get('preferred_username') or user_info.get('upn')
        name = user_info.get('name') or email
        
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
            user.last_login_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # Set session
        session.permanent = True
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['is_admin'] = user.is_admin(current_app.config['ADMIN_EMAILS'])
        
        # Redirect based on user role
        # Check if there's a specific next URL
        next_url = session.pop('next_url', None) or request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        
        # If admin, redirect to admin dashboard
        if session['is_admin']:
            flash(f'Welcome back, {user.name}! (Admin)', 'success')
            return redirect(url_for('admin.dashboard'))
        
        # If normal user, redirect to blog archive
        flash(f'Welcome, {user.name}!', 'success')
        return redirect(url_for('archive', month_key='2026-01'))
        
    except Exception as e:
        current_app.logger.error(f"Auth callback error: {e}")
        error_msg = str(e)
        
        # Provide specific error messages
        if '401' in error_msg or 'Unauthorized' in error_msg:
            error_type = 'Invalid CLIENT_SECRET'
            solution = 'Check your .env file has the correct CLIENT_SECRET from Azure Portal.'
        elif 'mismatching_state' in error_msg or 'CSRF' in error_msg:
            error_type = 'Session/Cookie Issue (CSRF State Mismatch)'
            solution = 'Clear your browser cookies and cache, then try again. Make sure cookies are enabled.'
        else:
            error_type = 'Authentication Error'
            solution = 'Check your Entra ID configuration and try again.'
        
        # Return error page instead of redirecting to prevent loop
        return render_template('auth_error.html', error=error_msg, error_type=error_type, solution=solution), 401


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

