"""
Initialize PostgreSQL database with FRESH START (DROPS ALL DATA!)
⚠️  WARNING: This script will DELETE ALL YOUR DATA!
⚠️  Only use this when you want to completely reset the database!
⚠️  For normal startup, use init_db_postgres.py instead

Usage: docker exec blogki-web python init_db_postgres_FRESH.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
from app import app, db
from models import User, Post, Comment, Like, ReadEvent

def fresh_init_database():
    """Initialize PostgreSQL database with FRESH START - DROPS ALL DATA!"""
    print("⚠️  ⚠️  ⚠️  WARNING: FRESH DATABASE INITIALIZATION ⚠️  ⚠️  ⚠️")
    print("⚠️  This will DELETE ALL DATA in the database!")
    print("⚠️  Press Ctrl+C to cancel within 5 seconds...")
    
    import time
    time.sleep(5)
    
    print("\n🏗️  Starting FRESH database initialization...")
    
    with app.app_context():
        try:
            # Drop all tables
            print("🗑️  Dropping ALL existing tables...")
            db.drop_all()
            
            # Create all tables
            print("📝 Creating fresh database tables...")
            db.create_all()
            
            # Create sessions table for Flask-Session
            print("📝 Creating sessions table...")
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) UNIQUE NOT NULL,
                        data BYTEA,
                        expiry TIMESTAMP
                    )
                """))
                conn.commit()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n✅ Fresh database initialized successfully!")
            print(f"📋 Created tables: {', '.join(tables)}")
            
            # Show post table schema
            if 'post' in tables:
                columns = inspector.get_columns('post')
                print(f"\n📝 Post table columns:")
                for col in columns:
                    print(f"   - {col['name']} ({col['type']})")
            
            print("\n⚠️  All previous data has been deleted!")
            print("💡 You can now add new posts via Admin panel")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fresh_init_database()
    sys.exit(0 if success else 1)

