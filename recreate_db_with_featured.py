"""
Recreate database with is_featured column - CLEAN approach
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import shutil
from datetime import datetime

def recreate_database():
    """Backup old DB, create new one with correct schema, migrate data"""
    
    # 1. Backup existing database
    print("📦 Step 1: Backing up existing database...")
    try:
        shutil.copy2('blogsite.db', f'blogsite_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        print("✅ Backup created successfully!")
    except Exception as e:
        print(f"⚠️  Backup failed (might not exist yet): {e}")
    
    # 2. Read existing data
    print("\n📖 Step 2: Reading existing posts...")
    existing_posts = []
    existing_users = []
    existing_comments = []
    existing_likes = []
    existing_read_events = []
    
    try:
        conn_old = sqlite3.connect('blogsite.db')
        cursor_old = conn_old.cursor()
        
        # Read all posts
        cursor_old.execute("SELECT * FROM posts")
        posts_data = cursor_old.fetchall()
        cursor_old.execute("PRAGMA table_info(posts)")
        posts_columns = [col[1] for col in cursor_old.fetchall()]
        existing_posts = [dict(zip(posts_columns, row)) for row in posts_data]
        
        # Read users
        cursor_old.execute("SELECT * FROM users")
        users_data = cursor_old.fetchall()
        cursor_old.execute("PRAGMA table_info(users)")
        users_columns = [col[1] for col in cursor_old.fetchall()]
        existing_users = [dict(zip(users_columns, row)) for row in users_data]
        
        # Read comments
        cursor_old.execute("SELECT * FROM comments")
        comments_data = cursor_old.fetchall()
        cursor_old.execute("PRAGMA table_info(comments)")
        comments_columns = [col[1] for col in cursor_old.fetchall()]
        existing_comments = [dict(zip(comments_columns, row)) for row in comments_data]
        
        # Read likes
        cursor_old.execute("SELECT * FROM likes")
        likes_data = cursor_old.fetchall()
        cursor_old.execute("PRAGMA table_info(likes)")
        likes_columns = [col[1] for col in cursor_old.fetchall()]
        existing_likes = [dict(zip(likes_columns, row)) for row in likes_data]
        
        # Read read_events
        cursor_old.execute("SELECT * FROM read_events")
        read_events_data = cursor_old.fetchall()
        cursor_old.execute("PRAGMA table_info(read_events)")
        read_events_columns = [col[1] for col in cursor_old.fetchall()]
        existing_read_events = [dict(zip(read_events_columns, row)) for row in read_events_data]
        
        conn_old.close()
        
        print(f"✅ Found {len(existing_posts)} posts, {len(existing_users)} users, {len(existing_comments)} comments")
        
    except Exception as e:
        print(f"⚠️  Error reading old data: {e}")
    
    # 3. Delete old database files
    print("\n🗑️  Step 3: Removing old database files...")
    import os
    try:
        if os.path.exists('blogsite.db'):
            os.remove('blogsite.db')
        if os.path.exists('blogsite.db-shm'):
            os.remove('blogsite.db-shm')
        if os.path.exists('blogsite.db-wal'):
            os.remove('blogsite.db-wal')
        print("✅ Old database files removed!")
    except Exception as e:
        print(f"❌ Error removing files: {e}")
        return
    
    # 4. Create new database with correct schema
    print("\n🏗️  Step 4: Creating new database with correct schema...")
    conn_new = sqlite3.connect('blogsite.db')
    cursor_new = conn_new.cursor()
    
    try:
        # Create users table
        cursor_new.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entra_oid VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                last_login_at DATETIME,
                created_at DATETIME
            )
        """)
        cursor_new.execute("CREATE INDEX idx_users_entra_oid ON users(entra_oid)")
        cursor_new.execute("CREATE INDEX idx_users_email ON users(email)")
        
        # Create posts table WITH is_featured
        cursor_new.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                month_key VARCHAR(7) NOT NULL,
                published_at DATETIME,
                updated_at DATETIME,
                created_at DATETIME,
                status VARCHAR(20) DEFAULT 'draft',
                is_featured INTEGER DEFAULT 0,
                hero_image_path VARCHAR(500),
                html_content TEXT,
                excerpt VARCHAR(500),
                category VARCHAR(100),
                read_time INTEGER,
                related_posts_json TEXT
            )
        """)
        cursor_new.execute("CREATE INDEX idx_posts_slug ON posts(slug)")
        cursor_new.execute("CREATE INDEX idx_posts_month_key ON posts(month_key)")
        cursor_new.execute("CREATE INDEX idx_posts_status ON posts(status)")
        cursor_new.execute("CREATE INDEX idx_posts_is_featured ON posts(is_featured)")
        
        # Create comments table
        cursor_new.execute("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                body TEXT NOT NULL,
                created_at DATETIME,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor_new.execute("CREATE INDEX idx_comments_post_id ON comments(post_id)")
        cursor_new.execute("CREATE INDEX idx_comments_user_id ON comments(user_id)")
        
        # Create likes table
        cursor_new.execute("""
            CREATE TABLE likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (post_id, user_id)
            )
        """)
        cursor_new.execute("CREATE INDEX idx_likes_post_id ON likes(post_id)")
        cursor_new.execute("CREATE INDEX idx_likes_user_id ON likes(user_id)")
        
        # Create read_events table
        cursor_new.execute("""
            CREATE TABLE read_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                percent INTEGER,
                seconds INTEGER,
                created_at DATETIME,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor_new.execute("CREATE INDEX idx_read_events_post_id ON read_events(post_id)")
        cursor_new.execute("CREATE INDEX idx_read_events_user_id ON read_events(user_id)")
        
        print("✅ New database schema created!")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn_new.close()
        return
    
    # 5. Migrate data
    print("\n📥 Step 5: Migrating data to new database...")
    
    try:
        # Migrate users
        for user in existing_users:
            cursor_new.execute("""
                INSERT INTO users (id, entra_oid, email, name, last_login_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user['id'], user['entra_oid'], user['email'], user['name'], 
                  user['last_login_at'], user['created_at']))
        
        # Migrate posts (adding is_featured = 0)
        for post in existing_posts:
            cursor_new.execute("""
                INSERT INTO posts (id, slug, title, month_key, published_at, updated_at, created_at,
                                 status, is_featured, hero_image_path, html_content, excerpt, 
                                 category, read_time, related_posts_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?)
            """, (post['id'], post['slug'], post['title'], post['month_key'], 
                  post['published_at'], post['updated_at'], post['created_at'],
                  post['status'], post['hero_image_path'], post['html_content'],
                  post['excerpt'], post['category'], post['read_time'], 
                  post.get('related_posts_json')))
        
        # Migrate comments
        for comment in existing_comments:
            cursor_new.execute("""
                INSERT INTO comments (id, post_id, user_id, body, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (comment['id'], comment['post_id'], comment['user_id'], 
                  comment['body'], comment['created_at']))
        
        # Migrate likes
        for like in existing_likes:
            cursor_new.execute("""
                INSERT INTO likes (id, post_id, user_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (like['id'], like['post_id'], like['user_id'], like['created_at']))
        
        # Migrate read_events
        for event in existing_read_events:
            cursor_new.execute("""
                INSERT INTO read_events (id, post_id, user_id, percent, seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event['id'], event['post_id'], event['user_id'], 
                  event['percent'], event['seconds'], event['created_at']))
        
        conn_new.commit()
        print(f"✅ Data migrated successfully!")
        print(f"   - {len(existing_users)} users")
        print(f"   - {len(existing_posts)} posts")
        print(f"   - {len(existing_comments)} comments")
        print(f"   - {len(existing_likes)} likes")
        print(f"   - {len(existing_read_events)} read events")
        
    except Exception as e:
        print(f"❌ Error migrating data: {e}")
        import traceback
        traceback.print_exc()
        conn_new.rollback()
        conn_new.close()
        return
    
    # 6. Verify
    print("\n✅ Step 6: Verifying new database...")
    cursor_new.execute("PRAGMA table_info(posts)")
    columns = [col[1] for col in cursor_new.fetchall()]
    print(f"Posts table columns: {', '.join(columns)}")
    
    if 'is_featured' in columns:
        print("✅ is_featured column exists!")
        
        cursor_new.execute("SELECT id, title, is_featured FROM posts")
        posts = cursor_new.fetchall()
        print(f"\n📝 Posts in new database:")
        for post_id, title, is_featured in posts:
            status = "⭐ FEATURED" if is_featured else "Not featured"
            print(f"   {post_id}. {title[:60]} - {status}")
    else:
        print("❌ is_featured column is MISSING!")
    
    conn_new.close()
    
    print("\n🎉 Database recreation complete!")
    print("   You can now restart Flask and the featured column will work.")

if __name__ == '__main__':
    recreate_database()

