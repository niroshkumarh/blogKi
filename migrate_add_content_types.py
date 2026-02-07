"""
Migration: Add Series, Videos, and Podcasts tables
"""
from app import app
from models import db

with app.app_context():
    print("Creating new content type tables...")
    db.create_all()
    print("OK: Series, Videos, and Podcasts tables created successfully!")
