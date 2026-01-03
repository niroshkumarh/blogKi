# Read Tracking Debug Guide

## Issue: Logged-in User Reads Not Showing Up

If you've logged in as **iqube@kct.ac.in** and viewed posts but don't see your reads in the admin panel, follow these debugging steps.

---

## 🔍 **Step 1: Deploy Latest Changes**

First, ensure you have the latest code with debugging enabled:

```bash
# Pull latest changes
git pull origin docker-postgres-analytics

# Restart Docker
docker-compose restart web
```

---

## 🧪 **Step 2: Test Read Tracking in Browser**

### **Open Browser Console**
1. Open any blog post (e.g., `http://localhost:4343/post/your-post-slug`)
2. Open **Developer Tools** (Press `F12`)
3. Go to **Console** tab

### **What You Should See**

Within 3-5 seconds, you should see these console messages:

```
🆔 Generated new anon_id: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
📖 Read tracking initialized for post: 3
📤 Sending read event: 25%, 3s, anon_id=xxxxxxxx...
✅ Read event tracked successfully!
   Tracked as: logged_in
   User ID: 1
   Anon ID: xxxxxxxx...
```

### **Key Things to Check**

✅ **"Tracked as: logged_in"** - You're being tracked as a logged-in user  
✅ **"User ID: X"** - Your user ID is being captured  
✅ **"Anon ID: xxxxxxxx..."** - Anonymous ID is also captured (for cross-session tracking)

### **If You See "Tracked as: anonymous"**

This means the session is not working. Possible causes:
- Cookies are blocked
- Session expired
- Different domain/port for API vs web

---

## 📊 **Step 3: Check Server Logs**

Check Docker logs to see server-side tracking:

```bash
docker-compose logs web --tail 50 | grep "Read event"
```

You should see:
```
📊 Read event: post_id=3, user_id=1, anon_id=xxxxxxxx..., percent=25%, seconds=3s
```

If `user_id=None`, the session is not being passed to the API.

---

## 🔍 **Step 4: Check Database Directly**

Verify events are being saved:

```bash
# Connect to database
docker exec -it blogki-db psql -U bloguser -d blogsite

# Check recent read events
SELECT id, post_id, user_id, anon_id, percent, seconds, created_at 
FROM read_events 
ORDER BY created_at DESC 
LIMIT 10;
```

### **What to Look For**

✅ **user_id is NOT NULL** - You're logged in  
✅ **anon_id is filled** - Cookie tracking works  
✅ **created_at is recent** - Events are being saved

### **If user_id is NULL for all events**

This means session is not working. Try:
1. Clear browser cookies
2. Log out and log back in
3. Check if cookies are enabled

---

## 👤 **Step 5: Check User Table**

Verify your user exists in the database:

```bash
# In psql (from Step 4)
SELECT id, email, name FROM users WHERE email = 'iqube@kct.ac.in';
```

You should see:
```
 id |      email        |  name  
----+-------------------+--------
  1 | iqube@kct.ac.in   | iQube
```

**Note the `id`** - this should match the `user_id` in read_events.

---

## 📋 **Step 6: Check Admin Readers Page**

Go to: `http://localhost:4343/admin/readers`

### **If You See Your Name**
✅ Everything is working! Click "View Details" to see your reading history.

### **If You Don't See Your Name**

1. **Check the filter** - Make sure "Filter by Post" is set to "All Posts"
2. **Check the query** - The admin page might have a query issue
3. **Refresh the page** - Sometimes caching can cause issues

---

## 🐛 **Common Issues & Fixes**

### **Issue 1: Session Not Working**

**Symptoms:**
- Console shows "Tracked as: anonymous" even when logged in
- user_id is NULL in database

**Fix:**
```bash
# Restart Flask to reset sessions
docker-compose restart web

# Clear browser cookies and log in again
```

### **Issue 2: Events Saved but Not Showing in Admin**

**Symptoms:**
- Database has events with your user_id
- Admin page shows 0 readers

**Fix:**
Check the SQL query in `admin.py`:

```bash
# In psql, run the same query as admin:
SELECT 
    u.id, u.email, u.name,
    COUNT(DISTINCT re.post_id) as posts_read,
    COUNT(re.id) as total_events
FROM users u
JOIN read_events re ON re.user_id = u.id
WHERE u.email = 'iqube@kct.ac.in'
GROUP BY u.id, u.email, u.name;
```

If this returns results but admin doesn't show them, it's a Python/Flask issue.

### **Issue 3: Cookie Not Setting**

**Symptoms:**
- Console shows error about missing anon_id
- No cookie named `hzn_anon_id`

**Check Cookies:**
1. Open DevTools → Application tab → Cookies
2. Look for `hzn_anon_id` cookie
3. If missing, check browser settings allow cookies

**Fix:**
```javascript
// In browser console, manually set cookie:
document.cookie = "hzn_anon_id=test-12345; path=/; max-age=31536000";
```

Then refresh the page.

---

## ✅ **Step 7: Test Complete Flow**

Follow these steps in order:

1. **Clear everything:**
   ```bash
   # Clear browser cache and cookies
   # Ctrl+Shift+Delete in most browsers
   ```

2. **Log in fresh:**
   - Go to `http://localhost:4343/`
   - Click "Login"
   - Sign in as iqube@kct.ac.in

3. **Open a post:**
   - Click on any blog post
   - Open console (F12)
   - **Wait 3-5 seconds**

4. **Verify console output:**
   ```
   ✅ Read event tracked successfully!
      Tracked as: logged_in
      User ID: 1
   ```

5. **Wait 30 seconds** (for second event)

6. **Check admin:**
   - Go to `http://localhost:4343/admin/readers`
   - You should see your name in the list!

---

## 📝 **Manual Debugging Queries**

### **Count Events by User**
```sql
SELECT 
    CASE 
        WHEN user_id IS NOT NULL THEN 'Logged In'
        ELSE 'Anonymous'
    END as type,
    COUNT(*) as event_count
FROM read_events
GROUP BY type;
```

### **Find Your Events**
```sql
SELECT 
    re.id,
    re.post_id,
    p.title,
    re.percent,
    re.seconds,
    re.created_at
FROM read_events re
JOIN posts p ON p.id = re.post_id
WHERE re.user_id = (SELECT id FROM users WHERE email = 'iqube@kct.ac.in')
ORDER BY re.created_at DESC;
```

### **Check Session Issues**
```sql
-- See all events with user_id
SELECT COUNT(*) FROM read_events WHERE user_id IS NOT NULL;

-- See all events without user_id  
SELECT COUNT(*) FROM read_events WHERE user_id IS NULL;
```

---

## 🚨 **If Nothing Works**

### **Nuclear Option: Fresh Test**

1. **Create a test post:**
   - Go to Admin → New Post
   - Title: "Test Tracking"
   - Status: Published
   - Save

2. **Test as anonymous:**
   - Open an **incognito window**
   - Go to the test post
   - Open console
   - Verify tracking works (should see "Tracked as: anonymous")

3. **Test as logged-in:**
   - In **normal window**, log in
   - Go to the test post  
   - Open console
   - Verify tracking works (should see "Tracked as: logged_in" with your User ID)

4. **Check database:**
   ```sql
   SELECT user_id, anon_id, post_id, created_at 
   FROM read_events 
   WHERE post_id = (SELECT id FROM posts WHERE slug = 'test-tracking')
   ORDER BY created_at DESC;
   ```

You should see:
- One row with `user_id = NULL` (anonymous)
- One row with `user_id = your_id` (logged in)

---

## 📞 **Still Not Working?**

If after all these steps you still don't see your reads, provide me with:

1. **Console output** (screenshot or copy/paste)
2. **Server logs:**
   ```bash
   docker-compose logs web --tail 100 | grep -E "(Read event|Track|Session)"
   ```
3. **Database query results:**
   ```sql
   SELECT * FROM read_events WHERE user_id IS NOT NULL LIMIT 5;
   ```

This will help me diagnose the exact issue!

---

**Last Updated**: January 2026  
**Related Files**: `api.py`, `templates/post.html`, `admin.py`

