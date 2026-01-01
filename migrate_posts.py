"""
Migrate existing blog posts from HTML files to database
"""
from datetime import datetime
from app import app, db
from models import Post


def migrate_posts():
    """Migrate existing HTML blog posts to database"""
    with app.app_context():
        # Blog post 1: Aravind Srinivas
        post1_data = {
            'slug': 'aravind-srinivas-perplexity-ai',
            'title': 'The Startup Story of Perplexity AI - Aravind Srinivas at TC Day 3',
            'month_key': '2026-01',
            'status': 'published',
            'published_at': datetime(2026, 1, 15, 10, 0),
            'html_content': '''
            <h2>My Reflection on Watching Aravind Srinivas at TechCrunch Day 3</h2>
            <p>I recently watched an incredible conversation with Aravind Srinivas, the founder and CEO of Perplexity AI, at TechCrunch Disrupt Day 3. It was one of those moments that makes you pause and reflect on the journey of building something meaningful.</p>
            
            <h3>What Struck Me Most</h3>
            <p>Aravind's story resonated deeply because it wasn't about overnight success or lucky breaks. It was about persistence, curiosity, and an unwavering belief in solving real problems. Perplexity AI emerged from his desire to make information discovery more intuitive and conversational.</p>
            
            <h3>Key Takeaways</h3>
            <ul>
                <li><strong>Start with the problem, not the technology</strong> - Aravind emphasized that Perplexity wasn't built to showcase AI capabilities, but to solve the friction in how people search for and discover information.</li>
                <li><strong>Iterate relentlessly</strong> - The path from idea to product-market fit involved countless iterations and user feedback cycles.</li>
                <li><strong>Stay curious</strong> - His background in AI research at OpenAI and DeepMind shaped his approach, but it was curiosity that drove innovation.</li>
            </ul>
            
            <h3>Why This Matters to Me</h3>
            <p>As I think about building products and creating value, Aravind's journey reminds me that the best companies are born from genuine frustrations and a commitment to making things better. It's not about chasing trends—it's about finding problems worth solving.</p>
            
            <blockquote>
                <p>"The best products come from founders who are solving their own problems."</p>
            </blockquote>
            
            <p>This conversation left me inspired to stay focused on real problems, embrace iteration, and never stop learning. The future belongs to those who stay curious and committed.</p>
            ''',
            'excerpt': 'Reflections on Aravind Srinivas startup journey with Perplexity AI and what it teaches us about building meaningful products.',
            'category': 'A Video I Watched',
            'read_time': 5,
            'hero_image_path': '/assets/imgs/news/news-1.jpg'
        }
        
        # Blog post 2: Vikram Arochamy
        post2_data = {
            'slug': 'vikram-arochamy-amazon-innovation',
            'title': 'Innovation at Scale: Learning from Vikram Arochamy (Amazon)',
            'month_key': '2026-01',
            'status': 'published',
            'published_at': datetime(2026, 1, 20, 14, 30),
            'html_content': '''
            <h2>A Conversation That Changed My Perspective</h2>
            <p>I had the opportunity to attend a talk by Vikram Arochamy from Amazon, where he shared insights on scaling innovation within one of the world's most customer-obsessed companies.</p>
            
            <h3>The Amazon Philosophy</h3>
            <p>What stood out was not the scale of Amazon, but the principles that drive every decision. Vikram walked us through how Amazon thinks about innovation, experimentation, and long-term thinking.</p>
            
            <h3>Key Principles I am Taking Away</h3>
            <ul>
                <li><strong>Customer obsession over competition</strong> - Amazon doesn't start by asking "what are competitors doing?" They ask "what do customers need?"</li>
                <li><strong>Bias for action</strong> - Speed matters. Making reversible decisions quickly is better than waiting for perfect information.</li>
                <li><strong>Think big, start small</strong> - Bold visions need to be broken down into executable experiments.</li>
                <li><strong>Embrace failure as learning</strong> - Failed experiments are just data points that inform the next iteration.</li>
            </ul>
            
            <h3>What Resonated Most</h3>
            <p>Vikram shared a story about a project that failed spectacularly but led to insights that shaped a successful product years later. It reminded me that innovation isn't linear—it's messy, iterative, and often requires patience.</p>
            
            <blockquote>
                <p>"We are willing to be misunderstood for long periods of time."</p>
                <cite>— Jeff Bezos (quoted during the talk)</cite>
            </blockquote>
            
            <h3>My Reflection</h3>
            <p>Listening to Vikram reinforced my belief that great companies aren't built on ideas alone—they're built on principles, discipline, and a willingness to experiment. The best teams create environments where failure is safe, learning is valued, and customers are at the center of every decision.</p>
            
            <p>I'm inspired to bring more of this mindset into my own work: start with the customer, move fast, learn from failures, and think long-term.</p>
            ''',
            'excerpt': 'Insights from Vikram Arochamy on how Amazon scales innovation through customer obsession and experimentation.',
            'category': 'A Conversation I Had',
            'read_time': 6,
            'hero_image_path': '/assets/imgs/news/news-2.jpg'
        }
        
        # Check if posts already exist
        existing1 = Post.query.filter_by(slug=post1_data['slug']).first()
        existing2 = Post.query.filter_by(slug=post2_data['slug']).first()
        
        if not existing1:
            post1 = Post(**post1_data)
            db.session.add(post1)
            print(f"✓ Created post: {post1_data['title']}")
        else:
            print(f"- Post already exists: {post1_data['title']}")
        
        if not existing2:
            post2 = Post(**post2_data)
            db.session.add(post2)
            print(f"✓ Created post: {post2_data['title']}")
        else:
            print(f"- Post already exists: {post2_data['title']}")
        
        db.session.commit()
        print("\n✓ Migration complete!")


if __name__ == '__main__':
    migrate_posts()

