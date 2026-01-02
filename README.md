# Horizon Blog

A personal blog platform with Microsoft Entra ID authentication, built with Flask and SQLite.

## Features

- **Microsoft Entra ID Authentication**: Single-tenant OAuth2/OIDC login
- **Protected Content**: All blog posts require authentication to view
- **Comments & Likes**: Engage with posts through comments and likes
- **Read Analytics**: Track user reading progress, time spent, and completion rates
- **Admin Dashboard**: 
  - View statistics on post performance
  - See user engagement (views, likes, comments, read progress)
  - Manage users and their activity
- **Admin Editor**:
  - WYSIWYG editor (Quill) for creating and editing posts
  - Image upload support
  - Month-based organization
  - Publish scheduling
  - Draft and published status
- **Month-Based Archives**: Organize posts by month (YYYY-MM format)
- **Responsive Design**: Beautiful UI based on NewsBoard template

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (easy migration to PostgreSQL)
- **Auth**: Microsoft Entra ID (Azure AD) via Authlib
- **ORM**: SQLAlchemy
- **Server**: Gunicorn + Nginx (for production)
- **Frontend**: Bootstrap 4, jQuery, Quill editor

## Quick Start (Development)

### Prerequisites

- Python 3.9+
- Microsoft Entra ID app registration

### 1. Clone Repository

```bash
git clone https://github.com/niroshkumarh/blogKi.git
cd blogKi
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```env
SECRET_KEY=your-secret-key-here
CLIENT_ID=423dd38a-439a-4b99-a313-9472d2c0dad6
CLIENT_SECRET=your-client-secret-here
TENANT_ID=6b8b8296-bdff-4ad8-93ad-84bcbf3842f5
REDIRECT_URI=http://localhost:5000/auth/callback
ADMIN_EMAILS=your-email@domain.com
```

### 4. Initialize Database

```bash
python init_db.py
python migrate_posts.py  # Import existing 2 blog posts
```

### 5. Run Development Server

```bash
python app.py
```

Visit `http://localhost:5000`

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Ubuntu/Nginx deployment instructions.

## Entra ID Configuration

1. Go to Azure Portal > Azure Active Directory > App registrations
2. Create or select your app registration
3. Under "Authentication", add redirect URI: `http://YOUR_DOMAIN/auth/callback`
4. Under "Certificates & secrets", create a client secret
5. Copy Client ID, Tenant ID, and Client Secret to `.env`

## Admin Access

Admin users are defined in the `ADMIN_EMAILS` environment variable (comma-separated). Admin users can:

- Access `/admin` dashboard
- View detailed analytics per post
- Create, edit, and delete posts
- View all users and their activity
- Manage comments

## Database Schema

- **users**: Entra ID users who have logged in
- **posts**: Blog articles with metadata
- **comments**: User comments on posts
- **likes**: User likes (one per user per post)
- **read_events**: Reading progress tracking (scroll %, time spent)

## Project Structure

```
blogKi/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── auth.py                # Authentication (Entra ID OIDC)
├── api.py                 # API routes (comments, likes, read tracking)
├── admin.py               # Admin routes and dashboard
├── templates/             # Jinja2 templates
│   ├── base.html          # Base layout
│   ├── archive.html       # Month archive view
│   ├── post.html          # Single post view
│   └── admin/             # Admin templates
├── assets/                # Static files (CSS, JS, images)
├── uploads/               # User-uploaded images
├── init_db.py             # Database initialization
├── migrate_posts.py       # Import existing posts
├── requirements.txt       # Python dependencies
├── DEPLOYMENT.md          # Production deployment guide
└── README.md              # This file
```

## Security Notes

- **Never commit `.env` file or secrets**
- Client secret should be rotated regularly in Azure Portal
- Use HTTPS in production
- SQLite file should have restricted permissions
- Admin emails should be limited to trusted users

## Future Enhancements

- Migrate to PostgreSQL for better concurrency
- Add full-text search across posts
- Email notifications for comments
- Export analytics to CSV
- Mobile app integration via API

## License

Private project - all rights reserved.

## Contact

For questions or issues, contact the admin via the configured admin email.


