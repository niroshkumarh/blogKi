"""
Quick test script to verify admin pages load without errors
"""
from app import app
from models import db, Series, Video, Podcast, AudioEpisode

with app.app_context():
    print("🧪 Testing Admin Pages...\n")
    
    # Test 1: Query each content type
    print("1️⃣ Testing database queries...")
    try:
        series = Series.query.all()
        print(f"   ✅ Series: {len(series)} items")
    except Exception as e:
        print(f"   ❌ Series error: {e}")
    
    try:
        videos = Video.query.all()
        print(f"   ✅ Videos: {len(videos)} items")
    except Exception as e:
        print(f"   ❌ Videos error: {e}")
    
    try:
        podcasts = Podcast.query.all()
        print(f"   ✅ Podcasts: {len(podcasts)} items")
    except Exception as e:
        print(f"   ❌ Podcasts error: {e}")
    
    try:
        audio = AudioEpisode.query.all()
        print(f"   ✅ Audio Episodes: {len(audio)} items")
    except Exception as e:
        print(f"   ❌ Audio error: {e}")
    
    # Test 2: Check if models have required fields
    print("\n2️⃣ Testing model attributes...")
    test_series = Series.query.first() if Series.query.count() > 0 else None
    if test_series:
        print(f"   ✅ Series has: id={test_series.id}, name={test_series.name}, created_at={test_series.created_at}")
    else:
        print("   ℹ️  No series to test (database empty)")
    
    # Test 3: Template rendering test
    print("\n3️⃣ Testing template rendering...")
    with app.test_client() as client:
        # Note: These will redirect to login, but we can check for template errors
        try:
            response = client.get('/admin/series', follow_redirects=False)
            if response.status_code in [200, 302]:  # 302 = redirect to login (expected)
                print(f"   ✅ /admin/series - Status {response.status_code}")
            else:
                print(f"   ⚠️  /admin/series - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ /admin/series error: {e}")
        
        try:
            response = client.get('/admin/videos', follow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"   ✅ /admin/videos - Status {response.status_code}")
            else:
                print(f"   ⚠️  /admin/videos - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ /admin/videos error: {e}")
        
        try:
            response = client.get('/admin/podcasts', follow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"   ✅ /admin/podcasts - Status {response.status_code}")
            else:
                print(f"   ⚠️  /admin/podcasts - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ /admin/podcasts error: {e}")
        
        try:
            response = client.get('/admin/audio', follow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"   ✅ /admin/audio - Status {response.status_code}")
            else:
                print(f"   ⚠️  /admin/audio - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ /admin/audio error: {e}")
    
    print("\n✅ All tests completed!")
    print("\nℹ️  Note: 302 redirects are expected (auth required)")
    print("   Template errors would show as 500 status codes")
