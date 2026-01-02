# Authentication & Redirect Flow

## After Successful Login:

### For Normal Users (Non-Admin):
1. User logs in with Microsoft account
2. System checks if email is in `ADMIN_EMAILS` list
3. **If NOT admin** → Redirects to: `/archive/2026-01`
   - This is the **dynamic blog archive page** (equivalent to category-grid.html)
   - Shows all blog posts from January 2026
   - User can view posts, like, comment
4. Welcome message: "Welcome, [Name]!"

### For Admin Users:
1. User logs in with Microsoft account
2. System checks if email is in `ADMIN_EMAILS` list  
3. **If admin** (email: `nirosh@kct.ac.in`) → Redirects to: `/admin`
   - This is the **admin dashboard**
   - Shows statistics, analytics, user management
   - Can create/edit/delete posts
4. Welcome message: "Welcome back, [Name]! (Admin)"

## URL Structure:

| Old Static Site | New Dynamic App | Purpose |
|----------------|-----------------|---------|
| `category-grid.html` | `/archive/2026-01` | Blog post grid for January 2026 |
| `blog-1-aravind-srinivas.html` | `/post/aravind-srinivas-perplexity-ai` | Individual blog post |
| `blog-2-vikram-arochamy.html` | `/post/vikram-arochamy-amazon-innovation` | Individual blog post |
| N/A | `/admin` | Admin dashboard (new) |
| N/A | `/admin/posts` | Manage all posts (new) |
| N/A | `/admin/posts/new` | Create new post (new) |

## Admin Email Configuration:

Current admin: **nirosh@kct.ac.in**

To add more admins, update `.env` file:
```env
ADMIN_EMAILS=nirosh@kct.ac.in,another-admin@domain.com,third-admin@domain.com
```

## Testing:

1. **Test as Normal User:**
   - Log in with a non-admin Microsoft account
   - Should redirect to `/archive/2026-01` (blog grid)
   - Can view, like, and comment on posts

2. **Test as Admin:**
   - Log in with `nirosh@kct.ac.in`
   - Should redirect to `/admin` (dashboard)
   - Can access all admin features

## Features Available After Login:

### All Users Can:
- ✅ View all blog posts
- ✅ Read full articles
- ✅ Like posts (toggle heart icon)
- ✅ Add comments
- ✅ Delete own comments
- ✅ Browse by month archives
- ✅ View reading analytics (tracked in background)

### Admin Users Can Also:
- ✅ Access admin dashboard (`/admin`)
- ✅ View detailed statistics for all posts
- ✅ See who read each post, completion %, time spent
- ✅ View all user accounts
- ✅ Create new blog posts with WYSIWYG editor
- ✅ Edit existing posts
- ✅ Delete posts
- ✅ Upload images
- ✅ Schedule posts by date/time
- ✅ Organize posts by month
- ✅ Delete any user's comments


