"""
Migration script to add PreRelease user group and Month Visibility features.
Adds:
- role column to users table (default: 'user')
- month_visibility table
- Seeds existing months as specified visibility
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app, db
from sqlalchemy import text

def migrate():
    print("🔄 Migrating database for PreRelease and Month Visibility...")
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)

            # 1. Add role column to users table
            users_columns = [col['name'] for col in inspector.get_columns('users')]

            if 'role' not in users_columns:
                print("📝 Adding role column to users table...")
                with db.engine.connect() as conn:
                    conn.execute(text(
                        "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"
                    ))
                    conn.commit()
                print("✅ role column added to users table")
            else:
                print("⚠️  role column already exists in users table")

            # 2. Create month_visibility table
            existing_tables = inspector.get_table_names()

            if 'month_visibility' not in existing_tables:
                print("📝 Creating month_visibility table...")
                with db.engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE month_visibility (
                            id SERIAL PRIMARY KEY,
                            month_key VARCHAR(7) NOT NULL UNIQUE,
                            visibility VARCHAR(20) DEFAULT 'prerelease' NOT NULL,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.execute(text(
                        "CREATE INDEX ix_month_visibility_month_key ON month_visibility(month_key)"
                    ))
                    conn.commit()
                print("✅ month_visibility table created")

                # Seed specific months as public
                print("📝 Seeding months as public: 2025-12, 2026-01, 2026-02...")
                with db.engine.connect() as conn:
                    for mk in ['2025-12', '2026-01', '2026-02']:
                        conn.execute(text(
                            "INSERT INTO month_visibility (month_key, visibility) "
                            "VALUES (:mk, 'public') ON CONFLICT (month_key) DO NOTHING"
                        ), {'mk': mk})
                    conn.commit()
                print("✅ Months seeded as public")
            else:
                print("⚠️  month_visibility table already exists")

            print("\n✅ Migration complete! PreRelease and Month Visibility features are now enabled.")
            print("   👥 Users can be assigned 'prerelease' role")
            print("   📅 Month visibility can be controlled (public/prerelease)")
            return True

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
