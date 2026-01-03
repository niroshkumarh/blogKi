"""
Migration script to add anonymous tracking fields to read_events table
Adds: anon_id, ip_address, user_agent columns and makes user_id nullable
Run this once to update existing database
Works with PostgreSQL
"""
from app import app
from models import db
from sqlalchemy import text, inspect

def migrate_read_events_anonymous():
    with app.app_context():
        try:
            print("🔄 Migrating read_events table for anonymous tracking...")
            
            # Get existing columns
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('read_events')]
            print(f"📋 Existing columns: {columns}")
            
            # Make user_id nullable (PostgreSQL syntax)
            print("1️⃣ Making user_id nullable...")
            try:
                db.session.execute(text("ALTER TABLE read_events ALTER COLUMN user_id DROP NOT NULL"))
                db.session.commit()
                print("✅ user_id is now nullable")
            except Exception as e:
                if 'does not exist' in str(e).lower():
                    print("✅ user_id already nullable or constraint doesn't exist")
                else:
                    print(f"⚠️ Warning making user_id nullable: {e}")
                db.session.rollback()
            
            # Add anon_id column
            if 'anon_id' not in columns:
                print("2️⃣ Adding anon_id column...")
                db.session.execute(text("ALTER TABLE read_events ADD COLUMN anon_id VARCHAR(255)"))
                db.session.execute(text("CREATE INDEX ix_read_events_anon_id ON read_events(anon_id)"))
                db.session.commit()
                print("✅ anon_id column added with index")
            else:
                print("✅ anon_id column already exists")
            
            # Add ip_address column
            if 'ip_address' not in columns:
                print("3️⃣ Adding ip_address column...")
                db.session.execute(text("ALTER TABLE read_events ADD COLUMN ip_address VARCHAR(45)"))
                db.session.execute(text("CREATE INDEX ix_read_events_ip_address ON read_events(ip_address)"))
                db.session.commit()
                print("✅ ip_address column added with index")
            else:
                print("✅ ip_address column already exists")
            
            # Add user_agent column
            if 'user_agent' not in columns:
                print("4️⃣ Adding user_agent column...")
                db.session.execute(text("ALTER TABLE read_events ADD COLUMN user_agent VARCHAR(500)"))
                db.session.commit()
                print("✅ user_agent column added")
            else:
                print("✅ user_agent column already exists")
            
            print("\n🎉 Migration completed successfully!")
            print("📊 read_events table now supports anonymous tracking")
            print("   - user_id is nullable")
            print("   - anon_id, ip_address, user_agent columns added")
            print("   - Indexes created for anon_id and ip_address")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_read_events_anonymous()

