# Import Page Flash Message Fix

## Issue

When visiting the import page (`/admin/posts/import`), users were seeing:
```
"Successfully exported 4 posts to Excel"
```

This message appeared even before selecting any file to import.

## Root Cause

**Problem 1: Flask Flash Message Persistence**
- Export page called: `flash('Successfully exported...', 'success')`
- Flash messages persist across the next request
- When user clicked "Import from Excel" button, they navigated to import page
- The old export message was still in the session and displayed

**Problem 2: Template Block Mismatch**
- Base template uses: `{% block content %}`
- Import template used: `{% block admin_content %}`
- This mismatch prevented the page from rendering properly

## Solution Applied

### Fix 1: Removed Flash Message from Export
**File:** `admin.py` - `posts_export()` function

**Before:**
```python
flash(f'Successfully exported {len(posts)} posts to Excel', 'success')
return send_file(...)
```

**After:**
```python
# Don't flash message - it will show on the download page
# flash(f'Successfully exported {len(posts)} posts to Excel', 'success')
return send_file(...)
```

**Reason:** 
- Export triggers a file download, user doesn't stay on any page
- Flash message was persisting to next page visited (import page)
- No need for flash message since download is the confirmation

### Fix 2: Corrected Template Block Name
**File:** `templates/admin/posts_import.html`

**Before:**
```html
{% block admin_content %}
```

**After:**
```html
{% block content %}
```

**Reason:** Must match the block name in base template

## Testing

**Before Fix:**
1. Visit `/admin/posts`
2. Click "Export to Excel"
3. Click "Import from Excel"
4. ❌ See: "Successfully exported 4 posts to Excel" (wrong message)

**After Fix:**
1. Visit `/admin/posts`
2. Click "Export to Excel"
3. File downloads (no flash message)
4. Click "Import from Excel"
5. ✅ See: Only the import form instructions (correct)

## Additional Notes

Flash messages are appropriate for:
- ✅ Import completion: "Import complete! Imported: X, Updated: Y, Skipped: Z"
- ✅ Error messages: "Import failed: ..."
- ✅ Actions that stay on a page

Flash messages are NOT appropriate for:
- ❌ File downloads (user leaves the page immediately)
- ❌ Actions where the result is obvious (download started)

## Status

✅ Fixed and deployed
- Container restarted with changes
- Import page now shows only import form
- Export still works, just without flash message

---

*Fixed: Feb 7, 2026*
