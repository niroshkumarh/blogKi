# Troubleshooting 403 Forbidden Error

## Current Issue
Getting `403 Forbidden` from openresty when accessing `https://blogs.iqubekct.ac.in/auth/login`

## Diagnosis Steps

### 1. Check Flask App Logs
```bash
docker logs blogki-web --tail 100
```
Look for authentication errors or exceptions.

### 2. Check Nginx Configuration
```bash
# Check if Nginx is blocking /auth/* routes
sudo nginx -T | grep -A 10 "location /auth"

# Check for any deny rules
sudo nginx -T | grep "deny"
```

### 3. Test Direct Container Access
```bash
# Bypass Nginx/Cloudflare and test Flask directly
curl -I http://localhost:4343/auth/login?next=/
```
If this works, the issue is with Nginx or Cloudflare, not Flask.

### 4. Check Nginx Error Logs
```bash
sudo tail -f /var/log/nginx/error.log
```

## Most Likely Causes

### Cause 1: Azure Portal Redirect URI Not Updated ⚠️ CRITICAL
**Symptom**: 403 when trying to authenticate with Microsoft  
**Fix**: 
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Microsoft Entra ID** → **App registrations** → Your App
3. Go to: **Authentication** → **Web** platform
4. **ADD** this redirect URI:
   ```
   https://blogs.iqubekct.ac.in/auth/callback
   ```
5. Click **Save**
6. Wait 2-3 minutes for propagation

### Cause 2: Nginx Blocking OAuth Callback
**Symptom**: Nginx rejecting requests to `/auth/*` routes  
**Fix**: Add this to your Nginx configuration:

```nginx
location /auth/ {
    proxy_pass http://localhost:4343;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Important for OAuth flows
    proxy_buffering off;
    proxy_redirect off;
}
```

Then reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Cause 3: Cloudflare WAF Blocking
**Symptom**: Cloudflare's Web Application Firewall blocking OAuth redirects  
**Fix**:
1. Go to Cloudflare Dashboard → **Security** → **WAF**
2. Check **Security Events** for blocked requests
3. If blocked, create a **WAF Exception Rule** for `/auth/*` paths

### Cause 4: REDIRECT_URI in .env Still Uses HTTP
**Check**:
```bash
cat ~/Blog/.env | grep REDIRECT_URI
```
**Should be**:
```
REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback
```

## Quick Test Commands

Run these on your production server:

```bash
# 1. Check if Flask is responding
curl http://localhost:4343/test

# 2. Check if /auth/login is accessible locally
curl -I http://localhost:4343/auth/login?next=/

# 3. Check current redirect URI
cat ~/Blog/.env | grep REDIRECT_URI

# 4. Check Flask logs for errors
docker logs blogki-web --tail 50 | grep -i error

# 5. Test with browser (check response headers)
curl -v https://blogs.iqubekct.ac.in/auth/login
```

## Expected Behavior

When visiting `https://blogs.iqubekct.ac.in/auth/login`, you should:
1. Be redirected to `https://login.microsoftonline.com/...`
2. See Microsoft login page
3. After login, be redirected to `https://blogs.iqubekct.ac.in/auth/callback?code=...`
4. Then redirected to `/archive/2026-01` (normal user) or `/admin` (admin)

## Next Steps

1. **Run the diagnosis commands above on your server**
2. **Share the output** so I can pinpoint the exact issue
3. **Most importantly**: Confirm if you've updated the Azure Portal redirect URI

