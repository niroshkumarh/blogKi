"""
Verification script to test Flask app imports and basic functionality
"""
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("✓ Flask-SQLAlchemy imported")
    except ImportError as e:
        print(f"✗ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        from authlib.integrations.flask_client import OAuth
        print("✓ Authlib imported")
    except ImportError as e:
        print(f"✗ Authlib import failed: {e}")
        return False
    
    try:
        import models
        print("✓ models.py imported")
    except Exception as e:
        print(f"✗ models.py import failed: {e}")
        return False
    
    try:
        import auth
        print("✓ auth.py imported")
    except Exception as e:
        print(f"✗ auth.py import failed: {e}")
        return False
    
    try:
        import api
        print("✓ api.py imported")
    except Exception as e:
        print(f"✗ api.py import failed: {e}")
        return False
    
    try:
        import admin
        print("✓ admin.py imported")
    except Exception as e:
        print(f"✗ admin.py import failed: {e}")
        return False
    
    try:
        import app as main_app
        print("✓ app.py imported")
    except Exception as e:
        print(f"✗ app.py import failed: {e}")
        return False
    
    return True


def test_app_context():
    """Test app context and database"""
    print("\n🔍 Testing app context...")
    
    try:
        from app import app, db
        from models import User, Post, Comment, Like, ReadEvent
        
        with app.app_context():
            print("✓ App context created")
            print(f"✓ Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"✓ Models loaded: User, Post, Comment, Like, ReadEvent")
        
        return True
    except Exception as e:
        print(f"✗ App context test failed: {e}")
        return False


def test_blueprints():
    """Test blueprint registration"""
    print("\n🔍 Testing blueprints...")
    
    try:
        from app import app
        
        blueprints = list(app.blueprints.keys())
        print(f"✓ Registered blueprints: {', '.join(blueprints)}")
        
        expected = ['auth', 'api', 'admin']
        for bp in expected:
            if bp in blueprints:
                print(f"  ✓ {bp} blueprint registered")
            else:
                print(f"  ✗ {bp} blueprint NOT registered")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Blueprint test failed: {e}")
        return False


def test_routes():
    """Test route registration"""
    print("\n🔍 Testing routes...")
    
    try:
        from app import app
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        expected_routes = [
            '/',
            '/archive/<month_key>',
            '/post/<slug>',
            '/auth/login',
            '/auth/callback',
            '/auth/logout',
            '/admin/',
            '/admin/posts',
            '/admin/posts/new',
            '/api/like/<int:post_id>',
            '/api/comment/<int:post_id>',
        ]
        
        for route in expected_routes:
            found = any(route in r for r in routes)
            if found:
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} NOT FOUND")
        
        return True
    except Exception as e:
        print(f"✗ Route test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Wide Angle Blog - Verification Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_app_context,
        test_blueprints,
        test_routes
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Application is ready.")
        print("\nNext steps:")
        print("1. Create .env file from .env.example")
        print("2. Add your Entra ID credentials")
        print("3. Run: python init_db.py")
        print("4. Run: python migrate_posts.py")
        print("5. Run: python app.py")
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    main()

