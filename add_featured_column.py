"""
Add is_featured column to posts table
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

def add_featured_column():
    """Add is_featured column to posts table"""
    print("Adding is_featured column to posts table...")
    
    # Connect to database
    conn = sqlite3.connect('blogsite.db')
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(posts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_featured' in columns:
            print("✓ Column 'is_featured' already exists!")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE posts
                ADD COLUMN is_featured INTEGER DEFAULT 0
            """)
            
            # Create index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_is_featured
                ON posts(is_featured)
            """)
            
            conn.commit()
            print("✓ Column 'is_featured' added successfully!")
        
        # Show current posts
        cursor.execute("SELECT id, title, is_featured FROM posts")
        posts = cursor.fetchall()
        
        if posts:
            print("\nCurrent posts:")
            for post_id, title, is_featured in posts:
                featured_status = "⭐ FEATURED" if is_featured else "Not featured"
                print(f"  {post_id}. {title[:50]} - {featured_status}")
        else:
            print("\nNo posts in database yet.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_featured_column()
    print("\n✅ Migration complete! You can now mark posts as featured in the admin panel.")

