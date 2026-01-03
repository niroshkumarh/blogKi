"""
Migration script to add nested comments support and comment likes
Adds:
- parent_id column to comments table (for nested replies)
- comment_likes table (for liking comments)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app, db
from sqlalchemy import text

def migrate_nested_comments():
    print("🔄 Migrating database for nested comments and comment likes...")
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            
            # Check if parent_id column exists in comments table
            comments_columns = [col['name'] for col in inspector.get_columns('comments')]
            
            if 'parent_id' not in comments_columns:
                print("📝 Adding parent_id column to comments table...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE comments ADD COLUMN parent_id INTEGER"))
                    conn.execute(text("CREATE INDEX ix_comments_parent_id ON comments(parent_id)"))
                    conn.execute(text("ALTER TABLE comments ADD CONSTRAINT fk_comments_parent_id FOREIGN KEY(parent_id) REFERENCES comments(id) ON DELETE CASCADE"))
                    conn.commit()
                print("✅ parent_id column added to comments table")
            else:
                print("⚠️  parent_id column already exists in comments table")
            
            # Check if comment_likes table exists
            existing_tables = inspector.get_table_names()
            
            if 'comment_likes' not in existing_tables:
                print("📝 Creating comment_likes table...")
                with db.engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE comment_likes (
                            id SERIAL PRIMARY KEY,
                            comment_id INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT fk_comment_likes_comment_id FOREIGN KEY(comment_id) REFERENCES comments(id) ON DELETE CASCADE,
                            CONSTRAINT fk_comment_likes_user_id FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                            CONSTRAINT unique_comment_user_like UNIQUE(comment_id, user_id)
                        )
                    """))
                    conn.execute(text("CREATE INDEX ix_comment_likes_comment_id ON comment_likes(comment_id)"))
                    conn.execute(text("CREATE INDEX ix_comment_likes_user_id ON comment_likes(user_id)"))
                    conn.commit()
                print("✅ comment_likes table created")
            else:
                print("⚠️  comment_likes table already exists")
            
            print("\n✅ Migration complete! Nested comments and comment likes are now enabled.")
            print("   📌 Users can now reply to comments")
            print("   ❤️  Users can now like comments")
            return True
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False

if __name__ == '__main__':
    success = migrate_nested_comments()
    sys.exit(0 if success else 1)

