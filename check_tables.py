"""Check database tables"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

conn = sqlite3.connect('blogsite.db')
cursor = conn.cursor()

print("📋 All tables in database:")
print("-" * 50)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
if tables:
    for table in tables:
        print(f"  - {table[0]}")
else:
    print("  No tables found!")

conn.close()


