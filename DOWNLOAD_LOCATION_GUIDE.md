# Download & Print Button - Complete Guide

## Where Downloaded Files Go

### Browser Default Locations

**Windows:**
- **Chrome/Edge:** `C:\Users\[YourName]\Downloads\`
- **Firefox:** `C:\Users\[YourName]\Downloads\`
- **Custom:** Check browser settings: Settings → Downloads

**Mac:**
- **Safari/Chrome/Firefox:** `/Users/[YourName]/Downloads/`
- **Custom:** Check browser settings

**Linux:**
- **All Browsers:** `~/Downloads/` or `/home/[username]/Downloads/`

### File Name Format
```
executive-presence-report-[assessment-id].txt
```

Example:
```
executive-presence-report-a1b2c3d4-5678-90ab-cdef-1234567890ab.txt
```

### How to Find Your Downloads

**Chrome:**
1. Click 3 dots (⋮) in top right
2. Click "Downloads" or press Ctrl+J (Cmd+Shift+J on Mac)
3. See list of all downloads

**Firefox:**
1. Click menu (☰) in top right
2. Click "Downloads" or press Ctrl+J
3. See download list

**Safari:**
1. Click "View" → "Show Downloads" or press Option+Cmd+L
2. See download list

**Edge:**
1. Click 3 dots (···) in top right
2. Click "Downloads" or press Ctrl+J
3. See download list

---

## Testing the Buttons

### Prerequisites
1. Upload a video
2. Wait for processing to complete
3. Navigate to report page
4. Ensure report is fully loaded (you see scores)

### Test Download Button

**Step 1: Open Browser Console**
- Press F12 (Windows/Linux) or Cmd+Option+I (Mac)
- Go to "Console" tab

**Step 2: Click Download Button**

**Expected Console Output:**
```
Download button clicked
Report data: {assessment_id: "...", overall_score: 85, ...}
Creating report text...
Creating download link...
Triggering download...
Download completed successfully
```

**Expected Result:**
- File downloads to your Downloads folder
- Browser shows download notification
- File appears in Downloads list

**Step 3: Verify File**
- Go to Downloads folder
- Open the .txt file
- Should contain:
  - Overall score
  - Bucket scores
  - LLM coaching report
  - Detailed parameters
  - Timestamp

### Test Print Button

**Step 1: Have Console Open**
- F12 → Console tab

**Step 2: Click Print Button**

**Expected Console Output:**
```
Print button clicked
Report available: true
Opening print dialog...
Print dialog opened
```

**Expected Result:**
- Browser print dialog opens
- Print preview shows:
  - ✅ Clean layout
  - ✅ No buttons
  - ✅ White background
  - ✅ All content visible

**Step 3: Test Print Preview**
- Check all sections are expanded
- Verify no buttons show
- Check page breaks look good
- Can print or save as PDF

---

## Troubleshooting

### Download Button Not Working

**Symptom:** Nothing happens when clicking Download

**Check Console For:**

1. **"Download button clicked"** 
   - ❌ Not showing? → Button handler not connected
   - ✅ Showing? → Continue checking

2. **"Report data: null" or "Report data: undefined"**
   - ❌ Problem: Report not loaded
   - ✅ Solution: Wait for page to fully load, refresh if needed

3. **Error message in console**
   - Look for red error text
   - Common errors:
     - "Cannot read property 'overall_score' of null" → Report not loaded
     - "Blob is not defined" → Browser compatibility issue
     - "SecurityError" → Browser blocking downloads

**Solutions:**

**A. Report Not Loaded**
```
Problem: Clicked too soon
Solution: Wait for scores to appear, then try again
```

**B. Browser Blocking Downloads**
```
Problem: Browser popup blocker
Solution: 
1. Check URL bar for blocked popup icon
2. Allow popups for this site
3. Try download again
```

**C. Browser Console Shows Errors**
```
Problem: JavaScript error
Solution:
1. Copy error message
2. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
3. Try again
4. If persists, try different browser
```

**D. File Not in Downloads Folder**
```
Problem: Custom download location or browser asking where to save
Solution:
1. Check browser's download settings
2. Some browsers ask "Save As" - check for that dialog
3. Look in browser's Downloads list (Ctrl+J)
```

### Print Button Not Working

**Symptom:** Nothing happens when clicking Print

**Check Console For:**

1. **"Print button clicked"**
   - ❌ Not showing? → Button handler not connected
   - ✅ Showing? → Continue

2. **"Print dialog opened"**
   - ❌ Not showing after 1 second? → Dialog blocked
   - ✅ Showing? → Should see print dialog

**Solutions:**

**A. Print Dialog Blocked**
```
Problem: Browser blocking print dialog
Solution: 
1. Try Ctrl+P (Cmd+P on Mac) as alternative
2. Check browser console for error
3. Ensure popups allowed
```

**B. Alternative Print Method**
```
Always works:
1. Press Ctrl+P (Cmd+P on Mac)
2. Or browser menu → Print
3. Print preview should appear
```

**C. Print Preview Shows Buttons**
```
Problem: CSS not loaded
Solution:
1. Hard refresh: Ctrl+Shift+R
2. Clear browser cache
3. Try again
```

### Files Download But Can't Find Them

**Check These Locations:**

1. **Browser Downloads List**
   - Chrome/Edge/Firefox: Ctrl+J
   - Safari: Option+Cmd+L

2. **System Downloads Folder**
   - Windows: `C:\Users\[YourName]\Downloads\`
   - Mac: `/Users/[YourName]/Downloads/`
   - Linux: `~/Downloads/`

3. **Search for File**
   - Windows: Windows key, type "executive-presence"
   - Mac: Cmd+Space, type "executive-presence"
   - Linux: Open file manager, search "executive-presence"

4. **Check Browser Settings**
   - Settings → Downloads → Download location
   - Might be custom folder

---

## Browser-Specific Notes

### Chrome
- Shows download at bottom of browser
- Click to open or arrow to "Show in folder"
- Ctrl+J to see all downloads

### Firefox
- Shows download arrow in toolbar
- Click arrow to see recent downloads
- Ctrl+J for full download manager

### Safari
- Downloads show in top right
- Click to see list
- Option+Cmd+L for downloads window

### Edge
- Similar to Chrome
- Shows download at bottom
- Ctrl+J for download list

---

## File Format Details

### What's in the Downloaded File?

```txt
EXECUTIVE PRESENCE ASSESSMENT REPORT
====================================

Overall Score: 85/100

BUCKET SCORES:
--------------
Communication: 87/100
Appearance & Nonverbal: 82/100
Storytelling: 86/100

DETAILED REPORT:
----------------
[Your personalized coaching insights from AI]

PARAMETER DETAILS:
------------------

COMMUNICATION:
  - Voice Clarity: 85/100
    Clear and easy to understand pronunciation
  
  - Speaking Rate: 90/100
    Optimal speaking pace at 150 words per minute
  
  [... more parameters]

APPEARANCE & NONVERBAL:
  - Posture: 80/100
    Good upright posture throughout
  
  [... more parameters]

Generated: 11/29/2025, 6:30:00 PM
```

### File Size
- Typical: 2-5 KB
- Small and easy to share

### Can Open With
- ✅ Notepad (Windows)
- ✅ TextEdit (Mac)
- ✅ Any text editor
- ✅ Word processors (Word, Google Docs)
- ✅ Email attachments

---

## Quick Reference

### Download Button
```
Click → File downloads → Check Downloads folder
Location: [Browser Downloads Folder]
Format: .txt file
```

### Print Button
```
Click → Print dialog opens → Choose printer or Save as PDF
Alternative: Ctrl+P (Cmd+P on Mac)
```

### If Nothing Works
```
1. Open browser console (F12)
2. Click button
3. Look for errors
4. Share console output for help
```

---

## Debug Mode

### Enable Full Debugging

1. **Open Console** (F12)
2. **Click Download/Print**
3. **Look for these messages:**

**Download Success:**
```
✅ Download button clicked
✅ Report data: [object Object]
✅ Creating report text...
✅ Creating download link...
✅ Triggering download...
✅ Download completed successfully
```

**Download Failure:**
```
❌ Download button clicked
❌ Report data: null
❌ No report data available
```

**Print Success:**
```
✅ Print button clicked
✅ Report available: true
✅ Opening print dialog...
✅ Print dialog opened
```

### Share Console Output

If buttons still don't work:
1. Click the button
2. Copy ALL console output (right-click → Save as)
3. Share the output for debugging

---

## Status After Fix

✅ Download button with comprehensive error handling
✅ Print button with comprehensive error handling  
✅ Detailed console logging for debugging
✅ Prevent default behavior
✅ Proper error messages
✅ Timeout for print dialog
✅ Safe property access

**Both buttons should now work reliably!**
