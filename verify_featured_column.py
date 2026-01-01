"""
Verify and add is_featured column
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

def verify_and_add_featured():
    """Verify and add is_featured column"""
    print("Checking database schema...")
    
    conn = sqlite3.connect('blogsite.db')
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(posts)")
        columns = cursor.fetchall()
        
        print("\nCurrent posts table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        column_names = [col[1] for col in columns]
        
        if 'is_featured' not in column_names:
            print("\n❌ is_featured column is MISSING! Adding it now...")
            
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
            print("✅ Column added successfully!")
            
            # Verify again
            cursor.execute("PRAGMA table_info(posts)")
            new_columns = [col[1] for col in cursor.fetchall()]
            
            if 'is_featured' in new_columns:
                print("✅ Verification passed! Column exists now.")
            else:
                print("❌ Verification failed! Column still missing.")
        else:
            print("\n✅ is_featured column already exists!")
        
        # Show all posts
        cursor.execute("SELECT id, title, is_featured FROM posts")
        posts = cursor.fetchall()
        
        if posts:
            print("\n📝 Current posts:")
            for post_id, title, is_featured in posts:
                status = "⭐ FEATURED" if is_featured else "Not featured"
                print(f"  {post_id}. {title[:60]} - {status}")
        else:
            print("\n📝 No posts in database.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    verify_and_add_featured()

