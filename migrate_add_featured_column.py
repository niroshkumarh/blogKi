"""
Migration script to add is_featured column to Post table
Run this once to update existing database
Works with both PostgreSQL and SQLite
"""
from app import app
from models import db
from sqlalchemy import text

def migrate_add_featured():
    with app.app_context():
        try:
            # Try to add the column
            print("Adding is_featured column to post table...")
            
            # PostgreSQL and SQLite compatible syntax
            db.session.execute(text("ALTER TABLE post ADD COLUMN is_featured BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            
            print("✅ Successfully added is_featured column")
            print("All posts are set to is_featured=False by default")
            print("Go to Admin → Edit Post to mark posts as Featured")
            
        except Exception as e:
            error_str = str(e)
            if 'already exists' in error_str or 'duplicate column' in error_str.lower():
                print("✅ is_featured column already exists - no action needed")
            else:
                print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_add_featured()

