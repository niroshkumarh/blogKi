"""
Initialize PostgreSQL database with correct schema
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
from app import app, db
from models import User, Post, Comment, Like, ReadEvent

def init_database():
    """Initialize PostgreSQL database"""
    print("🏗️  Initializing PostgreSQL database...")
    
    with app.app_context():
        try:
            # Drop all tables if they exist (for clean setup)
            print("Dropping existing tables (if any)...")
            db.drop_all()
            
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            
            # Create sessions table for Flask-Session
            print("Creating sessions table for Flask-Session...")
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
            
            print(f"\n✅ Database initialized successfully!")
            print(f"📋 Created tables: {', '.join(tables)}")
            
            # Show posts table schema
            if 'posts' in tables:
                columns = inspector.get_columns('posts')
                print(f"\n📝 Posts table columns:")
                for col in columns:
                    print(f"   - {col['name']} ({col['type']})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)

