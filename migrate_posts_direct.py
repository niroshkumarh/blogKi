"""Migrate posts using raw SQL"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
from datetime import datetime

conn = sqlite3.connect('blogsite.db')
cursor = conn.cursor()

# Post 1 data
post1 = {
    'slug': 'aravind-srinivas-perplexity-ai',
    'title': 'A Video I Watched: Aravind Srinivas on AI and Curiosity',
    'month_key': '2026-01',
    'published_at': '2026-01-01 12:00:00',
    'status': 'published',
    'hero_image_path': '/Aravind_Srinivas_TC_Day_3.jpg',
    'excerpt': 'How AI can extend the boundaries of human thought',
    'category': 'A Video I Watched',
    'read_time': 6
}

post1['html_content'] = '''
<p>Artificial Intelligence has become one of those subjects everyone has an opinion on - but very few speak about it with the clarity and balance that Aravind Srinivas does. I watched his recent conversation where he spoke not as a technologist selling the future, but as a thinker questioning how we'll live with it.</p>

<p>Aravind, the founder of Perplexity AI, comes across as calm, analytical, and deeply human in his approach. He doesn't glorify AI, nor does he fear it. His central point is simple: AI is not the end of human reasoning - it's an amplifier of it.</p>

<p>What he proposes is a shift in how we see the relationship between knowledge and technology. For years, we've treated information as power. But in this new phase, information is abundant; the ability to interpret it is the real advantage.</p>

<blockquote>
    <p>"AI should make humans more curious, not less."</p>
</blockquote>

<p>That line almost defines our time. It's not about what AI can do; it's about what it can make us want to learn.</p>

<h2>What the video tries to convey</h2>

<p><strong>AI as a thinking partner.</strong> Aravind frames AI not as an answer machine but as a reasoning collaborator. It doesn't give final truths, but possibilities to explore.</p>

<p><strong>From knowledge to inquiry.</strong> The focus shifts from storing data to constructing meaning. It's not "what do I know," but "what am I trying to understand."</p>

<p><strong>The ethics of dependency.</strong> If AI makes things easy, we risk losing the muscle of curiosity. The challenge is to use it consciously - to learn through it, not lean on it.</p>

<hr class="section-divider">

<p>I found this perspective valuable because it doesn't fall into either camp - the hype or the hysteria. It's grounded. And that's what I needed.</p>

<p>If you're interested, the full interview is available on YouTube. Worth your time if you're thinking about how technology might shape not just what we do, but how we think.</p>
'''

# Post 2 data
post2 = {
    'slug': 'vikram-arochamy-systems-thinking',
    'title': 'With Vikram Arochamy: Building systems that think',
    'month_key': '2026-01',
    'published_at': '2026-01-01 12:00:00',
    'status': 'published',
    'hero_image_path': '/Artcile 2.jpg',
    'excerpt': 'HORIZON',
    'category': 'A Picture I Took',
    'read_time': 5
}

post2['html_content'] = '''
<p>I had the chance to spend an afternoon with Vikram Arochamy, someone whose work sits at the intersection of software engineering and cognitive systems. He doesn't talk much about what he does - but when he does, it's layered, thoughtful, and unusually clear.</p>

<p>Our conversation began with a simple question: what does it mean to build intelligent systems today?</p>

<p>His answer wasn't technical. It was philosophical.</p>

<blockquote>
    <p>"We're not building intelligence. We're building responses. The real challenge is making those responses contextual, adaptive, and ethical."</p>
</blockquote>

<h2>Context over computation</h2>

<p>Vikram emphasized something that often gets overlooked in tech discussions - context. Systems can be fast, accurate, and scalable. But if they don't understand context, they fail where it matters most: in the human experience.</p>

<p>He shared an example from his work - a recommendation system that technically worked but felt "off" to users. The problem wasn't the algorithm. It was that the system didn't account for intent, mood, or timing.</p>

<p><strong>Technical correctness ≠ user relevance.</strong></p>

<h2>Designing for uncertainty</h2>

<p>One of the ideas that stood out: designing systems that can handle uncertainty gracefully. Not systems that try to eliminate ambiguity, but ones that can work within it.</p>

<p>He mentioned working with models that don't just predict outcomes but assess confidence levels, adapt based on new information, and communicate their limitations clearly.</p>

<p>"If a system knows it doesn't know something, it should say so," he said. Simple, but rarely implemented.</p>

<hr class="section-divider">

<p>Vikram's approach reminded me that the best technology doesn't impose itself. It adapts. It listens. It serves.</p>

<p>This conversation shaped how I think about the tools we build and the assumptions we embed in them. Worth reflecting on.</p>
'''

# Check if posts already exist
cursor.execute("SELECT COUNT(*) FROM posts WHERE slug IN (?, ?)", (post1['slug'], post2['slug']))
if cursor.fetchone()[0] > 0:
    print("⚠️  Posts already exist. Skipping migration.")
    conn.close()
    sys.exit(0)

print("📝 Adding post 1: Aravind Srinivas...")
cursor.execute('''
    INSERT INTO posts (slug, title, month_key, published_at, created_at, status, hero_image_path, html_content, excerpt, category, read_time, related_posts_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
''', (
    post1['slug'],
    post1['title'],
    post1['month_key'],
    post1['published_at'],
    datetime.utcnow().isoformat(),
    post1['status'],
    post1['hero_image_path'],
    post1['html_content'],
    post1['excerpt'],
    post1['category'],
    post1['read_time']
))

print("📝 Adding post 2: Vikram Arochamy...")
cursor.execute('''
    INSERT INTO posts (slug, title, month_key, published_at, created_at, status, hero_image_path, html_content, excerpt, category, read_time, related_posts_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
''', (
    post2['slug'],
    post2['title'],
    post2['month_key'],
    post2['published_at'],
    datetime.utcnow().isoformat(),
    post2['status'],
    post2['hero_image_path'],
    post2['html_content'],
    post2['excerpt'],
    post2['category'],
    post2['read_time']
))

conn.commit()
conn.close()

print()
print("✅ Posts migrated successfully!")
print()
print("You can now restart the Flask app and test:")
print("  python app.py")


