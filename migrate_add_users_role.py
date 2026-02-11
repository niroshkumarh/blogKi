"""
Migration script to add role column to users table.
Required for User model (admin, editor, viewer). Safe to re-run.
"""
from app import app
from models import db
from sqlalchemy import text


def migrate():
    with app.app_context():
        try:
            r = db.session.execute(
                text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'role'
                """)
            )
            if r.fetchone():
                print("✅ users.role column already exists - no action needed")
                return

            print("Adding role column to users table...")
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN role VARCHAR(20) DEFAULT 'viewer'
            """))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)"))
            db.session.commit()
            print("✅ users.role added (default: viewer)")

        except Exception as e:
            err = str(e).lower()
            if 'already exists' in err or 'duplicate column' in err:
                print("✅ users.role column already exists - no action needed")
            else:
                print(f"❌ Error: {e}")
            db.session.rollback()


if __name__ == '__main__':
    migrate()
