# ⭐ Featured Posts - Implementation Guide

## Overview
Added **Featured Posts** functionality with:
1. ✅ **Featured toggle** in Admin editor
2. ✅ **Auto-scrolling carousel** on archive page
3. ✅ **Database column** for marking posts as featured

---

## ✅ Changes Made

### 1. **Database Schema** (`models.py`)
```python
is_featured = db.Column(db.Boolean, default=False, index=True)
```
- Added `is_featured` column to Post model
- Indexed for faster queries
- Defaults to `False` (not featured)

### 2. **Admin Editor** (`templates/admin/post_edit.html`)
Added Featured toggle in the "Publish" section:

```html
<div class="custom-control custom-switch">
    <input type="checkbox" id="is_featured" name="is_featured" 
           {{ 'checked' if post and post.is_featured else '' }}>
    <label for="is_featured">
        <strong>⭐ Featured Post</strong>
        <br><small>Show in featured carousel on archive page</small>
    </label>
</div>
```

**Location:** Right after the Status dropdown

### 3. **Admin Backend** (`admin.py`)
Updated both `post_new()` and `post_edit()` functions:

```python
# Get featured status from checkbox
is_featured = request.form.get('is_featured') == 'on'

# Save to post
post.is_featured = is_featured
```

### 4. **Archive Route** (`app.py`)
Updated to query only featured posts:

```python
# Get only posts marked as featured
featured_posts = Post.query.filter_by(
    month_key=month_key, 
    status='published', 
    is_featured=True
).order_by(Post.published_at.desc()).limit(5).all()
```

**Limits:** Up to 5 featured posts per month

### 5. **Auto-Scroll Carousel** (`templates/archive.html`)
Added Slick carousel with auto-scroll:

```javascript
$('.slide-fade').slick({
    dots: true,
    infinite: true,
    speed: 800,
    fade: true,
    autoplay: true,
    autoplaySpeed: 5000,  // 5 seconds per slide
    arrows: true,
    pauseOnHover: true,
    pauseOnFocus: true
});
```

**Features:**
- ✅ Auto-scrolls every 5 seconds
- ✅ Smooth fade transition (800ms)
- ✅ Dots navigation
- ✅ Arrow navigation
- ✅ Pauses on hover
- ✅ Infinite loop

---

## 🚀 How to Use

### Step 1: Run Migration
Add the `is_featured` column to existing database:

```bash
# In Docker:
docker exec -it blogki-web python migrate_add_featured_column.py

# Or locally:
python migrate_add_featured_column.py
```

### Step 2: Mark Posts as Featured

1. Go to **Admin → Posts** (`/admin/posts`)
2. Click **Edit** on any post
3. In the **Publish** section, you'll see:
   ```
   ⭐ Featured Post
   Show in featured carousel on archive page
   ```
4. **Check the box** to mark as featured
5. Click **Update Post**

### Step 3: View Featured Carousel

1. Go to archive page: `/archive/2026-01`
2. You'll see the **Featured Posts carousel** at the top
3. It will auto-scroll through all featured posts
4. Hover to pause, click arrows to navigate manually

---

## 📊 Featured Posts Display

### Archive Page Layout

```
┌────────────────────────────────────────────┐
│     HORIZON Header                         │
└────────────────────────────────────────────┘

┌─────────────────────────────┐  ┌──────────┐
│                             │  │          │
│   FEATURED CAROUSEL         │  │  Post    │
│   (Auto-scrolls)            │  │  Cards   │
│   ⭐ Featured Post 1         │  │          │
│   ⭐ Featured Post 2         │  └──────────┘
│   ...                       │  
│   [Dots] [←] [→]            │  ┌──────────┐
│                             │  │  Post    │
└─────────────────────────────┘  │  Cards   │
                                 └──────────┘
```

### Carousel Features

| Feature | Details |
|---------|---------|
| **Auto-scroll** | Every 5 seconds |
| **Transition** | Smooth fade (800ms) |
| **Controls** | Dots + Arrows |
| **Behavior** | Pauses on hover |
| **Max Posts** | 5 featured posts |
| **Looping** | Infinite |

---

## 🎯 Featured Posts Criteria

### What Makes a Good Featured Post?

1. **High Quality** - Well-written, engaging content
2. **Visual Appeal** - Has an attractive hero image
3. **Recent** - Current or timely topics
4. **Popular** - High likes/comments (optional)
5. **Representative** - Showcases best content

### Recommended Number

- **Minimum:** 2-3 featured posts per month
- **Maximum:** 5 featured posts per month
- **Optimal:** 3 featured posts

### Auto-Selection (Future Enhancement)

Currently manual selection. Could auto-feature based on:
- Most likes in past week
- Most comments
- Highest read completion rate

---

## 🎨 Carousel Styling

### Default Theme (Dark Overlay)

```css
.post-thumb {
    position: relative;
    background-size: cover;
    height: 450px;
}

.post-content-overlay {
    position: absolute;
    bottom: 0;
    color: white;
    background: linear-gradient(transparent, rgba(0,0,0,0.8));
}

.top-left-icon {
    position: absolute;
    top: 20px;
    left: 20px;
    background: #ffc107;  /* Warning yellow */
}
```

### Customization Options

**Change auto-scroll speed:**
```javascript
autoplaySpeed: 3000,  // 3 seconds (faster)
// or
autoplaySpeed: 7000,  // 7 seconds (slower)
```

**Disable auto-scroll:**
```javascript
autoplay: false,
```

**Change transition effect:**
```javascript
fade: false,  // Use slide instead of fade
slidesToShow: 1,
slidesToScroll: 1,
```

---

## 📱 Responsive Behavior

### Desktop (> 992px)
- Carousel: 8 columns (66% width)
- Auto-scroll: Every 5 seconds
- Shows all controls

### Tablet (768px - 992px)
- Carousel: Full width (12 columns)
- Auto-scroll: Continues
- Touch-friendly controls

### Mobile (< 768px)
- Carousel: Full width
- Auto-scroll: Every 6 seconds (slower)
- Swipe gestures enabled
- Simplified controls

---

## 🔍 Troubleshooting

### No Featured Posts Showing?

**Check:**
1. ✅ At least one post has `is_featured = True`
2. ✅ Post is `published` (not draft)
3. ✅ Post matches the current `month_key`
4. ✅ Migration script was run

**Debug:**
```python
# In Flask shell or admin route
featured = Post.query.filter_by(is_featured=True).all()
print(f"Featured posts: {len(featured)}")
for post in featured:
    print(f"  - {post.title} (month: {post.month_key})")
```

### Carousel Not Auto-Scrolling?

**Check:**
1. ✅ Slick carousel JS is loaded (check Network tab)
2. ✅ jQuery is loaded before Slick
3. ✅ No JavaScript errors in console
4. ✅ `.slide-fade` class exists on carousel

**Fix:**
```javascript
// Hard refresh browser
Ctrl + Shift + R

// Check console
console.log('Slick loaded:', typeof $.fn.slick !== 'undefined');
```

### Migration Failed?

**SQLite Error:**
```bash
# Check current schema
sqlite3 instance/blogsite.db ".schema post"

# If column exists, no need to migrate
# If not, run migration again
```

**PostgreSQL:**
```sql
-- Check if column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='post' AND column_name='is_featured';

-- Add manually if needed
ALTER TABLE post ADD COLUMN is_featured BOOLEAN DEFAULT FALSE;
```

---

## 💡 Usage Tips

### For Content Creators

1. **Feature Your Best** - Only feature high-quality posts
2. **Rotate Regularly** - Update featured posts monthly
3. **Hero Images** - Featured posts should have great images
4. **Balance Topics** - Mix different categories
5. **Test First** - Preview before publishing

### For Administrators

1. **Limit Featured Posts** - 3-5 per month max
2. **Monitor Performance** - Track clicks on featured posts
3. **Update Seasonally** - Refresh featured content
4. **Check Mobile** - Ensure carousel works on phones
5. **Analytics** - Track which featured posts get most engagement

---

## 🔮 Future Enhancements

### Potential Additions

1. **Auto-feature by popularity**
   - Most liked posts
   - Most commented posts
   - Highest completion rate

2. **Scheduled featured**
   - Feature for specific date range
   - Auto-expire featured status

3. **Featured order**
   - Drag-and-drop reordering
   - Priority/weight system

4. **Featured analytics**
   - Track carousel impressions
   - Measure click-through rate
   - A/B test different posts

5. **Multiple carousels**
   - "Editor's Picks"
   - "Most Popular"
   - "Trending Now"

---

## 📦 Files Modified

| File | Changes |
|------|---------|
| `models.py` | Added `is_featured` column |
| `app.py` | Updated archive route to query featured posts |
| `admin.py` | Added featured checkbox handling (2 functions) |
| `templates/admin/post_edit.html` | Added featured toggle UI |
| `templates/archive.html` | Added Slick carousel auto-scroll |
| `migrate_add_featured_column.py` | New migration script |

---

## ✅ Testing Checklist

### Database
- [ ] Migration script runs without errors
- [ ] `is_featured` column exists in post table
- [ ] Default value is `False`

### Admin Panel
- [ ] Featured checkbox appears in post editor
- [ ] Checkbox saves correctly on new post
- [ ] Checkbox saves correctly on edit post
- [ ] Checkbox state persists after save

### Archive Page
- [ ] Featured carousel appears when posts exist
- [ ] Only featured posts show in carousel
- [ ] Carousel auto-scrolls every 5 seconds
- [ ] Dots navigation works
- [ ] Arrow navigation works
- [ ] Hover pauses auto-scroll
- [ ] Mobile swipe works

### Edge Cases
- [ ] No featured posts - carousel hidden
- [ ] 1 featured post - carousel shows 1 slide
- [ ] 5+ featured posts - shows first 5
- [ ] Featured + regular posts - both display correctly

---

## 📝 Summary

**What Was Added:**
- ✅ Database column for featured flag
- ✅ Admin toggle to mark posts as featured
- ✅ Filtered query to show only featured posts
- ✅ Auto-scrolling carousel with controls
- ✅ Migration script for existing databases

**Benefits:**
- ✅ Highlight best content
- ✅ Increase engagement on key posts
- ✅ Professional carousel presentation
- ✅ Easy to manage (one checkbox)
- ✅ Responsive and mobile-friendly

**User Experience:**
- **Admin:** Simple checkbox in post editor
- **Visitors:** Engaging auto-scrolling showcase
- **Mobile:** Touch-friendly carousel

---

**Status:** ✅ **Complete and Ready to Use**

*Last Updated: January 3, 2026*

