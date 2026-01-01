"""Create database directly with SQL"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import os

# Remove old database if exists
if os.path.exists('blogsite.db'):
    os.remove('blogsite.db')
    print("🗑️  Removed old database")

print("📝 Creating new database...")
conn = sqlite3.connect('blogsite.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entra_oid VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255),
        last_login_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create posts table
cursor.execute('''
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug VARCHAR(255) UNIQUE NOT NULL,
        title VARCHAR(500) NOT NULL,
        month_key VARCHAR(7) NOT NULL,
        published_at DATETIME,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT 'draft',
        hero_image_path VARCHAR(500),
        html_content TEXT,
        excerpt VARCHAR(500),
        category VARCHAR(100),
        read_time INTEGER,
        related_posts_json TEXT
    )
''')

# Create comments table
cursor.execute('''
    CREATE TABLE comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create likes table
cursor.execute('''
    CREATE TABLE likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(post_id, user_id),
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create read_events table
cursor.execute('''
    CREATE TABLE read_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        percent INTEGER,
        seconds INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

conn.commit()

# Verify
print()
print("✅ Database created successfully!")
print()
print("📋 Tables created:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    print(f"  - {table[0]}")
    
print()
print("📋 Posts table structure:")
cursor.execute("PRAGMA table_info(posts)")
for col in cursor.fetchall():
    print(f"  - {col[1]}: {col[2]}")

conn.close()

import os
size = os.path.getsize('blogsite.db')
print()
print(f"✅ Database file size: {size} bytes")
print(f"✅ Database location: {os.path.abspath('blogsite.db')}")

