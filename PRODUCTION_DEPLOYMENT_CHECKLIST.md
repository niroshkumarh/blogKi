# 🚀 Production Deployment Checklist

## ✅ Current Status

### Environment Configuration
- ✅ REDIRECT_URI updated to: `https://blogs.iqubekct.ac.in/auth/callback`
- ✅ Web container restarted

---

## 📋 Remaining Steps

### 1. ⚠️ Update Azure Portal (CRITICAL)

**Go to:** https://portal.azure.com

1. Navigate to **Microsoft Entra ID** → **App registrations**
2. Find your app: Client ID `423dd38a-439a-4b99-a313-9472d2c0dad6`
3. Click **"Authentication"** in left sidebar
4. Under **"Web" → "Redirect URIs"**, add:
   ```
   https://blogs.iqubekct.ac.in/auth/callback
   ```
5. Keep the localhost one for local testing:
   ```
   http://localhost:4343/auth/callback
   ```
6. Click **"Save"**

### 2. 🔍 Verify Container Status

```bash
docker compose ps
docker compose logs web --tail=30
```

Expected output:
- Both containers should show "Up"
- Web logs should show: "Running on http://0.0.0.0:4343"

### 3. 🧪 Test Backend Direct Access

```bash
# Test if Flask is responding
curl http://localhost:4343/test

# Should return HTML showing:
# - Database posts count
# - Auth config check
```

### 4. 🌐 Check Nginx Configuration

Make sure Nginx is properly proxying to port 4343:

```bash
sudo nginx -T | grep -A 30 "blogs.iqubekct.ac.in"
```

Should include:
```nginx
proxy_pass http://localhost:4343;
```

### 5. 🧹 Clear Browser Cache

**IMPORTANT:** Before testing again:

1. Open browser DevTools (F12)
2. Right-click on refresh button → **"Empty Cache and Hard Reload"**
3. Or use Incognito/Private mode

Alternatively:
- Clear cookies for `blogs.iqubekct.ac.in`
- Clear all site data

### 6. 🔐 Verify SSL Certificate

```bash
# Check SSL cert
sudo certbot certificates

# Should show valid cert for blogs.iqubekct.ac.in
```

---

## 🧪 Testing Steps

### Step 1: Check Containers
```bash
docker compose ps
```
Expected:
```
NAME         STATUS              PORTS
blogki-db    Up (healthy)       0.0.0.0:4345->5432/tcp
blogki-web   Up                 0.0.0.0:4343->4343/tcp
```

### Step 2: Check Web Logs
```bash
docker compose logs web --tail=50
```
Look for:
- ✅ "Database initialized successfully"
- ✅ "Migration complete"
- ✅ "Running on http://0.0.0.0:4343"
- ❌ No error messages

### Step 3: Test Direct Access
```bash
curl http://localhost:4343/test
```
Should return HTML page, not error.

### Step 4: Test via Nginx
```bash
curl -I https://blogs.iqubekct.ac.in/
```
Should return:
- `HTTP/2 302` (redirect to login)
- NOT `403 Forbidden`

### Step 5: Access in Browser
1. Clear browser cache
2. Go to: `https://blogs.iqubekct.ac.in`
3. Should redirect to Microsoft login
4. After login, should redirect back to your blog

---

## 🔧 If Still Getting 403 Forbidden

### Check 1: Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Check 2: Nginx Config
```bash
sudo cat /etc/nginx/sites-enabled/blogs.iqubekct.ac.in
```

Should have:
```nginx
location / {
    proxy_pass http://localhost:4343;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Check 3: Firewall
```bash
sudo ufw status
```
Port 4343 should be allowed (or localhost should have access).

### Check 4: Docker Network
```bash
docker compose exec web curl http://localhost:4343/test
```
Test from inside the container.

---

## 🚨 Common Issues & Solutions

### Issue: 403 Forbidden
**Cause**: Azure Portal redirect URI not updated  
**Fix**: Update Azure Portal as described in Step 1

### Issue: Connection Refused
**Cause**: Flask not running or Nginx can't reach it  
**Fix**: 
```bash
docker compose restart web
sudo systemctl restart nginx
```

### Issue: Redirect Loop
**Cause**: Mismatched redirect URIs  
**Fix**: Ensure `.env`, Azure Portal, and browser all use same URL

### Issue: SSL Certificate Error
**Cause**: Expired or invalid cert  
**Fix**:
```bash
sudo certbot renew
sudo systemctl restart nginx
```

---

## ✅ Success Indicators

When everything is working:

1. ✅ `docker compose ps` shows both containers "Up"
2. ✅ Web logs show Flask running on port 4343
3. ✅ `curl http://localhost:4343/test` returns HTML
4. ✅ Browser shows Microsoft login page
5. ✅ After login, blog loads successfully
6. ✅ Can create/view posts
7. ✅ Admin panel accessible

---

## 📊 Quick Diagnostic Script

Run this to check everything:

```bash
#!/bin/bash
echo "=== Docker Status ==="
docker compose ps

echo -e "\n=== Web Container Logs ==="
docker compose logs web --tail=20

echo -e "\n=== Environment Config ==="
grep REDIRECT_URI ~/Blog/.env

echo -e "\n=== Flask Test ==="
curl -s http://localhost:4343/test | grep -o '<h1>.*</h1>'

echo -e "\n=== Nginx Status ==="
sudo systemctl status nginx | grep Active

echo -e "\n=== SSL Certificate ==="
sudo certbot certificates | grep "blogs.iqubekct.ac.in" -A 3
```

---

## 🎯 Next Commands to Run

```bash
# 1. Check container status
docker compose ps

# 2. View web logs
docker compose logs web --tail=30

# 3. Test Flask directly
curl http://localhost:4343/test

# 4. Check nginx logs
sudo tail -20 /var/log/nginx/error.log
```

Then share the output so we can diagnose further!


