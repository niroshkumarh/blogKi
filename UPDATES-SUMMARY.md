# Updates Summary - Wide Angle Blog

## ✅ Changes Completed

### 1. **Site Name Changed from "Wonder List" to "Wide Angle"**

All references to "Wonder List" have been updated to "Wide Angle" across:

- ✅ **Homepage** (`category-grid.html`)
  - Page title
  - Main heading
  - Footer copyright

- ✅ **Blog 1** (`blog-1-aravind-srinivas.html`)
  - Page title
  - Logo alt text
  - Search placeholder
  - Footer section heading
  - Footer copyright

- ✅ **Blog 2** (`blog-2-vikram-arochamy.html`)
  - Page title
  - Logo alt text
  - Search placeholder
  - Footer section heading
  - Footer copyright

---

### 2. **YouTube Video Embed Added to Blog 1**

Instead of showing a plain text URL link, Blog 1 now features a **responsive YouTube embed player**.

**Before:**
```html
<p><strong>Watch here:</strong> <a href="https://www.youtube.com/" target="_blank">Aravind Srinivas on the Future of AI - YouTube</a></p>
```

**After:**
```html
<h3>Watch the conversation</h3>
<div class="wp-block-embed__wrapper" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 30px 0;">
    <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
<p class="font-small text-muted text-center"><em>Note: Replace the YouTube video ID in the embed code with the actual video you want to display</em></p>
```

**Features:**
- ✅ Fully responsive (16:9 aspect ratio maintained)
- ✅ Embedded player with controls
- ✅ Fullscreen support
- ✅ Clean integration with page design
- ✅ Note included for easy video ID replacement

---

## 📝 How to Replace the YouTube Video

To use your actual Aravind Srinivas video:

1. Get your YouTube video URL (e.g., `https://www.youtube.com/watch?v=ABC123xyz`)
2. Extract the video ID (the part after `v=`, so `ABC123xyz`)
3. Open `blog-1-aravind-srinivas.html`
4. Find this line:
   ```html
   src="https://www.youtube.com/embed/dQw4w9WgXcQ"
   ```
5. Replace `dQw4w9WgXcQ` with your actual video ID:
   ```html
   src="https://www.youtube.com/embed/ABC123xyz"
   ```
6. Save the file

---

## 🌐 Live URLs

- **Homepage:** `http://127.0.0.1:5500/` → Shows **Wide Angle**
- **Blog 1 (with YouTube):** `http://127.0.0.1:5500/blog-1-aravind-srinivas.html`
- **Blog 2:** `http://127.0.0.1:5500/blog-2-vikram-arochamy.html`

---

## 📋 Files Modified

1. `blog-1-aravind-srinivas.html` - Site name + YouTube embed
2. `blog-2-vikram-arochamy.html` - Site name only
3. `category-grid.html` - Site name only

---

## ✨ What's New

### Wide Angle Branding
- Professional blog name that suggests perspective and insight
- Consistent branding across all pages
- Updated in titles, headers, and footers

### YouTube Integration
- Professional embedded video player
- No external link clicks needed
- Better user engagement
- Maintains responsive design

---

## 🎯 Next Steps (Optional)

1. **Replace YouTube Video ID** with your actual Aravind Srinivas interview
2. **Update Logo** - Replace `assets/imgs/theme/logo.png` with "Wide Angle" logo
3. **Add More Posts** - Use the blog templates for additional content
4. **Customize Colors** - Update brand colors in CSS to match your style

---

**Updated:** December 31, 2025  
**Status:** ✅ All changes complete and tested

