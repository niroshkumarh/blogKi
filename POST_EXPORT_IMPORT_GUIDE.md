# Post Export/Import Feature Guide

## Overview

The blog platform now includes a complete **Export/Import** feature that allows you to easily migrate posts between different instances of the blog site. All post data, including images, is exported to an Excel file with images encoded as base64.

---

## Features

### ✅ What Gets Exported

All post fields are exported to an Excel (.xlsx) file:

- **Basic Info**: ID, Slug, Title, Month Key, Status
- **Dates**: Published At, Created At, Updated At
- **Content**: HTML Content, Excerpt, Category
- **Images**: Hero Image (as base64), Hero Image Filename
- **Metadata**: Read Time, Is Featured flag

### ✅ What Gets Imported

The import process:
- Creates new posts if the slug doesn't exist
- Updates existing posts if the slug matches
- Decodes and saves base64 images to the uploads folder
- Validates required fields (Slug, Title, Month Key, Status)
- Provides detailed feedback (imported/updated/skipped counts)

---

## How to Use

### 1. Exporting Posts

1. Go to **Admin Panel** → **Posts** (`/admin/posts`)
2. Click the **"Export to Excel"** button (green button)
3. An Excel file will be downloaded: `posts_export_YYYYMMDD_HHMMSS.xlsx`

**Note**: 
- All published and draft posts are exported
- Images are embedded as base64 in the Excel file
- The file can be large if you have many high-resolution images

### 2. Importing Posts

1. Go to **Admin Panel** → **Posts** (`/admin/posts`)
2. Click the **"Import from Excel"** button (yellow button)
3. OR navigate directly to `/admin/posts/import`
4. Select your Excel file (.xlsx)
5. Click **"Import Posts"**

**Important**:
- ⚠️ Always export your current posts as a backup before importing
- The import will update existing posts (matched by slug)
- New posts will be created for slugs that don't exist

---

## Excel File Structure

The exported Excel file has the following columns:

| Column | Description | Required | Notes |
|--------|-------------|----------|-------|
| ID | Post ID | No | Auto-assigned for new posts |
| Slug | URL slug | **Yes** | Must be unique |
| Title | Post title | **Yes** | - |
| Month Key | Archive month | **Yes** | Format: YYYY-MM |
| Published At | Publication date | No | Format: YYYY-MM-DD HH:MM:SS |
| Status | Post status | **Yes** | `published` or `draft` |
| Is Featured | Featured flag | No | `Yes` or `No` |
| Hero Image (Base64) | Image data | No | Base64 encoded |
| Hero Image Filename | Original filename | No | Used when decoding base64 |
| HTML Content | Post body | No | Full HTML content |
| Excerpt | Short description | No | - |
| Category | Post category | No | - |
| Read Time | Estimated read time | No | e.g., "5 min read" |
| Created At | Creation timestamp | No | Auto-assigned for new posts |
| Updated At | Last update timestamp | No | Auto-updated |

---

## Use Cases

### 1. Site-to-Site Migration

Move your entire blog to a new domain or hosting:

1. Export all posts from the old site
2. Set up the new site with the same database schema
3. Import the Excel file to the new site
4. All posts, including images, will be transferred

### 2. Backup and Restore

Create periodic backups:

1. Export posts monthly/weekly
2. Store Excel files securely
3. Restore quickly if needed by importing the file

### 3. Bulk Editing

Make bulk changes in Excel:

1. Export posts
2. Edit in Excel (e.g., change categories, update excerpts)
3. Import the modified file
4. All matching posts will be updated

### 4. Content Sharing

Share content between multiple blog instances:

1. Export specific posts
2. Delete unwanted rows in Excel
3. Import into another site instance

---

## Technical Details

### Dependencies

The feature requires:
- `openpyxl==3.1.2` - For Excel file operations
- `Pillow==10.2.0` - For image processing (if needed)

Both are included in `requirements.txt`.

### Image Handling

**Export Process**:
1. Reads the hero image file from the `uploads/` folder
2. Encodes the binary data as base64
3. Stores the base64 string in the Excel cell

**Import Process**:
1. Decodes the base64 string
2. Saves the binary data to `uploads/` folder
3. Updates the post's `hero_image_path` with the file path

**Note**: Base64 encoding increases file size by ~33%, but ensures portability without needing separate image files.

### Error Handling

The import process is resilient:
- **Invalid rows**: Skipped with a count
- **Missing images**: Logged as errors, but post is still imported
- **Duplicate slugs**: Existing post is updated
- **Database errors**: Transaction is rolled back, no partial imports

---

## Routes

### Export Route

```
GET /admin/posts/export
```

**Access**: Admin only  
**Returns**: Excel file download  
**File naming**: `posts_export_YYYYMMDD_HHMMSS.xlsx`

### Import Route

```
GET /admin/posts/import (show form)
POST /admin/posts/import (process upload)
```

**Access**: Admin only  
**Accepts**: `.xlsx` files only  
**Form field**: `file` (multipart/form-data)

---

## Best Practices

1. **Always Backup First**: Export your current posts before importing to avoid accidental overwrites
2. **Test with Small Files**: For large migrations, test with a few posts first
3. **Check Required Fields**: Ensure Slug, Title, Month Key, and Status are filled in all rows
4. **Image Quality**: Large images will create large Excel files; consider optimizing images before export
5. **Unique Slugs**: Duplicate slugs will cause updates, not new posts
6. **Date Formats**: Stick to the exported date format (YYYY-MM-DD HH:MM:SS)

---

## Troubleshooting

### Import Fails with "Missing required column"

**Solution**: The Excel file must contain the columns: Slug, Title, Month Key, Status. Don't rename or delete these columns.

### Images Not Importing

**Solution**: 
- Ensure the "Hero Image (Base64)" and "Hero Image Filename" columns are present
- Check if the base64 string is valid (not corrupted)
- Check Docker logs for image decoding errors

### Import Says "0 Imported, 10 Updated" But I Expected New Posts

**Solution**: The slugs in your Excel file match existing posts. Change the slugs to create new posts instead.

### Excel File is Very Large (>50MB)

**Solution**: 
- You have many posts with high-resolution images
- This is normal; Excel can handle it, but it may be slow to open
- Consider exporting in batches by filtering posts in the admin first (future enhancement)

---

## Future Enhancements

Potential improvements:
- Export only selected posts (checkboxes)
- Export only specific date ranges
- CSV format support (lighter than Excel)
- JSON export option
- Import progress bar for large files
- Image compression before base64 encoding
- Support for post comments and likes in export

---

## Security Notes

- 🔒 Export/Import routes are protected by `@admin_required` decorator
- 🔒 Only `.xlsx` files are accepted for import
- 🔒 Filenames are sanitized with `secure_filename()`
- 🔒 Database transactions are used (rollback on error)
- 🔒 File uploads go to the configured `UPLOAD_FOLDER` only

---

## Summary

The Export/Import feature provides a robust, Excel-based solution for:
- Migrating posts between sites
- Creating backups
- Bulk editing content
- Sharing content between instances

All with images embedded as base64 for maximum portability.

**Access the feature**: Admin Panel → Posts → Export/Import buttons

---

*Last updated: Feb 7, 2026*
