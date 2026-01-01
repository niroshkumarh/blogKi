"""
Initialize database tables - Fresh version
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("Database Initialization")
print("=" * 60)
print()

print("📝 Step 1: Importing app and models...")
from app import app, db
from models import User, Post, Comment, Like, ReadEvent

print("✅ Imports successful!")
print()

print("📝 Step 2: Creating database tables...")
with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Tables created!")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print()
    print("📋 Created tables:")
    for table in tables:
        print(f"  - {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"      {col['name']}: {col['type']}")
    
    print()
    print(f"✅ Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

print()
print("=" * 60)
print("✅ Database initialization complete!")
print("=" * 60)

