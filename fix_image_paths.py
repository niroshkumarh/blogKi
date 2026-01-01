"""Fix image paths with backslashes"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app, db
from models import Post

with app.app_context():
    posts = Post.query.all()
    
    for post in posts:
        if post.hero_image_path and '\\' in post.hero_image_path:
            old_path = post.hero_image_path
            new_path = post.hero_image_path.replace('\\', '/')
            post.hero_image_path = new_path
            print(f"Fixed: {post.title}")
            print(f"  Old: {old_path}")
            print(f"  New: {new_path}")
    
    db.session.commit()
    print("\n✅ All image paths fixed!")

