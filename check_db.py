"""Check database structure"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

conn = sqlite3.connect('blogsite.db')
cursor = conn.cursor()

print("📋 Posts table columns:")
print("-" * 50)
cursor.execute("PRAGMA table_info(posts)")
for col in cursor.fetchall():
    print(f"  {col[1]}: {col[2]}")

conn.close()
