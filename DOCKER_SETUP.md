# 🐳 Docker Setup Guide for Wide Angle Blog

This guide will help you run the Wide Angle Blog using Docker and PostgreSQL.

---

## 📋 Prerequisites

- Docker Desktop installed (Windows/Mac) or Docker + Docker Compose (Linux)
- Your Microsoft Entra ID credentials (CLIENT_ID, CLIENT_SECRET, TENANT_ID)
- At least 2GB of free disk space

---

## 🚀 Quick Start

### 1. Configure Environment Variables

Copy the example environment file and update it with your credentials:

```bash
# Copy the example file
cp env.docker.example .env

# Edit .env with your values
# - Add your CLIENT_SECRET from Azure Portal
# - Update ADMIN_EMAILS with your email
# - Change SECRET_KEY to a random string
```

**Important**: Update the `REDIRECT_URI` in Azure Portal to:
```
http://localhost:4343/auth/callback
```

### 2. Build and Run

```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application

- **Blog**: http://localhost:4343
- **PostgreSQL**: localhost:5432
  - Database: `blogsite`
  - User: `bloguser`
  - Password: `blogpass123`

---

## 📁 Project Structure

```
.
├── Dockerfile                  # Flask app container definition
├── docker-compose.yml         # Multi-container orchestration
├── init_postgres.sql          # PostgreSQL initialization
├── init_db_postgres.py        # Database schema creation
├── requirements.txt           # Python dependencies (includes psycopg2)
├── app.py                     # Flask application (supports PostgreSQL)
└── env.docker.example         # Environment variables template
```

---

## 🔧 Docker Compose Services

### `db` (PostgreSQL 16)
- **Image**: postgres:16-alpine
- **Port**: 5432
- **Database**: blogsite
- **User**: bloguser
- **Password**: blogpass123
- **Volume**: `postgres_data` (persists data)

### `web` (Flask Application)
- **Build**: From Dockerfile
- **Port**: 4343 → 4343
- **Depends on**: PostgreSQL database
- **Volumes**:
  - `./uploads` → `/app/uploads` (user uploads persist)
  - `./flask_session` → `/app/flask_session` (sessions persist)

---

## 🛠️ Common Commands

### Start Services
```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d
```

### Stop Services
```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and delete volumes (DELETES DATABASE!)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up --build

# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```

### Access Container Shell
```bash
# Flask app container
docker exec -it blogki-web sh

# PostgreSQL container
docker exec -it blogki-db psql -U bloguser -d blogsite
```

### Database Operations
```bash
# Backup database
docker exec blogki-db pg_dump -U bloguser blogsite > backup.sql

# Restore database
cat backup.sql | docker exec -i blogki-db psql -U bloguser -d blogsite

# Access PostgreSQL CLI
docker exec -it blogki-db psql -U bloguser -d blogsite
```

---

## 🔍 Troubleshooting

### Issue: "Connection refused" or "Database not ready"

**Solution**: Wait for the database to be fully initialized (about 10-15 seconds on first run)

```bash
# Check database health
docker-compose ps

# View database logs
docker-compose logs db
```

### Issue: "Port 4343 already in use"

**Solution**: Stop any process using port 4343, or change the port in `docker-compose.yml`:

```yaml
web:
  ports:
    - "8080:4343"  # Access via http://localhost:8080
```

### Issue: "Database schema mismatch"

**Solution**: Reset the database:

```bash
# Stop containers
docker-compose down

# Remove database volume
docker volume rm demo_postgres_data

# Restart (will recreate database)
docker-compose up --build
```

### Issue: "Authentication failed" after login

**Solution**: 
1. Clear browser cookies for `localhost:4343`
2. Update `REDIRECT_URI` in Azure Portal to match port 4343
3. Verify `CLIENT_SECRET` in `.env` file

### Issue: Images not loading

**Solution**: Check uploads volume mount:

```bash
# Verify uploads directory exists
docker exec blogki-web ls -la /app/uploads

# Check permissions
docker exec blogki-web chmod -R 755 /app/uploads
```

---

## 🔐 Security Notes

### For Production:

1. **Change default passwords**:
   ```yaml
   environment:
     POSTGRES_PASSWORD: your-strong-password-here
   ```

2. **Use secrets management**:
   - Don't commit `.env` file
   - Use Docker secrets or environment-specific configs

3. **Enable HTTPS**:
   - Add nginx reverse proxy
   - Configure SSL certificates

4. **Limit database access**:
   ```yaml
   ports:
     # Don't expose PostgreSQL externally
     # - "5432:5432"  # REMOVE THIS LINE
   ```

---

## 📊 Data Persistence

### Volumes

- **`postgres_data`**: Database files (survives container restarts)
- **`./uploads`**: User-uploaded images (persists on host)
- **`./flask_session`**: User sessions (persists on host)

### Backup Strategy

```bash
# Automated backup script (create backup.sh)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec blogki-db pg_dump -U bloguser blogsite > "backup_$DATE.sql"
docker exec blogki-db pg_dump -U bloguser -Fc blogsite > "backup_$DATE.dump"
```

---

## 🚀 Production Deployment

### Using Gunicorn (Production WSGI)

Modify `Dockerfile` CMD:

```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4343", "app:app"]
```

Or update `docker-compose.yml`:

```yaml
web:
  command: gunicorn -w 4 -b 0.0.0.0:4343 app:app
```

### Environment Variables for Production

```env
SECRET_KEY=<long-random-string>
FLASK_PORT=4343
DATABASE_URL=postgresql://bloguser:strongpassword@db:5432/blogsite
REDIRECT_URI=https://yourdomain.com/auth/callback
```

---

## 📈 Monitoring

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Specific container
docker stats blogki-web
```

### Health Checks

```bash
# Database health
docker-compose exec db pg_isready -U bloguser

# Web app health
curl http://localhost:4343/test
```

---

## 🎉 Success!

Your blog should now be running at **http://localhost:4343**

- ✅ PostgreSQL database
- ✅ Flask web application
- ✅ Data persistence
- ✅ Port 4343 exposed

**Next Steps:**
1. Login with your Entra ID account
2. Access admin panel: http://localhost:4343/admin
3. Create your first blog post!

---

## 🆘 Need Help?

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify `.env` configuration
3. Ensure Docker Desktop is running
4. Try rebuilding: `docker-compose up --build`

**For questions or issues, check the logs carefully - they usually contain the answer!** 🔍

