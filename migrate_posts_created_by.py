"""
Migration script to add created_by_id and updated_by_id columns to posts table.
Required for Post model audit tracking (who created/updated each post).
Run once; safe to re-run (skips if columns exist).
"""
from app import app
from models import db
from sqlalchemy import text


def migrate():
    with app.app_context():
        try:
            # Check existing columns (PostgreSQL)
            r = db.session.execute(
                text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'posts' AND column_name IN ('created_by_id', 'updated_by_id')
                """)
            )
            existing = {row[0] for row in r}

            if 'created_by_id' not in existing:
                print("Adding created_by_id column to posts table...")
                db.session.execute(text("""
                    ALTER TABLE posts
                    ADD COLUMN created_by_id INTEGER REFERENCES users(id)
                """))
                db.session.commit()
                print("✅ created_by_id added")
            else:
                print("✅ created_by_id column already exists - no action needed")

            if 'updated_by_id' not in existing:
                print("Adding updated_by_id column to posts table...")
                db.session.execute(text("""
                    ALTER TABLE posts
                    ADD COLUMN updated_by_id INTEGER REFERENCES users(id)
                """))
                db.session.commit()
                print("✅ updated_by_id added")
            else:
                print("✅ updated_by_id column already exists - no action needed")

        except Exception as e:
            err = str(e).lower()
            if 'already exists' in err or 'duplicate column' in err:
                print("✅ Columns already exist - no action needed")
            else:
                print(f"❌ Error: {e}")
            db.session.rollback()


if __name__ == '__main__':
    migrate()
