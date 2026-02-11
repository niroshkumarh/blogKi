# Quick Server Deployment Commands

## 🚀 Run These Commands on Your Server

```bash
# 1. Navigate to your project
cd /path/to/your/blog/project

# 2. Pull latest code from blogsite branch
git checkout blogsite
git pull origin blogsite

# 3. Rebuild Docker containers (includes new dependencies)
docker-compose down
docker-compose up -d --build

# 4. Wait 30 seconds for services to start
sleep 30

# 5. Check if running
docker-compose ps

# 6. Verify it works
curl -I http://localhost:4343/admin/posts
```

---

## ✅ Expected Results

After running commands:

1. **Git pull output:**
   ```
   From https://github.com/niroshkumarh/blogKi
      branch blogsite -> FETCH_HEAD
   Updating xxxxx..f8782ac
   Fast-forward
    admin.py | 262 +++++++++++++++++++++
    ...
   ```

2. **Docker build output:**
   ```
   Building web...
   Installing openpyxl==3.1.2
   Installing Pillow==10.2.0
   Successfully installed...
   ```

3. **Docker ps output:**
   ```
   blogki-web    Up 1 minute    0.0.0.0:4343->4343/tcp
   blogki-db     Up 1 minute    0.0.0.0:4345->5432/tcp
   ```

---

## 🧪 Test It

Visit in browser:
```
http://your-server-domain.com/admin/posts
```

You should see:
- ✅ Green "Export to Excel" button
- ✅ Yellow "Import from Excel" button

Click Export → File downloads → **Feature is working!** 🎉

---

## ⚠️ If Something Goes Wrong

```bash
# View logs
docker-compose logs web --tail 50

# Restart
docker-compose restart web

# Full rebuild (if needed)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

**Branch to pull:** `blogsite`  
**Estimated time:** 5-10 minutes  
**Downtime:** ~2 minutes
