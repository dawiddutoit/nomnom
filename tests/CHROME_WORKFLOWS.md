# NomNom Chrome Extension Testing Workflows

This guide provides ready-to-use prompts for testing NomNom with Claude-in-Chrome extension.

## Quick Start

1. **Ensure Chrome extension is installed and active**
2. **Copy a prompt from below**
3. **Paste into Claude Code conversation**
4. **Claude will execute the workflow automatically**

---

## Table of Contents

- [Barcode Scanner Testing](#barcode-scanner-testing)
- [Food Logging Workflows](#food-logging-workflows)
- [Goal Tracking & Dashboard](#goal-tracking--dashboard)
- [Error Handling & Edge Cases](#error-handling--edge-cases)
- [Performance & Network](#performance--network)
- [Creating Documentation](#creating-documentation)

---

## Barcode Scanner Testing

### Basic Barcode Scan Test

```
Open NomNom in Chrome at http://localhost:5173 and test the barcode scanner with Nutella (barcode 3017620422003).

Steps:
1. Navigate to the scanner page
2. Enter the barcode 3017620422003
3. Verify product name "Nutella" appears
4. Verify calories "539 kcal" is displayed
5. Check nutritional breakdown (protein, carbs, fat)
6. Take a screenshot of the product details
7. Check console for any errors
8. Report what you found
```

### Multi-Product Scan Test

```
Test the barcode scanner with multiple products and compare results:

Products to test:
- Nutella: 3017620422003 (expect 539 kcal)
- Coca-Cola: 5000112637588 (expect 42 kcal)
- Greek Yogurt: 8714100770221 (expect 97 kcal)
- Cheerios: 737628064502 (expect 367 kcal)

For each product:
1. Scan the barcode
2. Verify product name and calories
3. Check data quality indicator
4. Screenshot the result
5. Note any missing nutritional data

Create a summary table comparing all products.
```

### Barcode Scan Speed Test

```
Test barcode scanning performance:

1. Open NomNom scanner
2. Scan Nutella (3017620422003) - first time (uncached)
3. Note the time from scan to result display
4. Scan the same barcode again (should be cached)
5. Note the cached lookup time
6. Monitor network requests to see cache behavior
7. Compare cached vs uncached performance
8. Report timings and any performance issues
```

### Unknown Barcode Handling

```
Test error handling for unknown barcodes:

1. Open NomNom scanner
2. Try scanning barcode 0000000000000 (doesn't exist)
3. Verify "not found" error message appears
4. Check if "Enter Manually" button is shown
5. Click "Enter Manually"
6. Verify manual entry form opens
7. Check console for errors (should be none)
8. Screenshot the error state and manual entry form
9. Report the user experience
```

---

## Food Logging Workflows

### Complete Daily Logging Flow

```
Simulate a user logging a full day of meals:

Meals to log:
- Breakfast: Cheerios (737628064502)
- Mid-morning snack: Greek Yogurt (8714100770221)
- Lunch: Manual entry (Chicken Salad, 350 cal, 35g protein)
- Afternoon snack: Coca-Cola (5000112637588)
- Dinner: Manual entry (Grilled Salmon, 450 cal, 40g protein)

For each meal:
1. Navigate to food log
2. Add the item (scan or manual entry)
3. Verify it appears in today's log
4. Check that daily totals update
5. Take screenshots after each meal

After all meals:
1. Screenshot the complete food log
2. Verify total calories calculation
3. Check macro totals (protein, carbs, fat)
4. Verify progress bar if goals are set
5. Report any calculation errors
```

### Bulk Barcode Scanning

```
Test scanning multiple items in quick succession (grocery haul scenario):

Scan these items rapidly:
1. Nutella: 3017620422003
2. Coca-Cola: 5000112637588
3. Greek Yogurt: 8714100770221
4. Cheerios: 737628064502

Goals:
- Test UI responsiveness with rapid scans
- Verify all items are queued/processed
- Check for race conditions
- Monitor network requests (should batch if possible)
- Verify all items end up in the log
- Check console for any errors
- Report user experience and any issues
```

### Edit & Delete Food Entries

```
Test editing and deleting food log entries:

1. Log Nutella (3017620422003)
2. Find the entry in today's log
3. Click edit button
4. Change quantity from 1 serving to 2 servings
5. Verify calories double
6. Save changes
7. Verify totals updated
8. Screenshot the updated entry

Then:
1. Click delete button on the same entry
2. Confirm deletion
3. Verify entry removed from log
4. Verify totals recalculated
5. Screenshot the updated log
6. Report findings
```

---

## Goal Tracking & Dashboard

### Set Goals & Track Progress

```
Test goal setting and progress tracking:

1. Navigate to goals/settings
2. Set daily goals:
   - Calories: 2000
   - Protein: 150g
   - Carbs: 200g
   - Fat: 67g
3. Save goals
4. Navigate to dashboard
5. Log these foods:
   - Cheerios: 737628064502 (367 cal)
   - Greek Yogurt: 8714100770221 (97 cal)
6. Verify dashboard shows:
   - Total: 464 calories (23% of goal)
   - Protein progress
   - Carbs progress
   - Fat progress
7. Screenshot the dashboard
8. Add more foods to reach ~1500 calories
9. Screenshot at 75% progress
10. Report accuracy of calculations
```

### Dashboard Visualization Test

```
Test dashboard charts and visualizations:

1. Open NomNom dashboard
2. Verify these elements exist:
   - Daily calorie progress bar/chart
   - Macro breakdown (protein/carbs/fat)
   - Recent meals list
   - Today's summary
3. Screenshot each visualization
4. Check responsiveness (resize window)
5. Test different screen sizes:
   - Desktop (1920x1080)
   - Tablet (768x1024)
   - Mobile (375x667)
6. Take screenshots at each size
7. Report any layout issues
```

---

## Error Handling & Edge Cases

### Network Failure Simulation

```
Test app behavior when network is unavailable:

1. Open NomNom
2. Use Chrome DevTools to set network to "Offline"
3. Try scanning a barcode
4. Verify appropriate error message
5. Check if cached items still work
6. Re-enable network
7. Verify app recovers gracefully
8. Check console for errors
9. Report user experience during offline mode
```

### Invalid Input Handling

```
Test input validation and error handling:

Try these invalid inputs:
1. Barcode field:
   - Empty string
   - Letters: "ABCDEFG"
   - Too short: "123"
   - Too long: "12345678901234567890"
   - Special chars: "!@#$%^&*()"

2. Manual entry:
   - Negative calories: -500
   - Zero calories: 0
   - Huge calories: 999999
   - Empty product name
   - Very long product name (500 chars)

For each:
- Verify validation message
- Check form won't submit
- Verify no console errors
- Screenshot error states
- Report validation quality
```

### Concurrent User Actions

```
Test race conditions and concurrent actions:

1. Open two NomNom tabs
2. Log into same account in both
3. In Tab 1: Add Nutella to food log
4. In Tab 2: Add Cheerios to food log
5. Refresh both tabs
6. Verify both items appear
7. In Tab 1: Delete Nutella
8. In Tab 2: Check if Nutella still shows
9. Refresh Tab 2
10. Verify Nutella is gone
11. Report any sync issues
```

---

## Performance & Network

### Network Request Monitoring

```
Monitor API calls during barcode scanning:

1. Open Chrome DevTools Network tab
2. Navigate to NomNom scanner
3. Scan Nutella (3017620422003)
4. Analyze network requests:
   - Which APIs were called?
   - What were response times?
   - What status codes?
   - What were response sizes?
   - Check caching headers
5. Scan the same barcode again
6. Verify second scan uses cache (no API call)
7. Screenshot network tab
8. Report API performance and caching behavior
```

### Console Error Monitoring

```
Monitor console for errors during typical usage:

1. Open Console and filter for errors
2. Navigate through the app:
   - Home page
   - Scanner
   - Food log
   - Dashboard
   - Settings
3. Perform actions:
   - Scan 3 barcodes
   - Add manual entry
   - Edit an entry
   - Delete an entry
   - Update goals
4. Report ALL console errors/warnings
5. Categorize by severity
6. Screenshot any error stack traces
```

### Page Load Performance

```
Test page load and interaction performance:

1. Open Chrome DevTools Performance tab
2. Start recording
3. Navigate to http://localhost:5173
4. Wait for page to fully load
5. Stop recording
6. Analyze:
   - Time to First Contentful Paint
   - Time to Interactive
   - Total page load time
   - Main thread blocking
7. Scan a barcode (measure interaction latency)
8. Screenshot performance metrics
9. Report any performance issues
```

---

## Creating Documentation

### Create Barcode Scan Tutorial GIF

```
Record a GIF tutorial for scanning a barcode:

Workflow:
1. Start GIF recording
2. Open NomNom scanner
3. (Pause 1 second)
4. Enter barcode 3017620422003
5. (Pause 1 second)
6. Show product details appearing
7. (Pause 2 seconds on results)
8. Stop recording

Save as: "tutorials/barcode-scan-tutorial.gif"

Keep it under 15 seconds for easy sharing.
```

### Create Food Logging Tutorial GIF

```
Record a GIF showing complete food logging:

Workflow:
1. Start recording
2. Navigate to food log
3. Click "Add Food"
4. Scan barcode: 3017620422003 (Nutella)
5. Review product details
6. Confirm/add to log
7. Show item appearing in today's log
8. Highlight updated daily totals
9. Stop recording

Save as: "tutorials/food-logging-tutorial.gif"
```

### Screenshot All App Screens

```
Create a complete screenshot library of NomNom:

Capture these screens:
1. Home/Dashboard
2. Barcode scanner (empty)
3. Barcode scanner (with results)
4. Manual food entry form
5. Today's food log (with entries)
6. Goal settings page
7. User profile/settings
8. Each error state (not found, validation, etc.)

For each:
- Full page screenshot
- Clean test data (no personal info)
- Consistent window size (1280x720)
- Save as: screenshots/{screen-name}.png

Create an index documenting all screenshots.
```

---

## Advanced Workflows

### Accessibility Testing

```
Test keyboard navigation and screen reader support:

1. Navigate to NomNom using only keyboard
2. Test tab order through all interactive elements
3. Verify all buttons/links are keyboard accessible
4. Test scanner with keyboard only (no mouse)
5. Check for visible focus indicators
6. Use Chrome's Accessibility Audit
7. Screenshot audit results
8. Report accessibility issues
```

### Mobile Device Simulation

```
Test mobile experience using Chrome DevTools:

Test on these devices:
1. iPhone 14 Pro (393x852)
2. iPad Pro (1024x1366)
3. Samsung Galaxy S21 (360x800)

For each device:
1. Set device mode in DevTools
2. Navigate through all pages
3. Test barcode scanner touch interaction
4. Test scrolling and gestures
5. Verify responsive layout
6. Screenshot each major screen
7. Report mobile-specific issues
```

### Cross-Browser Comparison

```
Compare NomNom appearance across browsers:

(Note: Requires opening in different browsers)

Browsers to test:
- Chrome
- Firefox
- Safari (if on Mac)
- Edge

For each browser:
1. Navigate to scanner
2. Scan Nutella (3017620422003)
3. Screenshot product details
4. Check console for browser-specific errors
5. Test food logging
6. Compare rendering differences
7. Report browser compatibility issues
```

---

## Troubleshooting Common Issues

### Extension Not Responding

**Symptom:** Claude can't control Chrome

**Test:**
```
Check if Claude-in-Chrome extension is working:

1. Call tabs_context_mcp to list tabs
2. If it fails, the extension may not be running
3. Check Chrome extensions page
4. Restart Chrome if needed
5. Try opening a new tab manually
6. Call tabs_context_mcp again
```

### App Not Running

**Symptom:** Can't navigate to localhost:5173

**Test:**
```
Verify NomNom dev server is running:

1. Try navigating to http://localhost:5173
2. If it fails, check if server is running:
   - Frontend: npm run dev (should be on port 5173)
   - Backend: Check if API is running (port 8000)
3. Check console for connection errors
4. Report what you found
```

### Stale Test Data

**Symptom:** Food log has old data

**Test:**
```
Check and clean test data:

1. Navigate to food log
2. Check if there are old test entries
3. Delete all entries
4. Verify daily totals reset to 0
5. Scan a fresh barcode to verify clean state
6. Report findings
```

---

## Custom Workflows

### Create Your Own Workflow

Template for custom testing prompts:

```
Test [FEATURE NAME]:

1. Navigate to [PAGE/URL]
2. [ACTION 1]
3. Verify [EXPECTED RESULT 1]
4. [ACTION 2]
5. Verify [EXPECTED RESULT 2]
...
6. Screenshot [WHAT TO CAPTURE]
7. Check console for errors
8. Monitor network requests
9. Report findings

Expected behavior:
- [BEHAVIOR 1]
- [BEHAVIOR 2]

Success criteria:
- [CRITERIA 1]
- [CRITERIA 2]
```

---

## Best Practices

### When Using Chrome Extension

1. **Always start with `tabs_context_mcp`** - Get valid tab IDs
2. **Be specific** - "Click the blue 'Scan' button" not "click button"
3. **Request screenshots** - Visual evidence is valuable
4. **Ask for console monitoring** - Catch errors early
5. **Request network monitoring** - See API behavior
6. **Create GIFs for complex flows** - Better than text descriptions
7. **Test error states** - Not just happy paths
8. **Resize window for responsive testing** - Check mobile views

### Effective Prompts

**Good Prompt:**
```
Test barcode scanner with Nutella (3017620422003).
Scan the barcode, verify "Nutella" and "539 kcal" appear.
Take a screenshot and check console for errors.
```

**Better Prompt:**
```
Test barcode scanner comprehensively:
1. Navigate to scanner at localhost:5173
2. Monitor network requests
3. Scan Nutella (3017620422003)
4. Verify these appear:
   - Product name: "Nutella"
   - Calories: "539 kcal"
   - Protein: "6.3g"
   - Carbs: "57.5g"
   - Fat: "30.9g"
5. Verify API call to openfoodfacts.org
6. Check response time (should be < 2s)
7. Scan same barcode again (test cache)
8. Verify no API call second time
9. Screenshot both scans
10. Report any console errors
11. Provide performance summary
```

---

## Quick Reference

### Common Prompts

**Open NomNom:**
```
Open NomNom at http://localhost:5173 in a new Chrome tab
```

**Quick scan test:**
```
Test scanning Nutella (3017620422003) and screenshot the result
```

**Check for errors:**
```
Navigate through NomNom and report any console errors
```

**Create GIF:**
```
Record a GIF of scanning a barcode from start to finish
```

**Performance test:**
```
Measure how long it takes to scan and display Nutella
```

---

**Version:** 1.0
**Last Updated:** 2025-12-28
**For:** NomNom Development Team
