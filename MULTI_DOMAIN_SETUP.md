# 🌐 Multi-Domain Configuration for Wide Angle Blog

Your blog is accessible via **two domains**:
1. `https://blogs.iqubekct.ac.in`
2. `https://horizon.kumaraguru.in`

Both need to be configured in Azure Portal and your deployment.

---

## 🔐 Step 1: Update Azure Portal App Registration

This is **CRITICAL** - Azure must recognize both redirect URIs.

### Azure Portal Configuration:

1. Go to: [Azure Portal](https://portal.azure.com)
2. Navigate to: **Microsoft Entra ID** → **App registrations** → Your App
3. Click: **Authentication** (left sidebar)
4. Under **Platform configurations** → **Web**
5. Click: **Add URI** and add **BOTH** of these:

```
https://blogs.iqubekct.ac.in/auth/callback
https://horizon.kumaraguru.in/auth/callback
```

6. **Save** changes
7. Also check **Front-channel logout URL** if you have one - it should support both domains too

### Expected Result:
You should see **2 Redirect URIs** listed under the Web platform.

---

## 🐳 Step 2: Configure Docker Deployment for Primary Domain

Your `.env` file can only have **ONE** `REDIRECT_URI` at a time. You need to set it based on which domain the container is serving.

### For blogs.iqubekct.ac.in:

```bash
REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback
```

### For horizon.kumaraguru.in:

```bash
REDIRECT_URI=https://horizon.kumaraguru.in/auth/callback
```

---

## 🔄 Option A: Single Deployment (If Same Server)

If both domains point to the **same server**, you only need one deployment:

### Solution: Dynamic Redirect URI Detection

We can modify `auth.py` to automatically detect which domain the user is coming from and use the appropriate redirect URI.

**This is the recommended approach** - I'll implement this for you.

---

## 🔄 Option B: Two Separate Deployments

If you want separate deployments for each domain:

### Deployment 1: blogs.iqubekct.ac.in
```bash
# On server 1 (or port 4343)
cd ~/Blog
echo "REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback" >> .env
docker-compose up -d
```

### Deployment 2: horizon.kumaraguru.in
```bash
# On server 2 (or different port, e.g., 4344)
cd ~/Blog-Horizon
echo "REDIRECT_URI=https://horizon.kumaraguru.in/auth/callback" >> .env
# Update docker-compose.yml to use port 4344
docker-compose up -d
```

Then configure Nginx to proxy:
- `blogs.iqubekct.ac.in` → `localhost:4343`
- `horizon.kumaraguru.in` → `localhost:4344`

---

## ✅ Step 3: Update Environment Variables

### Current .env files needed:

#### For blogs.iqubekct.ac.in deployment:
```bash
DATABASE_URL=postgresql://postgres:your_password@db:5432/blogdb
SECRET_KEY=your-secret-key
CLIENT_ID=423dd38a-439a-4b99-a313-9472d2c0dad6
CLIENT_SECRET=your-client-secret
TENANT_ID=6b8b8296-bdff-4ad8-93ad-84bcbf3842f5
REDIRECT_URI=https://blogs.iqubekct.ac.in/auth/callback
ADMIN_EMAILS=nirosh@kct.ac.in,other@email.com
FLASK_ENV=production
PREFERRED_URL_SCHEME=https
```

#### For horizon.kumaraguru.in deployment:
```bash
DATABASE_URL=postgresql://postgres:your_password@db:5432/blogdb
SECRET_KEY=your-secret-key
CLIENT_ID=423dd38a-439a-4b99-a313-9472d2c0dad6
CLIENT_SECRET=your-client-secret
TENANT_ID=6b8b8296-bdff-4ad8-93ad-84bcbf3842f5
REDIRECT_URI=https://horizon.kumaraguru.in/auth/callback
ADMIN_EMAILS=nirosh@kct.ac.in,other@email.com
FLASK_ENV=production
PREFERRED_URL_SCHEME=https
```

---

## 🎯 Recommended Approach: Dynamic Detection (Single Deployment)

The best solution is to make the app **automatically detect** which domain is being used and adjust the redirect URI accordingly.

I'll update `auth.py` to:
1. Detect the incoming request domain (`request.host`)
2. Build the redirect URI dynamically
3. Work with both domains seamlessly

### Benefits:
- ✅ Single deployment
- ✅ Single database
- ✅ Works with any domain automatically
- ✅ No manual configuration per domain

---

## 🚦 Current Status Checklist

- [ ] **Azure Portal**: Add both redirect URIs
  - `https://blogs.iqubekct.ac.in/auth/callback`
  - `https://horizon.kumaraguru.in/auth/callback`

- [ ] **Code Update**: Implement dynamic redirect URI detection (I'll do this)

- [ ] **Nginx Configuration**: Ensure both domains proxy to the same Flask app

- [ ] **Test**: Try logging in from both domains

---

## 🧪 Testing After Setup

### Test Domain 1:
```bash
curl -I https://blogs.iqubekct.ac.in/
# Should redirect to Microsoft login
```

### Test Domain 2:
```bash
curl -I https://horizon.kumaraguru.in/
# Should redirect to Microsoft login
```

### Browser Test:
1. Visit `https://blogs.iqubekct.ac.in/` → Login → Should work ✅
2. Visit `https://horizon.kumaraguru.in/` → Login → Should work ✅

---

## 🆘 Troubleshooting Multi-Domain Issues

### Error: "redirect_uri_mismatch"
**Cause**: Azure Portal doesn't have the redirect URI for that domain

**Fix**: Add the missing URI in Azure Portal → Authentication

### Error: 400 Bad Request
**Cause**: App is using wrong REDIRECT_URI for the domain

**Fix**: Use dynamic detection (I'll implement this)

### Both domains show same content but only one works for login
**Cause**: Hardcoded REDIRECT_URI in `.env`

**Fix**: Switch to dynamic detection

---

## 📞 What I Need From You

**Please confirm:**

1. **Are both domains on the same server?**
   - Same server → Use dynamic detection (recommended)
   - Different servers → Use separate deployments

2. **Have you added both redirect URIs to Azure Portal?**
   - Go to Azure Portal and verify both URIs are listed

3. **Which domain do you want as primary?**
   - This helps me set the default if detection fails

Once you confirm, I'll implement the dynamic redirect URI detection! 🚀

