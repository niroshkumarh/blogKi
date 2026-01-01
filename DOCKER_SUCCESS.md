# 🎉 Docker Setup Complete!

## ✅ Your Blog is Now Running in Docker!

---

## 🚀 Access Your Blog

### **Blog Website**
🌐 **http://localhost:4343**

### **Database (PostgreSQL)**
📊 **localhost:5432**
- Database: `blogsite`
- User: `bloguser`
- Password: `blogpass123`

---

## 📊 Container Status

```
✅ blogki-db  (PostgreSQL 16)  - HEALTHY
✅ blogki-web (Flask App)      - RUNNING
```

### Ports
- **Web Application**: `0.0.0.0:4343` → Container:4343
- **Database**: `0.0.0.0:5432` → Container:5432

---

## 🎯 What Was Successfully Done

### ✅ Database Migration
- PostgreSQL database created
- All tables initialized:
  - `users` (Entra ID authenticated users)
  - `posts` (Blog articles)
  - `comments` (User comments)
  - `likes` (Post likes)
  - `read_events` (Reading analytics)

### ✅ Data Migration
- **2 blog posts** successfully migrated:
  1. "The Startup Story of Perplexity AI - Aravind Srinivas at TC Day 3"
  2. "Innovation at Scale: Learning from Vikram Arochamy (Amazon)"

### ✅ Application Features
- Flask web server running on port 4343
- PostgreSQL database backend
- Persistent data storage (volumes)
- Health checks enabled
- Auto-restart on failure

---

## 🔧 Managing Your Docker Blog

### View Logs
```bash
# All logs
docker-compose logs -f

# Web logs only
docker-compose logs -f web

# Database logs only
docker-compose logs -f db
```

### Stop/Start
```bash
# Stop containers (data persists)
docker-compose stop

# Start containers
docker-compose start

# Restart containers
docker-compose restart
```

### Shutdown
```bash
# Stop and remove containers (data persists in volumes)
docker-compose down

# Stop, remove containers AND delete all data (⚠️ DANGEROUS!)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up --build -d

# View logs
docker-compose logs -f web
```

---

## 📝 Next Steps

### 1. Update Azure Portal Redirect URI

**⚠️ IMPORTANT**: Update your Microsoft Entra ID app registration:

```
Old: http://localhost:5000/auth/callback
New: http://localhost:4343/auth/callback
```

### 2. Test Your Blog

1. Open: **http://localhost:4343**
2. Login with Microsoft Entra ID
3. Verify both blog posts are visible
4. Check admin panel: **http://localhost:4343/admin**

### 3. Create a New Post

- Click "New Post" in admin
- Fill in details
- Upload images
- Publish!

---

## 🗄️ Database Operations

### Access PostgreSQL CLI
```bash
docker exec -it blogki-db psql -U bloguser -d blogsite
```

### Common SQL Commands
```sql
-- List all tables
\dt

-- View posts
SELECT id, title, status, published_at FROM posts;

-- View users
SELECT id, email, name FROM users;

-- View comments
SELECT id, user_id, post_id, body FROM comments;

-- Exit
\q
```

### Backup Database
```bash
# SQL format
docker exec blogki-db pg_dump -U bloguser blogsite > backup_$(date +%Y%m%d).sql

# Binary format (smaller, faster)
docker exec blogki-db pg_dump -U bloguser -Fc blogsite > backup_$(date +%Y%m%d).dump
```

### Restore Database
```bash
# From SQL backup
cat backup_20260101.sql | docker exec -i blogki-db psql -U bloguser -d blogsite

# From binary backup
cat backup_20260101.dump | docker exec -i blogki-db pg_restore -U bloguser -d blogsite
```

---

## 📊 Monitoring

### Check Container Health
```bash
docker-compose ps
```

### View Resource Usage
```bash
docker stats blogki-web blogki-db
```

### Container Info
```bash
# Web container details
docker inspect blogki-web

# Database container details
docker inspect blogki-db
```

---

## 🔐 Security Notes

### Current Setup (Development)
- ⚠️ Using default database password
- ⚠️ Database port exposed externally
- ⚠️ Debug mode enabled
- ⚠️ HTTP only (no HTTPS)

### For Production
1. **Change database password**:
   ```env
   DATABASE_URL=postgresql://bloguser:STRONG-PASSWORD@db:5432/blogsite
   ```

2. **Remove database port exposure**:
   ```yaml
   # Comment out in docker-compose.yml
   # ports:
   #   - "5432:5432"
   ```

3. **Use Gunicorn** instead of Flask dev server:
   ```yaml
   command: gunicorn -w 4 -b 0.0.0.0:4343 app:app
   ```

4. **Add nginx reverse proxy** for HTTPS

5. **Use Docker secrets** for sensitive data

---

## 🎨 Volume Mounts

Your data is persistent across container restarts:

| Volume | Purpose | Location |
|--------|---------|----------|
| `postgres_data` | Database files | Docker managed |
| `./uploads` | User images | Host directory |
| `./flask_session` | Sessions | Host directory |

---

## 🚨 Troubleshooting

### Cannot Access http://localhost:4343
```bash
# Check if containers are running
docker-compose ps

# Check web logs
docker-compose logs web

# Restart containers
docker-compose restart
```

### Database Connection Issues
```bash
# Check database health
docker-compose exec db pg_isready -U bloguser

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Authentication Fails
1. Clear browser cookies for `localhost:4343`
2. Verify `CLIENT_SECRET` in `.env`
3. Update redirect URI in Azure Portal to port 4343
4. Restart web container: `docker-compose restart web`

### Images Not Loading
```bash
# Check uploads directory
docker exec blogki-web ls -la /app/uploads

# Fix permissions
docker exec blogki-web chmod -R 755 /app/uploads
```

---

## 📚 Documentation

- **Setup Guide**: `DOCKER_SETUP.md`
- **Implementation Summary**: `DOCKER_SUMMARY.md`
- **Quick Start Scripts**:
  - Windows: `docker-start.bat`
  - Linux/Mac: `docker-start.sh`

---

## 🎊 Success Checklist

- ✅ PostgreSQL container running and healthy
- ✅ Flask web container running
- ✅ Database tables created
- ✅ Blog posts migrated
- ✅ Web accessible at http://localhost:4343
- ✅ Database accessible at localhost:5432
- ✅ Volumes configured for data persistence
- ✅ Health checks active

---

## 🚀 Your Blog is Ready!

**Open your browser and go to:**

## 🌐 **http://localhost:4343**

**Login, create posts, and enjoy your Dockerized blog!** 🎉

---

**For detailed information, see:**
- `DOCKER_SETUP.md` - Complete setup guide
- `DOCKER_SUMMARY.md` - Technical implementation details

