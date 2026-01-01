"""Quick script to add related_posts_json column to existing database"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

try:
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(posts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'related_posts_json' in columns:
        print("✅ Column 'related_posts_json' already exists!")
    else:
        print("📝 Adding 'related_posts_json' column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN related_posts_json TEXT")
        conn.commit()
        print("✅ Column added successfully!")
    
    conn.close()
    print("\n🎉 Database updated! You can now restart the Flask app.")
    
except Exception as e:
    print(f"❌ Error: {e}")

