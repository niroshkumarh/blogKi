"""
Migrate existing blog posts from HTML files to database
"""
from datetime import datetime
from app import app, db
from models import Post


def migrate_posts():
    """Migrate existing HTML blog posts to database (currently disabled - posts added manually via admin)"""
    with app.app_context():
        print("ℹ️  Post migration skipped - articles are added manually via admin panel")
        print("[SUCCESS] Migration complete!")


if __name__ == '__main__':
    migrate_posts()

