# Audit Tracking & User Management Guide

## 🎯 Overview

Your magazine site now includes **comprehensive audit tracking** and **user role management** to track all content changes and control access levels.

---

## 🆕 New Features

### 1. **Audit Tracking**
Every content item now tracks:
- ✅ **Who created it** (Created By)
- ✅ **When it was created** (Created At)
- ✅ **Who last updated it** (Updated By)
- ✅ **When it was last updated** (Updated At)

**Applies to:**
- Posts
- Audio Episodes
- Series
- Videos
- Podcasts

### 2. **User Role Management**
Three role levels for access control:
- 🔴 **Admin**: Full access (create, edit, delete, manage users)
- 🔵 **Editor**: Can create and edit all content
- ⚫ **Viewer**: Read-only access to admin panel

### 3. **Enhanced DataTables**
- 📊 Show **ALL** posts (no pagination limit on data)
- 📥 Export to **CSV, Excel, PDF**
- 🖨️ Print functionality
- 📋 Copy to clipboard
- 🔍 Advanced search and filtering
- 📑 Sortable columns

---

## 🚀 Setup Instructions

### Step 1: Run Database Migration

```bash
# In Docker container
docker exec -it blogki-web bash
python migrate_add_audit_tracking.py
exit
```

**OR from Windows:**
```powershell
docker exec blogki-web python migrate_add_audit_tracking.py
```

This adds:
- `role` column to `users` table
- `created_by_id`, `updated_by_id` columns to all content tables

### Step 2: Restart Docker (if needed)

```bash
docker-compose restart web
```

### Step 3: Assign User Roles

1. Go to: `http://localhost:4343/admin/users`
2. You'll see all users
3. Use the dropdown to assign roles:
   - **Admin** for full access
   - **Editor** for content creators
   - **Viewer** for read-only users
4. Click **Update** to save

---

## 📖 How To Use

### Managing Users

1. **Access User Management:**
   ```
   Admin Panel → Users
   URL: /admin/users
   ```

2. **Assign Roles:**
   - Select role from dropdown
   - Click "Update"
   - User's access changes immediately

3. **View Statistics:**
   - See count of Admins, Editors, Viewers
   - Monitor last login times
   - Track user creation dates

### Viewing Audit History

#### **Posts List (Enhanced)**
1. Go to: `Admin Panel → Posts`
2. See ALL columns:
   - ID, Title, Slug, Month, Category
   - Status, Featured
   - **Created By** (who created)
   - **Created At** (timestamp)
   - **Updated By** (who last updated)
   - **Updated At** (timestamp)
   - Published date
   - View count

#### **Export Data**
- **CSV**: Click "CSV" button → Opens in Excel
- **Excel**: Click "Excel" button → Downloads .xlsx file
- **PDF**: Click "PDF" button → Generates PDF report
- **Print**: Click "Print" button → Print-friendly view
- **Copy**: Click "Copy" button → Copy to clipboard

#### **Search & Filter**
- Use search box to find posts by any column
- Click column headers to sort
- Change page length (10, 25, 50, 100)

### Tracking Content Changes

**When you create content:**
- System automatically records your user ID in `created_by_id`
- Timestamp saved in `created_at`

**When you edit content:**
- System automatically records your user ID in `updated_by_id`
- Timestamp updated in `updated_at`

**In the admin panel you'll see:**
```
Created By: John Smith (2026-01-18 10:30)
Updated By: Jane Doe (2026-01-18 14:45)
```

---

## 🔒 Role Permissions

### Admin Role
✅ Create posts/content  
✅ Edit posts/content  
✅ Delete posts/content  
✅ View stats and readers  
✅ Manage users  
✅ Assign roles  
✅ Full system access  

### Editor Role
✅ Create posts/content  
✅ Edit posts/content  
✅ View stats and readers  
❌ Delete posts (admins only)  
❌ Manage users (admins only)  

### Viewer Role
✅ View posts list  
✅ View stats  
❌ Create content  
❌ Edit content  
❌ Delete content  
❌ Manage users  

---

## 📊 DataTables Features

### Columns Shown (Posts)
1. **ID** - Post ID number
2. **Title** - Full post title
3. **Slug** - URL slug
4. **Month** - Issue month (YYYY-MM)
5. **Category** - Content category
6. **Status** - Published/Draft
7. **Featured** - Featured badge if featured
8. **Created By** - User who created (name + icon)
9. **Created At** - Creation timestamp
10. **Updated By** - Last editor (name + icon)
11. **Updated At** - Last update timestamp
12. **Published** - Publication date
13. **Views** - View count
14. **Actions** - View, Stats, Edit, Delete buttons

### Export Formats

**CSV Export:**
- Plain text, comma-separated
- Opens in Excel, Google Sheets
- Best for data analysis

**Excel Export:**
- .xlsx format
- Preserves formatting
- Best for reports

**PDF Export:**
- Landscape A4 format
- Print-ready
- Best for archiving

**Print:**
- Clean, printer-friendly layout
- Removes buttons/styling
- Best for physical copies

### Keyboard Shortcuts
- Type in search box → Filters instantly
- Click column header → Sort ascending/descending
- Click again → Reverse sort

---

## 🧪 Testing the System

### Test Audit Tracking

1. **Create a new post:**
   ```
   Admin Panel → New Post → Fill form → Create
   ```
   
2. **Check Posts List:**
   - Find your post
   - See your name in "Created By" column
   - Note the timestamp

3. **Edit the post:**
   ```
   Click Edit → Make changes → Save
   ```

4. **Check Posts List again:**
   - "Created By" stays the same
   - "Updated By" now shows your name
   - "Updated At" shows new timestamp

### Test Role Management

1. **Create a test editor:**
   ```
   Have someone login → Admin Panel → Users
   Find their name → Set role to "Editor" → Update
   ```

2. **Test editor access:**
   - Editor can create/edit posts ✅
   - Editor can see posts list ✅
   - Editor cannot manage users ❌

3. **Create a test viewer:**
   ```
   Set someone's role to "Viewer"
   ```

4. **Test viewer access:**
   - Viewer can see posts list ✅
   - Viewer cannot create posts ❌
   - Viewer cannot edit posts ❌

### Test DataTables Export

1. **Create multiple posts** (at least 5-10)
2. **Go to Posts List**
3. **Click "Excel" button**
4. **Check downloaded file:**
   - All posts included ✅
   - All columns present ✅
   - Created By/Updated By shown ✅
5. **Try PDF export:**
   - Landscape format ✅
   - All data visible ✅

---

## 🎯 Best Practices

### For Admins
1. ✅ Assign roles based on responsibility
2. ✅ Keep at least 2 admins for redundancy
3. ✅ Regularly export audit data for records
4. ✅ Review "Updated By" to track changes
5. ✅ Use viewer role for trainees/interns

### For Editors
1. ✅ Always review "Updated By" before editing
2. ✅ Communicate with other editors
3. ✅ Check timestamps to avoid conflicts
4. ✅ Use draft status for work-in-progress

### For All Users
1. ✅ Remember: all changes are tracked
2. ✅ Add meaningful content
3. ✅ Test in draft mode first
4. ✅ Export data regularly for backups

---

## 📈 Monitoring & Reports

### Weekly Audit Report
Export posts to Excel and check:
- Who created the most content?
- When was content last updated?
- Which posts need review?

### Monthly User Activity
Go to Users page and check:
- Who hasn't logged in recently?
- Are all roles appropriately assigned?
- Do we need more editors?

### Content Timeline
Sort Posts by "Created At":
- See content creation patterns
- Identify busy periods
- Plan content calendar

---

## ⚠️ Important Notes

### Existing Content
- Content created **before** migration will show `-` for Created By/Updated By
- Only **new** content and **edited** content will have tracking
- This is normal and expected

### Role Changes
- Role changes take effect **immediately**
- User doesn't need to log out/in
- Next page load will use new permissions

### Data Export
- Export includes ALL posts (no limit)
- Large exports may take a few seconds
- PDF works best with <100 posts per page

### Privacy
- Only admins can see Users page
- Audit data stays internal (not shown to public)
- User emails are visible to admins only

---

## 🛠️ Troubleshooting

### "Column not found" error
```bash
# Re-run migration
docker exec blogki-web python migrate_add_audit_tracking.py
```

### Audit data not showing
- Check you're logged in (tracking needs user session)
- Migration must be run first
- Try creating **new** content to test

### Export buttons not working
- Check browser console for JavaScript errors
- Verify jQuery and DataTables are loading
- Try hard refresh (Ctrl + Shift + R)

### Role changes not working
- Verify you're logged in as Admin
- Check database: `SELECT email, role FROM users;`
- Restart Docker if needed

---

## 📞 Support

### Need Help?
1. Check this guide first
2. Review error logs: `docker-compose logs web`
3. Test with a simple case first
4. Document the issue clearly

### Feature Requests?
Current system supports:
- Audit tracking ✅
- Role management ✅
- DataTables with export ✅

Future possibilities:
- Email notifications on changes
- Detailed change logs (before/after)
- Content approval workflows
- Scheduled publishing

---

## ✅ Checklist

**Setup Complete?**
- [ ] Migration run successfully
- [ ] Users page accessible
- [ ] Roles assigned
- [ ] Posts list shows audit columns
- [ ] Export buttons work
- [ ] Test user created content
- [ ] Audit tracking verified

**Ready to Use!** 🎉
