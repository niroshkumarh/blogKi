# Fixing 400 Bad Request Error During OAuth Callback

## What's Happening
✅ Nginx and Cloudflare are working (no more 403)  
✅ Flask is receiving requests  
❌ OAuth callback is getting a 400 Bad Request

## Root Cause
The OAuth callback is likely failing because Flask isn't correctly detecting the HTTPS scheme when behind Nginx/Cloudflare.

## Fix Steps

### Step 1: Update Flask to Handle Proxied Requests

We need to tell Flask to trust the proxy headers. On your **production server**, add this to `.env`:

```bash
echo "FLASK_ENV=production" >> ~/Blog/.env
echo "PREFERRED_URL_SCHEME=https" >> ~/Blog/.env
```

### Step 2: Update Nginx Configuration

Add the OAuth-specific proxy headers. Edit your Nginx config:

```bash
sudo nano /etc/nginx/sites-available/blogs.iqubekct.ac.in
```

Add or update the `location /` block with these critical headers:

```nginx
location / {
    proxy_pass http://localhost:4343;
    
    # Standard proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    
    # Critical for OAuth
    proxy_buffering off;
    proxy_redirect off;
    
    # Increase buffer sizes for OAuth tokens
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;
}
```

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Restart Docker Container

```bash
cd ~/Blog
docker-compose restart web
```

### Step 4: Clear Everything and Test

1. **Clear browser cookies completely** for `blogs.iqubekct.ac.in`
2. **Close all browser tabs**
3. Visit: `https://blogs.iqubekct.ac.in/`
4. Try logging in again

## Alternative Fix: Update auth.py (If Above Doesn't Work)

If the issue persists, we need to modify Flask's auth handling. Let me know and I'll update the code to:
- Use `ProxyFix` middleware to properly handle X-Forwarded headers
- Add more robust error handling in the callback route

## Debug Commands

Run these to diagnose:

```bash
# Check Docker logs during login attempt
docker logs -f blogki-web

# Check current environment variables
docker exec blogki-web env | grep -E "(REDIRECT_URI|FLASK|PREFERRED)"

# Test direct access
curl -I http://localhost:4343/auth/login?next=/
```

## What to Look For in Logs

When you try to log in, watch for these errors in `docker logs -f blogki-web`:
- `KeyError` related to session or request
- `ValueError` about redirect URI
- `400` from Microsoft's token endpoint
- Any mention of "scheme" or "https"

## Next Steps

1. Add the two lines to `.env` (FLASK_ENV and PREFERRED_URL_SCHEME)
2. Update Nginx config with the proxy headers
3. Restart: `docker-compose restart web`
4. Clear browser cookies
5. Try login again
6. If still failing, run `docker logs -f blogki-web` and share the error

