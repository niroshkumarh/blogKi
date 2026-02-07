"""
Migration: Add audit tracking fields to all content types
- created_by_id, updated_by_id for Posts, Audio, Series, Videos, Podcasts
- role field for Users (admin, editor, viewer)
"""
from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    print("Adding audit tracking fields...")
    
    try:
        # Add role to users table
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'viewer';
        """))
        print("✓ Added role to users")
        
        # Add audit fields to posts
        db.session.execute(text("""
            ALTER TABLE posts 
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER REFERENCES users(id),
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER REFERENCES users(id);
        """))
        print("✓ Added audit fields to posts")
        
        # Add audit fields to audio_episodes
        db.session.execute(text("""
            ALTER TABLE audio_episodes 
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER REFERENCES users(id),
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER REFERENCES users(id);
        """))
        print("✓ Added audit fields to audio_episodes")
        
        # Add audit fields to series
        db.session.execute(text("""
            ALTER TABLE series 
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER REFERENCES users(id),
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER REFERENCES users(id);
        """))
        print("✓ Added audit fields to series")
        
        # Add audit fields to videos
        db.session.execute(text("""
            ALTER TABLE videos 
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER REFERENCES users(id),
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER REFERENCES users(id);
        """))
        print("✓ Added audit fields to videos")
        
        # Add audit fields to podcasts
        db.session.execute(text("""
            ALTER TABLE podcasts 
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER REFERENCES users(id),
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER REFERENCES users(id);
        """))
        print("✓ Added audit fields to podcasts")
        
        db.session.commit()
        print("\n✅ All audit tracking fields added successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error: {e}")
        raise
