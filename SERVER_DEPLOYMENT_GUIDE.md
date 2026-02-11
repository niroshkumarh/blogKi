# Server Deployment Guide - Export/Import Feature

## 📋 Overview

Deploy the new export/import feature to your production server.

**Branch:** `blogsite`  
**Repository:** https://github.com/niroshkumarh/blogKi

---

## 🚀 Deployment Steps

### Step 1: SSH to Your Server

```bash
ssh user@your-server-ip
```

### Step 2: Navigate to Project Directory

```bash
cd /path/to/your/blog/project
# Example: cd /var/www/blogki
# or: cd /home/user/blogki
```

### Step 3: Check Current Branch

```bash
git branch
```

**Expected output:**
```
* blogsite  (if already on blogsite)
or
* main     (if on main branch)
```

### Step 4: Pull Latest Changes

**If already on `blogsite` branch:**
```bash
git pull origin blogsite
```

**If on different branch (e.g., main), switch first:**
```bash
# Stash any local changes first
git stash

# Switch to blogsite branch
git checkout blogsite

# Pull latest changes
git pull origin blogsite
```

### Step 5: Stop Running Containers

```bash
docker-compose down
```

**Expected output:**
```
Stopping blogki-web ...
Stopping blogki-db ...
Removing blogki-web ...
Removing blogki-db ...
```

### Step 6: Rebuild with New Dependencies

```bash
docker-compose up -d --build
```

**Why `--build`?**
- New dependencies: openpyxl, Pillow
- Updated code in admin.py
- New template files

**Expected output:**
```
Building web...
Installing openpyxl==3.1.2
Installing Pillow==10.2.0
...
Creating blogki-db ...
Creating blogki-web ...
```

### Step 7: Wait for Services to Start

```bash
# Check status
docker-compose ps

# Watch logs
docker-compose logs -f web
```

**Wait for:**
```
✅ Database already initialized
✅ Migration complete!
✅ Serving Flask app 'app'
```

**Press Ctrl+C to stop watching logs**

### Step 8: Verify Deployment

```bash
# Check if containers are running
docker ps | grep blogki

# Test the endpoints
curl -I http://localhost:4343/admin/posts
```

**Expected:**
```
HTTP/1.1 302 FOUND  (redirects to login)
or
HTTP/1.1 200 OK     (if already logged in)
```

---

## 🧪 Test the New Feature

### 1. Access Admin Panel

Visit: `http://your-domain.com/admin/posts`

### 2. Test Export

1. Click **"Export to Excel"** (green button)
2. File should download: `posts_export_YYYYMMDD_HHMMSS.xlsx`
3. Open file, verify 16 columns and your posts

### 3. Test Import

1. Click **"Import from Excel"** (yellow button)
2. Upload the Excel file you just exported
3. Click **"Import Posts"**
4. Should see: `✅ Import complete! Imported: 0, Updated: X, Skipped: 0`

---

## 🔧 Troubleshooting

### Issue: "openpyxl not found"

**Solution:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Import page is empty

**Solution:**
```bash
docker-compose restart web
# Wait 10 seconds
docker-compose logs web --tail 20
```

### Issue: Excel export fails

**Check logs:**
```bash
docker logs blogki-web | grep -i error
```

**Common fix:**
```bash
docker exec blogki-web pip install openpyxl Pillow
docker-compose restart web
```

### Issue: Import says "Skipped: X"

**Check what was skipped:**
```bash
docker logs blogki-web | grep -i "error importing row"
```

---

## 📊 What's New on Server

### New Features Available:
- ✅ Export all posts to Excel
- ✅ Import posts from Excel
- ✅ Base64 image support
- ✅ Bulk post updates
- ✅ Site-to-site migration capability

### New Files on Server:
```
/app/admin.py                           (updated)
/app/requirements.txt                   (updated)
/app/templates/admin/posts_list.html    (updated)
/app/templates/admin/posts_import.html  (new)
/app/*.md                               (documentation files)
```

### New Dependencies Installed:
- openpyxl==3.1.2
- Pillow==10.2.0

---

## 🎯 Quick Commands Summary

```bash
# Navigate to project
cd /path/to/blogki

# Pull latest code
git checkout blogsite
git pull origin blogsite

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f web

# Verify
curl -I http://localhost:4343/admin/posts
```

---

## 🔐 Environment Variables

**No new environment variables needed!**

The feature uses existing configuration:
- `UPLOAD_FOLDER` - For saving imported images
- Database connection - For post data

---

## ⚠️ Important Notes

1. **Backup First:**
   ```bash
   # Backup database before first import
   docker exec blogki-db pg_dump -U postgres blogki > backup.sql
   ```

2. **Test Import:**
   - Export first, then re-import to test
   - Check that all posts are still there

3. **Large Files:**
   - Excel with many images can be 5-10 MB
   - Ensure nginx/web server allows large uploads
   - Check `client_max_body_size` in nginx config

4. **Migration Use:**
   - Perfect for moving posts between servers
   - Export from one server, import to another

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Server is accessible
- [ ] Can log in to admin panel
- [ ] See "Export to Excel" button (green)
- [ ] See "Import from Excel" button (yellow)
- [ ] Export downloads an Excel file
- [ ] Import page shows upload form
- [ ] Test import works without errors
- [ ] Posts display correctly after import

---

## 📞 Need Help?

**Check logs:**
```bash
docker-compose logs web --tail 50
docker-compose logs db --tail 20
```

**Restart if needed:**
```bash
docker-compose restart web
```

**Full rebuild:**
```bash
docker-compose down
docker-compose up -d --build --force-recreate
```

---

**Deployment Status:** Ready to deploy  
**Estimated Time:** 5-10 minutes  
**Downtime:** ~2 minutes during rebuild

*Last updated: Feb 7, 2026*
