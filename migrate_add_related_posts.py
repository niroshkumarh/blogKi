"""Add related_posts_json column to posts table"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
from pathlib import Path

# Database path
DB_PATH = 'blog.db'

def migrate():
    """Add related_posts_json column if it doesn't exist"""
    if not Path(DB_PATH).exists():
        print(f"❌ Database {DB_PATH} not found. Run init_db.py first.")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'related_posts_json' in columns:
            print("✅ Column 'related_posts_json' already exists. No migration needed.")
            conn.close()
            return True
        
        # Add the column
        print("📝 Adding 'related_posts_json' column to posts table...")
        cursor.execute("ALTER TABLE posts ADD COLUMN related_posts_json TEXT")
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("   - Added 'related_posts_json' column to posts table")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add Related Posts Support")
    print("=" * 60)
    print()
    
    success = migrate()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration completed!")
        print()
        print("You can now:")
        print("  1. Restart your Flask app")
        print("  2. Edit posts in the admin panel")
        print("  3. Select related posts for each article")
    else:
        print("❌ Migration failed. Please check errors above.")
    print("=" * 60)

