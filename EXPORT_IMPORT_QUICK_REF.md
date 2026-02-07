# Export/Import Quick Reference

## ✅ Tests Completed Successfully!

### Test Results (Feb 7, 2026)

**Export Test:** ✅ PASSED
- 4 posts exported
- 3 images encoded (79 KB total)
- Sample file created: `test_export_sample.xlsx`

**Import Test:** ✅ PASSED  
- All posts detected correctly
- Update logic working
- Image handling validated

---

## 📤 How to Export

1. Visit: `http://localhost:4343/admin/posts`
2. Click: **"Export to Excel"** (green button)
3. Download: `posts_export_YYYYMMDD_HHMMSS.xlsx`

**What you get:**
- All posts (published + draft)
- Images as base64 (if found)
- Original image paths preserved
- 16 columns of data

---

## 📥 How to Import

1. Visit: `http://localhost:4343/admin/posts`
2. Click: **"Import from Excel"** (yellow button)
3. Upload: Your `.xlsx` file
4. Result: "Import complete! Imported: X, Updated: Y, Skipped: Z"

**What happens:**
- New slugs → Creates new posts
- Existing slugs → Updates posts
- Missing fields → Skips rows

---

## 📊 Excel Structure (16 Columns)

| Column | Required | Example |
|--------|----------|---------|
| Slug | ✅ YES | `aravind-srinivas-perplexity-ai` |
| Title | ✅ YES | `The Startup Story...` |
| Month Key | ✅ YES | `2026-02` |
| Status | ✅ YES | `published` or `draft` |
| Is Featured | No | `Yes` or `No` |
| Hero Image Path | No | `/assets/imgs/news/news-1.jpg` |
| Hero Image (Base64) | No | `iVBORw0KGgo...` |
| ... | ... | ... |

---

## 🖼️ Image Handling

### On Export:
```
1. Searches for image in 3 locations
2. If found → Encodes to base64
3. Always preserves original path
```

### On Import:
```
IF "Hero Image Path" exists:
    ✅ Use that path (priority)
ELSE IF "Hero Image (Base64)" exists:
    ✅ Decode and save to /uploads/
```

**Result:** Images work whether you have paths or base64!

---

## ✅ Verification Checklist

### Before Export:
- [ ] All posts visible in admin panel
- [ ] Images displaying on site

### After Export:
- [ ] Excel has 16 columns
- [ ] Column H shows image paths
- [ ] All 4 posts present
- [ ] File size reasonable (~80 KB for your site)

### Before Import:
- [ ] Backup: Export current posts first!
- [ ] Verify: Required columns filled (Slug, Title, Month Key, Status)
- [ ] Check: No duplicate slugs (unless updating)

### After Import:
- [ ] Check result message
- [ ] Verify posts in admin panel
- [ ] Test: View a post to see content
- [ ] Confirm: Images displaying

---

## 🎯 Common Use Cases

### 1. Backup Posts
```
Export → Save file → Done!
Restore: Import the file
```

### 2. Move to New Site
```
Export from old site
Import to new site
Copy /assets/imgs/ if needed
```

### 3. Bulk Edit
```
Export → Edit in Excel → Save → Import
Updates all matching posts!
```

### 4. Share Content
```
Export → Share Excel file
Recipient imports to their site
```

---

## ⚠️ Important Notes

1. **Excel Cell Limit:** ~32,767 chars
   - Large images may be truncated
   - Path is always preserved (Column H)

2. **Slug Matching:**
   - Same slug = Update post
   - New slug = Create post

3. **Required Fields:**
   - Must have: Slug, Title, Month Key, Status
   - Missing = Row skipped

4. **Images:**
   - Path takes priority over base64
   - Both can exist (path used first)

---

## 📁 Sample Files

**In project root:**
- `test_export_sample.xlsx` (80 KB)
  - Real export from your database
  - All 4 posts included
  - Ready to test import

**Documentation:**
- `TEST_RESULTS.md` - Detailed test results
- `EXPORT_IMPORT_VERIFICATION.md` - Verification guide
- `POST_EXPORT_IMPORT_GUIDE.md` - Complete guide
- `EXPORT_IMPORT_FINAL.md` - Final summary

---

## 🚀 Ready to Use!

**Admin URL:** `http://localhost:4343/admin/posts`

**Test the feature:**
1. Click "Export to Excel" → Download file
2. Open in Excel → Check data
3. Make small edit → Save
4. Click "Import from Excel" → Upload
5. Check result message → Verify changes

---

## 📞 Need Help?

**Check logs:**
```powershell
docker logs blogki-web --tail 50
```

**Verify posts:**
```powershell
docker exec blogki-web python -c "from app import app; from models import Post; app.app_context().push(); posts = Post.query.all(); print(f'Posts: {len(posts)}')"
```

**Check images:**
```powershell
docker exec blogki-web ls -la /app/assets/imgs/news/
docker exec blogki-web ls -la /app/uploads/
```

---

**Status:** ✅ Feature is live and tested  
**Last Test:** Feb 7, 2026 - All passed  
**Sample File:** test_export_sample.xlsx (included)

🎉 **Ready for production use!**
