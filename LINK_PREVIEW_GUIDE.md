# Link Preview Cards - User Guide

## Overview
The Link Preview feature allows you to insert WhatsApp-style preview cards for any URL directly into your post content. These cards show rich metadata including title, description, images, and for video content, they can even embed the player directly.

## Features

### 1. **Rich Metadata Display**
- **Title**: The page or content title
- **Description**: A brief summary (up to 4 lines)
- **Image**: Featured image or thumbnail
- **Site Name**: The source website
- **URL**: The original link

### 2. **Video Support**
- **oEmbed Integration**: Automatic embedding for:
  - YouTube (including Shorts)
  - Vimeo
  - Twitter/X
  - Instagram
- **Play Overlay**: Visual play button for video content
- **Responsive Player**: Videos adapt to screen size

### 3. **Security**
- **SSRF Protection**: Blocks private IPs, localhost, and metadata endpoints
- **Timeout Protection**: 8-second timeout for external requests
- **Size Limits**: Max 2MB download per URL
- **Content Type Validation**: Only HTML pages are processed

### 4. **Performance**
- **Caching**: Previews cached for 1 hour
- **Efficient Parsing**: Uses BeautifulSoup4 for fast HTML parsing
- **Fallback Support**: Falls back to Twitter Card tags if Open Graph unavailable

## How to Use

### In the Post Editor

1. **Click the "Link Preview" Button**
   - Located in the editor controls (bottom of editor)
   - Icon: 🔗 Link Preview

2. **Enter the URL**
   - A prompt will appear asking for the URL
   - Enter any http:// or https:// URL
   - Examples:
     - Website: `https://example.com/article`
     - YouTube: `https://www.youtube.com/watch?v=VIDEO_ID`
     - YouTube Shorts: `https://www.youtube.com/shorts/VIDEO_ID`
     - Vimeo: `https://vimeo.com/VIDEO_ID`
     - Twitter: `https://twitter.com/user/status/ID`

3. **Wait for Processing**
   - A notification shows "Fetching link preview..."
   - The backend fetches and parses metadata
   - Usually takes 1-3 seconds

4. **Preview Inserted**
   - The card appears at your cursor position
   - You'll see a success notification
   - The card is interactive (clickable) in the editor

### Supported URL Types

#### Regular Websites
Any website with Open Graph or Twitter Card meta tags:
```
https://techcrunch.com/article
https://medium.com/@user/post
https://dev.to/article
```

#### Videos (with oEmbed)
- **YouTube**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **YouTube Shorts**: `https://www.youtube.com/shorts/bbwtRCx09JQ`
- **Vimeo**: `https://vimeo.com/123456789`

#### Social Media
- **Twitter/X**: `https://twitter.com/user/status/123456`
- **Instagram**: `https://instagram.com/p/ABC123/`

## Preview Card Appearance

### In the Editor
- Clean, bordered card with rounded corners
- Hover effect for better visibility
- Shows preview exactly as it will appear on the site

### On the Post Page
- Fully responsive design
- Hover animation (lifts slightly)
- Click to open original URL in new tab
- Video embeds play directly in the card

## Technical Details

### Backend API
- **Endpoint**: `/api/link-preview?url=ENCODED_URL`
- **Authentication**: Requires login
- **Response Format**:
```json
{
  "success": true,
  "data": {
    "type": "video",
    "url": "https://...",
    "title": "Video Title",
    "description": "Video description",
    "image": "https://thumbnail.jpg",
    "site_name": "YouTube",
    "embed_html": "<iframe...>",
    "provider": "youtube.com"
  }
}
```

### Error Handling
The API returns helpful error messages:
- `Invalid URL`: Not http/https or SSRF blocked
- `Request timeout`: External site took too long
- `URL does not point to an HTML page`: Content-Type check failed
- `Could not extract metadata`: No OG/Twitter tags found

### Cache Management
- **Duration**: 1 hour (3600 seconds)
- **Storage**: In-memory (resets on server restart)
- **Key**: MD5 hash of the URL
- **Future**: Can be extended to use Redis or database

## Troubleshooting

### "Invalid URL" Error
- Make sure URL starts with `http://` or `https://`
- Check that the domain is publicly accessible
- Private IPs and localhost are blocked for security

### "Request timeout" Error
- The external site is slow or unreachable
- Try again later
- Check if the URL is correct

### No Preview Generated
- The website might not have Open Graph tags
- Try a different URL or manually add content
- Check browser console for errors

### Preview Not Showing in Post
- Make sure CSS is loaded (check browser DevTools)
- Clear browser cache and hard refresh (Ctrl+Shift+R)
- Check if the preview data is in the HTML source

## Development Notes

### Dependencies Added
```txt
beautifulsoup4==4.12.2
```

### Files Modified
1. **api.py**: Added `/api/link-preview` endpoint
2. **templates/admin/post_edit.html**: Added Link Preview button and Quill blot
3. **templates/post.html**: Added preview card CSS
4. **requirements.txt**: Added BeautifulSoup4

### Custom Quill Blot
- **Name**: `linkPreview`
- **Type**: BlockEmbed
- **Storage**: JSON in `data-preview` attribute
- **Rendering**: Custom HTML with CSS classes

## Future Enhancements

Potential improvements for future versions:
- [ ] Database caching for persistence
- [ ] Admin panel to manage cached previews
- [ ] Whitelist/blacklist for domains
- [ ] Custom preview editor (override fetched data)
- [ ] Preview refresh button
- [ ] Analytics tracking for preview clicks
- [ ] Support for more oEmbed providers
- [ ] Batch preview generation
- [ ] Preview thumbnail customization

## Examples

### Example 1: Tech Article
```
Input: https://techcrunch.com/2024/01/01/article-title
Output: Card with TC logo, article title, excerpt, and featured image
```

### Example 2: YouTube Video
```
Input: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Output: Card with video thumbnail, title, and embedded player
Click: Plays video directly in the card
```

### Example 3: YouTube Shorts
```
Input: https://www.youtube.com/shorts/bbwtRCx09JQ
Output: Card with thumbnail and embedded vertical video
Note: Automatically converts to regular embed format
```

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Status**: Production Ready ✅

