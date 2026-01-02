"""Fix database by adding missing column"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

print("🔧 Adding missing column to database...")
print()

conn = sqlite3.connect('blogsite.db')
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

# Verify
print()
print("📋 Final posts table structure:")
cursor.execute("PRAGMA table_info(posts)")
for col in cursor.fetchall():
    print(f"  - {col[1]}: {col[2]}")

conn.close()

print()
print("✅ Database fixed! You can now restart the Flask app.")


