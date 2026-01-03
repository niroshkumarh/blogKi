# Reader Audit Trail - Complete Guide

## Overview
The Reader Audit Trail feature provides comprehensive tracking of who reads each blog post, with timestamps and detailed analytics. It supports both **logged-in users** and **anonymous visitors**, giving you complete visibility into your readership.

## Key Features

### 1. **Anonymous + Logged-in Tracking**
- **Logged-in Users**: Tracked by their user account (name/email)
- **Anonymous Visitors**: Tracked by cookie-based anonymous ID + IP + user-agent
- **Zero Impact**: Only tracks on post detail pages, no changes to other pages

### 2. **Rich Tracking Data**
For every read event, we capture:
- **Reader Identity**: User ID or anonymous ID
- **Timestamp**: Exact date/time of the event
- **Progress**: Scroll depth percentage (0-100%)
- **Time Spent**: Seconds on page
- **IP Address**: Visitor IP (respects X-Forwarded-For)
- **User Agent**: Browser/device information

### 3. **Multiple Admin Views**

#### Per-Post Stats (`/admin/posts/<id>/stats`)
- Shows recent 20 read events in a preview table
- Clickable "Total Views" stat that opens detailed reader log
- View who read this specific post

#### Per-Post Readers (`/admin/posts/<id>/readers`)
- Full paginated list of all read events for a post
- Filter by: All / Logged In / Anonymous
- Shows timestamp, reader, progress bar, time, IP, user-agent
- 50 events per page with pagination

#### Global Readers (`/admin/readers`)
- See all readers across all blog posts
- **Reader aggregation**: Shows how many posts each person read
- Filter by specific post
- Click on any reader to see detailed activity

#### Per-Reader Detail (`/admin/readers/<type>/<id>`)
- Complete reading history for a single reader
- Shows which posts they read
- Max progress and total time per post
- Expandable event details for each post

---

## How It Works

### Anonymous ID Cookie
When a visitor opens a blog post:
1. JavaScript checks for `hzn_anon_id` cookie
2. If not found, generates a UUID v4 and sets cookie (1 year expiry)
3. All read events include this ID for anonymous tracking

### Read Event Tracking
Every 30 seconds while reading a post:
- Calculates scroll depth percentage
- Calculates time elapsed since page load
- Sends data to `/api/read-event/<post_id>`
- Final event sent on page unload

### Backend Storage
All events stored in `read_events` table:
```sql
- id (primary key)
- post_id (which post)
- user_id (if logged in, nullable)
- anon_id (if anonymous, nullable)
- ip_address (visitor IP)
- user_agent (browser info)
- percent (scroll depth 0-100)
- seconds (time spent)
- created_at (timestamp)
```

---

## Admin Usage Guide

### Viewing Who Read a Specific Post

**Method 1: From Post Stats**
1. Go to **Admin → Posts**
2. Click **"Stats"** on any post
3. Click the **"Total Views"** number at the top
4. You'll see a detailed reader log with filters

**Method 2: Direct Navigation**
1. Go to **Admin → Posts → Stats**
2. Scroll to **"Recent Read Events"** section
3. Click **"View All Read Events"** button

### Filtering Readers
On the post readers page:
- Click **"All"** to see everyone
- Click **"Logged In"** to see only authenticated users
- Click **"Anonymous"** to see only cookie-tracked visitors

### Viewing Global Reader Activity

1. Go to **Admin → Readers** (in sidebar)
2. See all readers sorted by last activity
3. Each row shows:
   - Reader name/ID
   - Type (Logged In / Anonymous)
   - **How many distinct posts they read**
   - Total read events count
   - First seen / Last seen dates
   - IP address (for anonymous)

### Drilling Down on a Specific Reader

1. From **Admin → Readers**, click **"View Details"** on any reader
2. You'll see:
   - Complete list of posts they read
   - Max progress % for each post
   - Total time spent on each post
   - Click **"Show Events"** to see raw event log per post

---

## Data Privacy & Security

### Privacy Considerations
- Anonymous IDs are random UUIDs (not personally identifiable)
- IP addresses stored for admin analytics only
- User-agent strings stored for device/browser analytics
- All data visible **only to admins**

### GDPR/Privacy Compliance
If you need to comply with privacy regulations:
- Cookie notice: Inform users about analytics cookies
- Data retention: Consider purging old read events
- User rights: Implement data deletion on request
- IP anonymization: Consider truncating IPs (future enhancement)

### Security Features
- Anonymous tracking requires valid cookie
- No tracking on archive/home pages (only post detail)
- IP capture respects reverse proxy headers (X-Forwarded-For)
- User-agent limited to 500 characters

---

## Technical Details

### Database Schema

**ReadEvent Model** (`read_events` table):
```python
id = Integer (primary key)
post_id = Integer (foreign key to posts)
user_id = Integer (nullable, foreign key to users)
anon_id = String(255) (nullable, indexed)
ip_address = String(45) (nullable, indexed)
user_agent = String(500) (nullable)
percent = Integer (scroll depth 0-100)
seconds = Integer (time in seconds)
created_at = DateTime (indexed)
```

**Indexes**:
- `ix_read_events_post_id`
- `ix_read_events_user_id`
- `ix_read_events_anon_id`
- `ix_read_events_ip_address`
- `ix_read_events_created_at`

### API Endpoint

**POST `/api/read-event/<post_id>`**

Request body:
```json
{
  "percent": 75,
  "seconds": 120,
  "anon_id": "uuid-v4-string"  // Required if not logged in
}
```

Response:
```json
{
  "success": true
}
```

**Authentication**: Not required (works for anonymous)

### Migration Script

**File**: `migrate_read_events_anonymous.py`

Run once to update existing database:
```bash
python migrate_read_events_anonymous.py
```

Changes:
1. Makes `user_id` nullable
2. Adds `anon_id` column with index
3. Adds `ip_address` column with index
4. Adds `user_agent` column

### Viewer Counting Logic

**Old (logged-in only)**:
```python
viewers = ReadEvent.query.filter_by(post_id=id).distinct(user_id).count()
```

**New (logged-in + anonymous)**:
```python
unique_users = ReadEvent.query.filter(
    post_id=id, 
    user_id.isnot(None)
).distinct(user_id).count()

unique_anon = ReadEvent.query.filter(
    post_id=id,
    anon_id.isnot(None)
).distinct(anon_id).count()

total_views = unique_users + unique_anon
```

---

## Deployment Steps

### 1. Pull Latest Code
```bash
git pull origin docker-postgres-analytics
```

### 2. Rebuild Docker (runs migration automatically)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

The migration script `migrate_read_events_anonymous.py` runs automatically on startup.

### 3. Verify Migration
Check Docker logs:
```bash
docker-compose logs web | grep -A 10 "Migrating read_events"
```

You should see:
```
✅ user_id is now nullable
✅ anon_id column added with index
✅ ip_address column added with index
✅ user_agent column added
🎉 Migration completed successfully!
```

### 4. Test Tracking
1. Open any blog post (not logged in)
2. Open browser DevTools → Console
3. Look for:
   ```
   🆔 Generated new anon_id: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
   📖 Read tracking initialized for post: X
   📊 Read event tracked: Y%, Zs
   ```

### 5. Verify Admin Pages
1. Log in to admin
2. Go to **Admin → Readers** (should load without errors)
3. Go to any post stats and click "Total Views"
4. Should see the new reader log page

---

## Troubleshooting

### No Read Events Showing

**Check 1: Migration ran successfully**
```bash
docker-compose logs web | grep "Migration completed"
```

**Check 2: Tracking is working**
Open a post, check browser console for tracking logs

**Check 3: Database columns exist**
```bash
docker exec -it blogki-db psql -U bloguser -d blogsite -c "\d read_events"
```

Should show: `anon_id`, `ip_address`, `user_agent` columns

### Anonymous Cookie Not Setting

**Check 1**: Browser allows cookies (not in incognito with strict settings)

**Check 2**: Check browser console for errors

**Check 3**: Manually check cookie:
```javascript
document.cookie.split(';').find(c => c.includes('hzn_anon_id'))
```

### Admin Page Errors

**Error**: `'post_readers' endpoint not found`

**Fix**: Restart Flask app:
```bash
docker-compose restart web
```

**Error**: `Column 'anon_id' does not exist`

**Fix**: Run migration manually:
```bash
docker exec -it blogki-web python migrate_read_events_anonymous.py
```

---

## Future Enhancements

Potential improvements for future versions:
- [ ] Export reader data as CSV/Excel
- [ ] Date range filters on all admin pages
- [ ] Email reports for post performance
- [ ] Heatmaps showing where readers scroll
- [ ] Reader retention analysis (returning vs new)
- [ ] Data retention policies (auto-purge old events)
- [ ] IP anonymization (GDPR compliance)
- [ ] Geographic analysis (GeoIP lookup)
- [ ] Device/browser analytics
- [ ] Reading time distribution charts

---

## Examples

### Example 1: Finding Engaged Readers
1. Go to **Admin → Readers**
2. Sort by "Posts Read" (manual sort, click header)
3. Click on readers with high post counts
4. See which topics they're interested in

### Example 2: Analyzing Post Performance
1. Go to **Admin → Posts → Stats** for a specific post
2. Look at "Avg Completion" (75% = most readers finish)
3. Click "Total Views" to see the reader log
4. Filter by "Anonymous" to see organic traffic
5. Check time spent to gauge engagement

### Example 3: Tracking Anonymous User Journey
1. Go to **Admin → Readers**
2. Find an anonymous reader with multiple posts read
3. Click "View Details"
4. See their complete reading journey
5. Identify content patterns (which topics they prefer)

---

**Last Updated**: January 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Database Impact**: Adds 3 columns + 3 indexes to `read_events` table  
**Performance**: Minimal (event tracking is async, no page load impact)

