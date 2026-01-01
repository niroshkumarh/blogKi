"""
Configuration module for Flask app
"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blogsite.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Entra ID
    ENTRA_CLIENT_ID = os.environ.get('CLIENT_ID', '')
    ENTRA_CLIENT_SECRET = os.environ.get('CLIENT_SECRET', '')
    ENTRA_TENANT_ID = os.environ.get('TENANT_ID', '')
    ENTRA_REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:5000/auth/callback')
    ENTRA_AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('TENANT_ID', '')}"
    ENTRA_SCOPE = ['openid', 'profile', 'email']
    
    # Admin emails
    ADMIN_EMAILS = [email.strip() for email in os.environ.get('ADMIN_EMAILS', '').split(',') if email.strip()]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

