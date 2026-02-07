# Export/Import Verification Guide

## How to Verify Export is Perfect for Import

### Step 1: Export Your Posts

1. Visit `http://localhost:4343/admin/posts`
2. Log in as admin
3. Click **"Export to Excel"** (green button)
4. Download the file: `posts_export_YYYYMMDD_HHMMSS.xlsx`

### Step 2: Check the Excel File Structure

Open the Excel file and verify it has these **16 columns** in order:

| # | Column Name | Required? | What to Check |
|---|-------------|-----------|---------------|
| 1 | ID | No | Should have post IDs (numbers) |
| 2 | Slug | **YES** | Must be unique, no empty values |
| 3 | Title | **YES** | Must have values, no empty |
| 4 | Month Key | **YES** | Format: YYYY-MM (e.g., 2026-01) |
| 5 | Published At | No | Format: YYYY-MM-DD HH:MM:SS |
| 6 | Status | **YES** | Either "published" or "draft" |
| 7 | Is Featured | No | Either "Yes" or "No" |
| 8 | Hero Image Path | No | Full path like `/assets/imgs/news/news-2.jpg` |
| 9 | Hero Image (Base64) | No | Long base64 string (if image found) |
| 10 | Hero Image Filename | No | Filename like `news-2.jpg` |
| 11 | HTML Content | No | Your post HTML |
| 12 | Excerpt | No | Short description |
| 13 | Category | No | Category name |
| 14 | Read Time | No | e.g., "5 min read" |
| 15 | Created At | No | Timestamp |
| 16 | Updated At | No | Timestamp |

### Step 3: Verify Required Fields

**Check each row to ensure:**

✅ **Slug** column: No empty cells, no duplicates  
✅ **Title** column: All cells filled  
✅ **Month Key** column: All cells in YYYY-MM format  
✅ **Status** column: All cells are either "published" or "draft"  

**Common Issues:**
- ❌ Empty slug → Import will skip that row
- ❌ Empty title → Import will skip that row
- ❌ Wrong Month Key format → Import may fail
- ❌ Status is not "published" or "draft" → Import may fail

### Step 4: Check Image Handling

The export now handles images in TWO ways:

1. **Hero Image Path** (Column H):
   - Contains the original path (e.g., `/assets/imgs/news/news-2.jpg`)
   - Used if image exists in your assets folder
   - **Priority on import**: If this column has a value, it will be used as-is

2. **Hero Image (Base64)** (Column I):
   - Contains base64-encoded image data (looks like: `iVBORw0KGgo...`)
   - Used for images that were found and encoded
   - **On import**: If "Hero Image Path" is empty, this will be decoded and saved to `/uploads/`

**Verification:**
- If you see a path in Column H but no base64 in Column I, it means the image wasn't found during export
- If you see both, the path takes priority on import
- If you see only base64 (no path), a new file will be created in `/uploads/` on import

### Step 5: Test Import

**Before importing:**
- ⚠️ **ALWAYS export first as backup**
- Don't modify the header row (row 1)
- Don't rename columns
- Keep required columns filled

**To test:**

1. Make a small change in Excel (e.g., edit a title)
2. Save the Excel file
3. Go to `http://localhost:4343/admin/posts`
4. Click **"Import from Excel"** (yellow button)
5. Upload the file
6. Check the result message

**Expected results:**
```
Import complete! Imported: 0, Updated: 4, Skipped: 0
```

- **Imported** = New posts created (new slugs)
- **Updated** = Existing posts updated (matching slugs)
- **Skipped** = Rows with errors or empty required fields

---

## What Was Fixed

### Issue 1: Images Not Exporting
**Problem:** Images in `/assets/imgs/` folder weren't being found because export only looked in `/uploads/`.

**Fix:** Export now tries multiple locations:
1. `/uploads/` folder
2. `/app/` + image path
3. Absolute path from database

### Issue 2: Image Path Lost on Import
**Problem:** Original image paths were lost when importing.

**Fix:** Added **"Hero Image Path"** column that preserves the original path.

**Import logic:**
```
IF "Hero Image Path" exists:
    Use that path directly
ELSE IF "Hero Image (Base64)" exists:
    Decode and save to /uploads/
    Set path to /uploads/filename
```

### Issue 3: Column Count Mismatch
**Problem:** 15 columns in export, but import expected different structure.

**Fix:** Now consistently 16 columns in both export and import.

---

## Troubleshooting

### Export says "Successfully exported N posts" but Excel is small

**Reason:** Images couldn't be found, so base64 columns are empty.

**Check:**
- Look at "Hero Image Path" column - are the paths correct?
- In Docker, run: `docker exec blogki-web ls -la /app/assets/imgs/news/`
- Verify image files exist at those paths

### Import says "0 Imported, 4 Updated" but I expected new posts

**Reason:** The slugs in your Excel match existing posts.

**Solution:**
- Change the slug column values to create new posts
- Or delete the ID column for rows you want as new posts

### Import says "Skipped: 5"

**Reason:** Those 5 rows had missing required fields.

**Check:**
- Are Slug, Title, Month Key, Status filled for all rows?
- Are there any blank rows in the Excel?
- Is Status either "published" or "draft"?

### Images not showing after import

**Case 1: You had "Hero Image Path"**
- The path was preserved
- Check if the image exists at that path in your new site
- If not, you need to copy the images manually OR use base64

**Case 2: You had base64**
- Image should be in `/uploads/` folder
- Check Docker: `docker exec blogki-web ls -la /app/uploads/`
- Check the post's `hero_image_path` in database

---

## Quick Verification Checklist

Before importing:

- [ ] Excel has 16 columns
- [ ] Header row is intact (row 1)
- [ ] All rows have Slug, Title, Month Key, Status filled
- [ ] No duplicate slugs (unless you want to update)
- [ ] Status values are only "published" or "draft"
- [ ] Month Key format is YYYY-MM
- [ ] If you want new posts, make sure slugs are unique

After importing:

- [ ] Check the import result message
- [ ] Visit `/admin/posts` to see the posts
- [ ] Click "View" on an imported post to check content
- [ ] Verify images are displaying
- [ ] Check if featured posts (Is Featured = Yes) are marked

---

## Advanced: Manual Verification

### Verify Export Logic (in Container)

```bash
docker exec blogki-web python -c "
from app import app
from models import Post
import os

with app.app_context():
    posts = Post.query.all()
    for post in posts:
        print(f'Post: {post.slug}')
        print(f'  Image path: {post.hero_image_path}')
        if post.hero_image_path:
            paths = [
                os.path.join('/app/uploads', os.path.basename(post.hero_image_path)),
                os.path.join('/app', post.hero_image_path.lstrip('/')),
                post.hero_image_path
            ]
            for p in paths:
                if os.path.exists(p):
                    print(f'  ✅ Found at: {p}')
                    break
            else:
                print(f'  ❌ Not found')
        print()
"
```

### Verify Import Success

```bash
docker exec blogki-web python -c "
from app import app
from models import Post

with app.app_context():
    posts = Post.query.all()
    print(f'Total posts: {len(posts)}')
    for post in posts:
        print(f'  - {post.slug}: {post.title[:40]}...')
"
```

---

## Summary

✅ **Export is ready** when:
- File has 16 columns
- "Hero Image Path" shows your original paths
- "Hero Image (Base64)" has data (if images were found)
- All 4 posts are in the Excel

✅ **Import will work** when:
- Required columns (Slug, Title, Month Key, Status) are filled
- No duplicate slugs (unless updating intentionally)
- Image handling is understood (path vs base64)

🎯 **Best practice**: Always export before import as backup!

---

*Last updated: Feb 7, 2026*
