# 🔐 Azure Portal Setup for Multi-Domain Configuration

## Critical Step: Add Both Redirect URIs

Your blog is accessible via **TWO domains**, so Azure must trust both.

---

## 📋 Step-by-Step Instructions

### 1. Go to Azure Portal

Visit: **https://portal.azure.com**

### 2. Navigate to App Registration

1. Click **Microsoft Entra ID** (in left sidebar or search)
2. Click **App registrations**
3. Find and click your app (Client ID: `423dd38a-439a-4b99-a313-9472d2c0dad6`)

### 3. Add Redirect URIs

1. Click **Authentication** (left sidebar)
2. Under **Platform configurations**, find the **Web** platform
3. Click **Add URI** (you'll need to do this twice - once for each domain)

**Add these TWO URIs:**

```
https://blogs.iqubekct.ac.in/auth/callback
```

```
https://HORIZON.kumaraguru.in/auth/callback
```

### 4. Configure Additional Settings

In the same **Authentication** page:

#### Implicit grant and hybrid flows (if prompted)
- ✅ Check: **ID tokens (used for implicit and hybrid flows)**

#### Advanced settings
- **Allow public client flows**: No
- **Enable the following mobile and desktop flows**: No

### 5. Save Changes

Click **Save** at the top of the page.

---

## ✅ Verification

After saving, you should see:

**Platform configurations → Web:**
- Redirect URIs: **2**
  - `https://blogs.iqubekct.ac.in/auth/callback`
  - `https://HORIZON.kumaraguru.in/auth/callback`

---

## 🎯 Expected Result

Once configured:
- ✅ Users visiting **blogs.iqubekct.ac.in** can log in
- ✅ Users visiting **HORIZON.kumaraguru.in** can log in
- ✅ No more "redirect_uri_mismatch" errors
- ✅ No more "400 Bad Request" errors

---

## 📸 Screenshot Guide

Here's what you should see:

```
Azure Portal → Entra ID → App registrations → Your App → Authentication

┌─────────────────────────────────────────────────────────────┐
│ Platform configurations                                      │
├─────────────────────────────────────────────────────────────┤
│ Web                                                          │
│   Redirect URIs: 2                                           │
│                                                              │
│   • https://blogs.iqubekct.ac.in/auth/callback              │
│   • https://HORIZON.kumaraguru.in/auth/callback             │
│                                                              │
│   [Add URI]                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### "I can't find my App Registration"

**Search by:**
- Client ID: `423dd38a-439a-4b99-a313-9472d2c0dad6`
- Or look in: **Owned applications** tab

### "I can only add one URI"

Click **Add URI** again to add the second one. You can have multiple URIs.

### "The URIs are grayed out"

You might not have permission. Contact your Azure administrator:
- Required role: **Application Administrator** or **Cloud Application Administrator**

### "Save button is disabled"

Make sure:
- ✅ Both URIs use `https://` (not `http://`)
- ✅ Both URIs end with `/auth/callback`
- ✅ No trailing slashes after `callback`

---

## 🔄 After Adding URIs

### Next Steps:

1. **Deploy the updated code** (with dynamic redirect URI detection)
2. **Test both domains:**
   - `https://blogs.iqubekct.ac.in/` → Should log in ✅
   - `https://HORIZON.kumaraguru.in/` → Should log in ✅

### Clear browser cache before testing:
- Press `Ctrl+Shift+Delete`
- Select "Cookies and other site data"
- Clear and try again

---

## 📞 Need Help?

If you're getting errors after setup:

1. **Verify URIs are saved:** Go back to Azure Portal → Authentication and confirm both URIs are listed
2. **Check capitalization:** Azure is case-sensitive for URIs
3. **Wait 1-2 minutes:** Sometimes Azure takes time to propagate changes
4. **Clear browser cookies:** Old cookies can cause issues

---

## 🚀 Ready to Test?

Once you've added both URIs in Azure Portal:

1. **Commit and push the updated code** (I've updated `auth.py` with dynamic detection)
2. **Deploy to production server**
3. **Test both domains**

Let me know when you've added the URIs, and I'll help you deploy! 🎉

