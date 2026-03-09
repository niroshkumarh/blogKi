# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HORIZON Blog is a Flask-based internal blog platform with Microsoft Entra ID (Azure AD) single-tenant authentication. All content requires login. Posts are organized by month (`YYYY-MM` format). The frontend is based on the NewsBoard Bootstrap 4 template with Quill WYSIWYG editor for admin post creation.

## Development Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run dev server (defaults to port 5000, configurable via FLASK_PORT env var)
python app.py

# Run with Docker (uses PostgreSQL, exposes port 4343)
docker-compose up --build

# Initialize database
python init_db.py

# Run migrations (order matters)
python init_db_postgres.py
python migrate_add_featured_column.py
python migrate_nested_comments.py
python migrate_read_events_anonymous.py
python migrate_posts.py

# Run tests (these are standalone scripts, not pytest)
python test_export_import.py
python test_full_export_import.py
```

## Architecture

### Core Application Files

- **`app.py`** - Flask app factory, route definitions (`/`, `/archive/<month_key>`, `/post/<slug>`), template filters, error handlers. Configures ProxyFix for reverse proxy support. `db` is imported from `models.py`.
- **`models.py`** - SQLAlchemy models and `db` instance. Models: `User`, `Post`, `Comment` (supports nested replies via `parent_id`), `Like`, `CommentLike`, `ReadEvent` (supports both logged-in and anonymous tracking via `anon_id`).
- **`auth.py`** - Blueprint (`auth_bp`, prefix `/auth`). Entra ID OIDC via Authlib. Provides `login_required` and `admin_required` decorators. Dynamic redirect URI for multi-domain support.
- **`api.py`** - Blueprint (`api_bp`, prefix `/api`). REST endpoints for comments, likes, read tracking, and link previews. Includes SSRF protection for link preview fetching.
- **`admin.py`** - Blueprint (`admin_bp`, prefix `/admin`). Dashboard, post CRUD with Quill editor, analytics, user management, Excel export/import with base64 image support.
- **`config.py`** - Configuration classes (not directly used by `app.py` which configures inline from env vars).

### Key Patterns

- **Auth flow**: Session-based. `session['user_id']` holds the logged-in user ID. Admin check compares `user.email` against `ADMIN_EMAILS` env var list.
- **Database**: SQLite locally (`sqlite:///blogsite.db`), PostgreSQL in Docker. The `DATABASE_URL` env var controls which is used. The `postgres://` → `postgresql://` rewrite is handled in `app.py`.
- **Static files**: Served from `assets/` folder (mapped to `/assets` URL path). Uploaded images go to `uploads/`.
- **Templates**: Jinja2 in `templates/`. Public-facing pages extend `templates/base.html`. Admin pages extend `templates/admin/base.html`. The `post.html` template uses `{% block extra_js %}` for page-specific JavaScript.
- **Featured posts**: Posts with `is_featured=True` appear in the archive page carousel.

### Environment Variables

Defined in `.env` (gitignored but currently tracked — contains secrets):
- `SECRET_KEY`, `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` - Entra ID OAuth config
- `REDIRECT_URI` - OAuth callback URL
- `ADMIN_EMAILS` - Comma-separated admin email addresses
- `DATABASE_URL` - Database connection string
- `FLASK_ENV` - `development` or `production` (controls cookie security, URL scheme)
- `FLASK_PORT` - Server port (default 5000)

### Docker Setup

`docker-compose.yml` runs two services:
- `db`: PostgreSQL 16 on port 4345 (mapped from 5432)
- `web`: Flask app on port 4343, runs migrations automatically on startup

## Conventions

- Post slugs are URL-safe unique identifiers for posts
- Month keys use `YYYY-MM` format (e.g., `2026-01`)
- All datetime values use UTC via `datetime.now(timezone.utc)`
- Migration scripts are standalone Python files (no Alembic workflow despite it being in requirements)
- The `.env` file is listed in `.gitignore` but is currently committed — avoid committing secret changes
