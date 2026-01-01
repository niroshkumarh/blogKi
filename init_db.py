"""
Initialize database tables
"""
from app import app, db

def init_database():
    """Create all database tables"""
    with app.app_context():
        # Drop all tables (use with caution!)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created successfully")
        print(f"✓ Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")


if __name__ == '__main__':
    init_database()

