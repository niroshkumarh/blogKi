# 🚀 Deploy 400 Error Fix to Production

## What We Fixed

✅ Added **ProxyFix middleware** to handle X-Forwarded headers from Nginx/Cloudflare  
✅ Added **FLASK_ENV** and **PREFERRED_URL_SCHEME** configuration  
✅ Made session cookies secure in production  

This will fix the 400 Bad Request error during OAuth callback.

---

## 🔥 Quick Deploy (5 Minutes)

### Step 1: Commit and Push Changes

On your **Windows machine**, run these commands:

```powershell
cd "C:\Downloaded Web Sites\wp.alithemes.com\html\stories\demo"

git add app.py deploy-production.sh DEPLOY_FIX_NOW.md FIX_400_ERROR.md nginx_oauth_fix.conf TROUBLESHOOTING_403.md

git commit -m "Fix: Add ProxyFix middleware for OAuth behind reverse proxy"

git push origin docker-deployment
```

### Step 2: Deploy to Production Server

SSH into your production server and run:

```bash
ssh iqube@blogs.iqubekct.ac.in

cd ~/Blog

# Pull latest changes
git pull origin docker-deployment

# Make deploy script executable
chmod +x deploy-production.sh

# Run deployment
./deploy-production.sh
```

The script will:
- ✅ Pull latest code
- ✅ Add `FLASK_ENV=production` to .env
- ✅ Add `PREFERRED_URL_SCHEME=https` to .env
- ✅ Rebuild Docker containers
- ✅ Initialize database
- ✅ Test the application

---

## 🔧 Manual Deployment (If Script Fails)

### On Production Server:

```bash
cd ~/Blog

# 1. Pull code
git pull origin docker-deployment

# 2. Update .env
echo "FLASK_ENV=production" >> .env
echo "PREFERRED_URL_SCHEME=https" >> .env

# 3. Verify redirect URI
cat .env | grep REDIRECT_URI
# Should be: REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback

# 4. Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 5. Check logs
docker logs -f blogki-web
```

---

## 📋 Verification Checklist

After deployment, verify:

### 1. Container is Running
```bash
docker-compose ps
# Should show "Up" status
```

### 2. App is Responding
```bash
curl http://localhost:4343/test
# Should return HTML with "Flask App is Running!"
```

### 3. Environment Variables
```bash
docker exec blogki-web env | grep -E "(FLASK_ENV|PREFERRED_URL_SCHEME)"
# Should show:
#   FLASK_ENV=production
#   PREFERRED_URL_SCHEME=https
```

### 4. Test Login Flow

1. **Clear browser cookies** for `blogs.iqubekct.ac.in`
2. Visit: `https://blogs.iqubekct.ac.in/`
3. Should redirect to Microsoft login
4. After login, should redirect to blog archive (no more 400 error!)

---

## 🆘 If Still Getting 400 Error

### Option A: Check Nginx Configuration

Your Nginx config needs these headers:

```bash
sudo nano /etc/nginx/sites-available/blogs.iqubekct.ac.in
```

Ensure you have:

```nginx
location / {
    proxy_pass http://localhost:4343;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_buffering off;
}
```

Then:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Option B: Check Docker Logs

```bash
docker logs -f blogki-web
```

Watch for errors during login attempt. Share the error with me.

### Option C: Verify Azure Portal

Ensure Azure Portal has this redirect URI:
```
https://blogs.iqubekct.ac.in/auth/callback
```

Go to: **Azure Portal** → **Entra ID** → **App registrations** → Your App → **Authentication**

---

## 🎯 Expected Behavior After Fix

1. Visit `https://blogs.iqubekct.ac.in/`
2. Redirects to `https://login.microsoftonline.com/...` (Microsoft login)
3. After login, redirects to `https://blogs.iqubekct.ac.in/auth/callback?code=...`
4. **No 400 error** - successfully processes callback
5. Redirects to `/archive/2026-01` (normal user) or `/admin` (admin)
6. You see the blog page! 🎉

---

## 📞 What to Report If It Doesn't Work

Run these and share the output:

```bash
# 1. Check if ProxyFix is active
docker logs blogki-web --tail 50

# 2. Test direct access
curl -I http://localhost:4343/auth/login?next=/

# 3. Check environment
docker exec blogki-web env | grep -E "(FLASK|DATABASE|REDIRECT)"

# 4. Test through Nginx
curl -I https://blogs.iqubekct.ac.in/
```

---

## 🎉 Success Indicators

After successful deployment, you should see:

✅ No more "403 Forbidden"  
✅ No more "400 Bad Request"  
✅ Microsoft login page appears  
✅ Successfully redirected to blog after login  
✅ Can view blog posts, comment, and like  

---

Ready to deploy? Run the commands in **Step 1** and **Step 2** above! 🚀

