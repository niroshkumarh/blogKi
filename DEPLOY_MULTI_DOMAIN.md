# 🌐 Multi-Domain Deployment Guide

Your blog supports **two domains**:
1. **https://blogs.iqubekct.ac.in**
2. **https://horizon.kumaraguru.in**

---

## 🎯 What's New

✅ **Dynamic Redirect URI Detection** - App automatically detects which domain the user is visiting  
✅ **ProxyFix Middleware** - Handles X-Forwarded headers from Nginx/Cloudflare  
✅ **Production-Ready** - HTTPS, secure cookies, timezone-aware timestamps  

---

## 🚀 Quick Deployment (3 Steps)

### Step 1: Update Azure Portal (CRITICAL - Do This First!)

You **MUST** add both redirect URIs to Azure Portal:

1. Go to: **https://portal.azure.com**
2. Navigate: **Entra ID** → **App registrations** → Your App → **Authentication**
3. Add these **TWO** redirect URIs:

```
https://blogs.iqubekct.ac.in/auth/callback
https://horizon.kumaraguru.in/auth/callback
```

4. Click **Save**

**📋 Detailed instructions:** See `AZURE_PORTAL_SETUP.md`

---

### Step 2: Commit and Push Code (Windows Machine)

```powershell
cd "C:\Downloaded Web Sites\wp.alithemes.com\html\stories\demo"

git add auth.py deploy-production.sh MULTI_DOMAIN_SETUP.md AZURE_PORTAL_SETUP.md DEPLOY_MULTI_DOMAIN.md

git commit -m "Add multi-domain support with dynamic redirect URI detection

- Updated auth.py to detect domain automatically
- Supports blogs.iqubekct.ac.in and horizon.kumaraguru.in
- ProxyFix middleware for reverse proxy compatibility
- Fixed datetime.utcnow() deprecation warnings"

git push origin docker-postgres-analytics
```

---

### Step 3: Deploy to Production Server (Linux)

```bash
ssh iqube@blogs.iqubekct.ac.in

cd ~/Blog

# Pull latest code
git pull origin docker-postgres-analytics

# Update environment
echo "FLASK_ENV=production" >> .env
echo "PREFERRED_URL_SCHEME=https" >> .env

# Set fallback redirect URI (app will auto-detect, this is backup)
# Use whichever domain is primary for this server
sed -i 's|REDIRECT_URI=.*|REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback|g' .env

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
docker logs -f blogki-web
```

---

## 🧪 Testing Both Domains

### Test Domain 1: blogs.iqubekct.ac.in

1. **Clear browser cookies** for `blogs.iqubekct.ac.in`
2. Visit: **https://blogs.iqubekct.ac.in/**
3. Should redirect to Microsoft login
4. After login → Should see blog archive ✅

### Test Domain 2: horizon.kumaraguru.in

1. **Clear browser cookies** for `horizon.kumaraguru.in`
2. Visit: **https://horizon.kumaraguru.in/**
3. Should redirect to Microsoft login
4. After login → Should see blog archive ✅

---

## 🔍 How Dynamic Detection Works

When a user visits your site:

1. **User visits** `https://horizon.kumaraguru.in/`
2. **App detects** domain from `X-Forwarded-Host` header (set by Nginx)
3. **Builds redirect URI** dynamically: `https://horizon.kumaraguru.in/auth/callback`
4. **Redirects to Microsoft** with the correct callback URL
5. **Microsoft redirects back** to the same domain
6. **Login succeeds** ✅

### Code Implementation:

```python
def _get_dynamic_redirect_uri():
    """Build redirect URI based on incoming request domain"""
    scheme = request.headers.get('X-Forwarded-Proto', 'https')
    host = request.headers.get('X-Forwarded-Host', request.host)
    return f"{scheme}://{host}/auth/callback"
```

---

## 🖥️ Server Configuration

### If Both Domains Point to Same Server

Use **ONE deployment** with dynamic detection (recommended):

```nginx
# /etc/nginx/sites-available/blogs.conf

server {
    listen 443 ssl;
    server_name blogs.iqubekct.ac.in;
    
    # SSL certificates for blogs.iqubekct.ac.in
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:4343;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }
}

server {
    listen 443 ssl;
    server_name horizon.kumaraguru.in;
    
    # SSL certificates for horizon.kumaraguru.in
    ssl_certificate /path/to/cert2.pem;
    ssl_certificate_key /path/to/key2.pem;
    
    location / {
        proxy_pass http://localhost:4343;  # Same Flask app!
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }
}
```

### If Domains Point to Different Servers

Deploy **TWO separate instances** with different `.env` files:

**Server 1 (blogs.iqubekct.ac.in):**
```bash
REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback
```

**Server 2 (horizon.kumaraguru.in):**
```bash
REDIRECT_URI=https://horizon.kumaraguru.in/auth/callback
```

---

## 📋 Environment Configuration

### Required `.env` variables:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@db:5432/blogdb

# Security
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=production
PREFERRED_URL_SCHEME=https

# Azure Entra ID
CLIENT_ID=423dd38a-439a-4b99-a313-9472d2c0dad6
CLIENT_SECRET=your-client-secret
TENANT_ID=6b8b8296-bdff-4ad8-93ad-84bcbf3842f5

# Redirect URI (fallback only - app auto-detects domain)
REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback

# Admin access
ADMIN_EMAILS=nirosh@kct.ac.in,other@email.com
```

---

## ✅ Verification Checklist

After deployment, verify:

### 1. Azure Portal Configuration
- [ ] Both redirect URIs added to Authentication
- [ ] Changes saved successfully

### 2. Container Status
```bash
docker-compose ps
# Should show both containers as "Up"
```

### 3. Environment Variables
```bash
docker exec blogki-web env | grep -E "(FLASK_ENV|PREFERRED_URL_SCHEME)"
# Should show:
#   FLASK_ENV=production
#   PREFERRED_URL_SCHEME=https
```

### 4. App Response
```bash
curl http://localhost:4343/test
# Should return HTML with "Flask App is Running!"
```

### 5. Dynamic Detection
```bash
# Check logs during login attempt
docker logs -f blogki-web

# Should see lines like:
#   INFO: Dynamic redirect URI: https://horizon.kumaraguru.in/auth/callback
```

### 6. Both Domains Work
- [ ] `https://blogs.iqubekct.ac.in/` - Login works ✅
- [ ] `https://horizon.kumaraguru.in/` - Login works ✅

---

## 🆘 Troubleshooting

### Error: "redirect_uri_mismatch"

**Cause:** Azure Portal doesn't have the redirect URI for that domain

**Fix:**
1. Go to Azure Portal → Authentication
2. Verify **both** URIs are listed
3. Wait 1-2 minutes for propagation
4. Clear browser cookies and try again

---

### Error: "400 Bad Request"

**Cause:** App isn't detecting domain correctly

**Debug:**
```bash
# Check Docker logs during login
docker logs -f blogki-web

# Look for:
#   "Dynamic redirect URI: https://..."
```

**Fix:**
1. Verify `FLASK_ENV=production` in `.env`
2. Verify `PREFERRED_URL_SCHEME=https` in `.env`
3. Check Nginx proxy headers (see `nginx_oauth_fix.conf`)

---

### Only One Domain Works

**Cause:** Nginx proxy headers not configured

**Fix:** Update Nginx config:
```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
```

Then:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### "state mismatch" or "CSRF" error

**Cause:** Browser cookies not working properly

**Fix:**
1. Clear **all** browser cookies for both domains
2. Close all browser tabs
3. Try in incognito/private window
4. Verify cookies are enabled

---

## 📞 What to Report If Issues Persist

Run these diagnostic commands:

```bash
# 1. Check container logs
docker logs blogki-web --tail 50

# 2. Test direct access
curl -I http://localhost:4343/auth/login?next=/

# 3. Test through Nginx
curl -I https://blogs.iqubekct.ac.in/
curl -I https://horizon.kumaraguru.in/

# 4. Check environment
docker exec blogki-web env | grep -E "(FLASK|REDIRECT|DATABASE)"

# 5. Verify Azure setup
# Go to Azure Portal and screenshot the Authentication page
```

---

## 🎉 Success Indicators

After successful deployment:

✅ No more "403 Forbidden"  
✅ No more "400 Bad Request"  
✅ No more "redirect_uri_mismatch"  
✅ Microsoft login works on **both domains**  
✅ Users can view posts, comment, and like  
✅ Admin panel accessible at `/admin`  
✅ Google Analytics tracking on all pages  

---

## 🚀 Ready to Deploy?

1. **First**: Update Azure Portal (Step 1 above)
2. **Then**: Push code from Windows (Step 2 above)
3. **Finally**: Deploy to Linux server (Step 3 above)
4. **Test**: Both domains

Let me know when you're ready, and I'll help monitor the deployment! 🎯

