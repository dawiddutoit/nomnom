# NomNom Testing Guide

This guide covers two complementary testing approaches for NomNom:

1. **Playwright MCP** - Automated E2E testing
2. **Claude-in-Chrome** - Interactive testing and exploration

## Table of Contents

- [Quick Start](#quick-start)
- [Playwright MCP Testing](#playwright-mcp-testing)
- [Claude-in-Chrome Testing](#claude-in-chrome-testing)
- [Test Data & Fixtures](#test-data--fixtures)
- [Testing Workflows](#testing-workflows)
- [Best Practices](#best-practices)

---

## Quick Start

### Prerequisites

```bash
# Ensure Playwright is installed
mcp-cli call plugin_playwright_playwright/browser_install '{}'

# Verify tools are available
mcp-cli tools | grep playwright
mcp-cli tools | grep chrome
```

### Run Your First Test

**Automated (Playwright):**
```bash
# Navigate to test directory
cd tests/e2e

# Run test via MCP
# (see Playwright MCP Testing section below)
```

**Interactive (Chrome):**
```bash
# Open Chrome with extension
# Ask Claude: "Open NomNom in Chrome and test the barcode scanner"
```

---

## Playwright MCP Testing

Playwright MCP provides **automated, repeatable E2E tests** for CI/CD pipelines.

### Architecture

```
tests/
├── e2e/
│   ├── barcode_scanning.py      # Barcode scan flow tests
│   ├── food_logging.py           # Food entry tests
│   ├── goal_tracking.py          # Dashboard tests
│   └── user_auth.py              # Login/signup tests
├── fixtures/
│   ├── test_data.py              # Known barcodes, users
│   └── helpers.py                # Test utilities
└── screenshots/                  # Test artifacts
```

### Available Playwright Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `browser_navigate` | Navigate to URL | `{"url": "http://localhost:5173"}` |
| `browser_snapshot` | Get page state | Returns clickable elements |
| `browser_click` | Click elements | `{"ref": "button[123]"}` |
| `browser_fill_form` | Fill forms | Multiple fields at once |
| `browser_type` | Type text | `{"text": "3017620422003"}` |
| `browser_take_screenshot` | Screenshot | `{"filename": "test.png"}` |
| `browser_console_messages` | Read console | Debug logs |
| `browser_network_requests` | Monitor network | API calls |
| `browser_wait_for` | Wait for element | Async operations |

### Example: Barcode Scan Test

**Workflow via MCP:**

```bash
# 1. Navigate to app
mcp-cli call plugin_playwright_playwright/browser_navigate '{
  "url": "http://localhost:5173"
}'

# 2. Get page snapshot to find elements
mcp-cli call plugin_playwright_playwright/browser_snapshot '{}'

# 3. Click "Scan Barcode" button
mcp-cli call plugin_playwright_playwright/browser_click '{
  "element": "Scan Barcode button",
  "ref": "button[scan-barcode]"
}'

# 4. Enter barcode manually (simulating scan)
mcp-cli call plugin_playwright_playwright/browser_type '{
  "text": "3017620422003"
}'

# 5. Wait for product to load
mcp-cli call plugin_playwright_playwright/browser_wait_for '{
  "state": "visible",
  "ref": "div[product-details]"
}'

# 6. Take screenshot
mcp-cli call plugin_playwright_playwright/browser_take_screenshot '{
  "filename": "screenshots/barcode-scan-success.png"
}'

# 7. Verify product data
mcp-cli call plugin_playwright_playwright/browser_snapshot '{}'
# Check for "Nutella", "539 kcal", etc.
```

### Test Script Pattern (Python)

```python
# tests/e2e/barcode_scanning.py
import subprocess
import json

def run_mcp_command(server_tool: str, params: dict) -> dict:
    """Execute MCP command and return result."""
    result = subprocess.run(
        ["mcp-cli", "call", server_tool, json.dumps(params)],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def test_barcode_scan_nutella():
    """Test scanning Nutella barcode returns correct product."""

    # Navigate to app
    run_mcp_command("plugin_playwright_playwright/browser_navigate", {
        "url": "http://localhost:5173"
    })

    # Get page state
    snapshot = run_mcp_command("plugin_playwright_playwright/browser_snapshot", {})

    # Find and click scan button
    scan_button_ref = find_element_ref(snapshot, "scan-barcode")
    run_mcp_command("plugin_playwright_playwright/browser_click", {
        "element": "Scan Barcode button",
        "ref": scan_button_ref
    })

    # Enter barcode
    run_mcp_command("plugin_playwright_playwright/browser_type", {
        "text": "3017620422003"
    })

    # Wait for product details
    run_mcp_command("plugin_playwright_playwright/browser_wait_for", {
        "state": "visible",
        "ref": "div[product-details]"
    })

    # Verify product data
    snapshot = run_mcp_command("plugin_playwright_playwright/browser_snapshot", {})
    assert "Nutella" in snapshot["content"]
    assert "539" in snapshot["content"]  # Calories

    # Screenshot evidence
    run_mcp_command("plugin_playwright_playwright/browser_take_screenshot", {
        "filename": "screenshots/test-nutella-scan.png"
    })

def find_element_ref(snapshot: dict, element_id: str) -> str:
    """Extract element ref from snapshot."""
    # Parse snapshot to find matching ref
    # Implementation depends on snapshot structure
    pass
```

### Running Tests

```bash
# Run single test
python tests/e2e/barcode_scanning.py

# Run all E2E tests
pytest tests/e2e/

# Run with verbose output
pytest tests/e2e/ -v

# Run specific test
pytest tests/e2e/barcode_scanning.py::test_barcode_scan_nutella
```

### Continuous Integration

Add to `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Playwright
        run: mcp-cli call plugin_playwright_playwright/browser_install '{}'

      - name: Start backend
        run: |
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 5

      - name: Start frontend
        run: |
          cd frontend
          npm run dev -- --port 5173 &
          sleep 5

      - name: Run E2E tests
        run: pytest tests/e2e/ -v

      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/screenshots/
```

---

## Claude-in-Chrome Testing

Claude-in-Chrome provides **interactive, exploratory testing** with AI-powered insights.

### When to Use

- **Manual testing**: Exploring new features
- **Visual verification**: "Does this look right?"
- **Workflow recording**: Create GIF tutorials
- **Debugging**: Inspect console logs, network requests
- **User simulation**: Realistic interaction patterns

### Available Chrome Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `tabs_context_mcp` | Get current tabs | Returns all open tabs |
| `tabs_create_mcp` | Open new tab | `{"url": "http://localhost:5173"}` |
| `navigate` | Navigate tab | `{"url": "...", "tabId": 123}` |
| `read_page` | Read page content | Returns visible text |
| `find` | Find elements | Search by text/selector |
| `form_input` | Fill forms | `{"selector": "#barcode", "value": "..."}` |
| `computer` | Click/interact | Mouse/keyboard actions |
| `gif_creator` | Record GIF | Workflow documentation |
| `read_console_messages` | Console logs | Debug info |
| `read_network_requests` | Network monitor | API calls |

### Example: Interactive Barcode Test

**Ask Claude:**

> "Open NomNom in Chrome, navigate to the barcode scanner, and test scanning Nutella (barcode 3017620422003). Record the workflow as a GIF."

**Claude will:**

1. Get current tabs: `tabs_context_mcp`
2. Create new tab: `tabs_create_mcp` with `http://localhost:5173`
3. Read page: `read_page` to see UI
4. Find scan button: `find` with "Scan Barcode"
5. Click button: `computer` with click action
6. Fill barcode: `form_input` with barcode value
7. Record GIF: `gif_creator` capturing the workflow
8. Verify result: `read_page` to confirm product details
9. Check console: `read_console_messages` for errors
10. Report findings

### Interactive Testing Workflows

#### 1. Barcode Scanner Verification

```
Prompt: "Test the barcode scanner with these products:
- Nutella (3017620422003)
- Coca-Cola (5000112637588)
- Greek Yogurt (8714100770221)

For each:
1. Scan the barcode
2. Verify product name and calories
3. Check if nutritional data is complete
4. Screenshot the results
5. Check console for errors"
```

#### 2. Food Logging Flow

```
Prompt: "Test the complete food logging workflow:
1. Open NomNom
2. Navigate to today's food log
3. Add 3 food items via barcode scan
4. Verify they appear in the log
5. Check that daily totals update
6. Take a GIF of the entire process"
```

#### 3. Goal Dashboard Test

```
Prompt: "Test the goal tracking dashboard:
1. Set a goal of 2000 calories
2. Log foods totaling ~1500 calories
3. Verify the dashboard shows 75% progress
4. Check that macros are calculated correctly
5. Screenshot the dashboard"
```

#### 4. Network Monitoring

```
Prompt: "Monitor network requests while scanning a barcode:
1. Open network monitor
2. Scan a new product (never cached)
3. Show me the API calls made
4. Verify OpenFoodFacts API is called
5. Check caching headers
6. Report response times"
```

### Recording Workflows as GIFs

**For documentation or bug reports:**

```
Prompt: "Record a GIF tutorial showing how to scan a barcode and log food.
Include:
1. Opening the scanner
2. Entering/scanning a barcode
3. Reviewing product details
4. Confirming and saving to log
5. Seeing it appear in today's entries

Save as 'barcode-scan-tutorial.gif'"
```

**Claude will:**
- Use `gif_creator` with proper timing
- Capture key steps with pauses
- Save to specified filename
- Provide the GIF for sharing

---

## Test Data & Fixtures

### Known Good Barcodes

Use these for consistent testing:

```python
# tests/fixtures/test_data.py

KNOWN_BARCODES = {
    "nutella": {
        "barcode": "3017620422003",
        "name": "Nutella",
        "calories": 539,
        "protein": 6.3,
        "carbs": 57.5,
        "fat": 30.9,
        "quality": "complete"
    },
    "coca_cola": {
        "barcode": "5000112637588",
        "name": "Coca-Cola",
        "calories": 42,
        "protein": 0,
        "carbs": 10.6,
        "fat": 0,
        "quality": "complete"
    },
    "greek_yogurt": {
        "barcode": "8714100770221",
        "name": "Greek Yogurt",
        "calories": 97,
        "protein": 10,
        "carbs": 4,
        "fat": 5,
        "quality": "partial"
    },
    "cheerios": {
        "barcode": "737628064502",
        "name": "Cheerios",
        "calories": 367,
        "protein": 11.7,
        "carbs": 73.3,
        "fat": 5,
        "quality": "complete"
    }
}

TEST_USER = {
    "email": "test@nomnom.app",
    "password": "Test123!",
    "goals": {
        "calories": 2000,
        "protein": 150,
        "carbs": 200,
        "fat": 67
    }
}
```

### Test Helpers

```python
# tests/fixtures/helpers.py

import subprocess
import json
from typing import Dict, Any

def mcp_call(server_tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MCP command via subprocess."""
    result = subprocess.run(
        ["mcp-cli", "call", server_tool, json.dumps(params)],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def playwright_navigate(url: str) -> Dict[str, Any]:
    """Navigate Playwright browser to URL."""
    return mcp_call("plugin_playwright_playwright/browser_navigate", {"url": url})

def playwright_screenshot(filename: str, fullPage: bool = False) -> Dict[str, Any]:
    """Take screenshot with Playwright."""
    return mcp_call("plugin_playwright_playwright/browser_take_screenshot", {
        "filename": filename,
        "fullPage": fullPage
    })

def playwright_get_console() -> list:
    """Get console messages."""
    result = mcp_call("plugin_playwright_playwright/browser_console_messages", {})
    return result.get("messages", [])

def verify_product_displayed(snapshot: Dict[str, Any], product_name: str, calories: int) -> bool:
    """Verify product is shown with correct data."""
    content = snapshot.get("content", "")
    return product_name in content and str(calories) in content

def chrome_navigate(tab_id: int, url: str) -> Dict[str, Any]:
    """Navigate Chrome tab to URL."""
    return mcp_call("claude-in-chrome/navigate", {
        "url": url,
        "tabId": tab_id
    })

def chrome_get_tabs() -> Dict[str, Any]:
    """Get current Chrome tabs."""
    return mcp_call("claude-in-chrome/tabs_context_mcp", {})

def chrome_read_console(pattern: str = None) -> Dict[str, Any]:
    """Read console messages, optionally filtered."""
    params = {}
    if pattern:
        params["pattern"] = pattern
    return mcp_call("claude-in-chrome/read_console_messages", params)
```

---

## Testing Workflows

### Critical User Journeys

#### 1. First-Time User Onboarding

**Test:** New user signs up, sets goals, scans first food item

**Playwright Script:**
```python
def test_onboarding_flow():
    # 1. Navigate to signup
    playwright_navigate("http://localhost:5173/signup")

    # 2. Fill signup form
    mcp_call("plugin_playwright_playwright/browser_fill_form", {
        "fields": [
            {"name": "Email", "type": "textbox", "ref": "input[email]", "value": "newuser@test.com"},
            {"name": "Password", "type": "textbox", "ref": "input[password]", "value": "Test123!"},
            {"name": "Confirm Password", "type": "textbox", "ref": "input[confirm]", "value": "Test123!"}
        ]
    })

    # 3. Submit form
    mcp_call("plugin_playwright_playwright/browser_click", {
        "element": "Sign Up button",
        "ref": "button[submit]"
    })

    # 4. Set goals
    playwright_wait_for_navigation("http://localhost:5173/goals")
    # ... fill goals form

    # 5. Scan first food
    # ... barcode scan flow

    # 6. Verify onboarding complete
    playwright_screenshot("screenshots/onboarding-complete.png")
```

**Claude-in-Chrome:**
```
Prompt: "Simulate a new user onboarding:
1. Sign up with email newuser@test.com
2. Set goal to 2000 calories
3. Walk through the tutorial (if any)
4. Scan their first food item
5. Record the experience as a GIF
6. Report any confusing UI or errors"
```

#### 2. Daily Food Logging

**Test:** User logs breakfast, lunch, dinner, snack

**Playwright Script:**
```python
def test_daily_logging():
    # Login first
    login_test_user()

    meals = [
        ("Cheerios", "737628064502", "breakfast"),
        ("Greek Yogurt", "8714100770221", "snack"),
        # ... more meals
    ]

    for name, barcode, meal_type in meals:
        scan_and_log_food(barcode, meal_type)
        verify_food_in_log(name)

    # Verify daily totals
    snapshot = mcp_call("plugin_playwright_playwright/browser_snapshot", {})
    assert "Total: " in snapshot["content"]
```

**Claude-in-Chrome:**
```
Prompt: "Log a full day of meals:
- Breakfast: Cheerios (737628064502)
- Snack: Greek Yogurt (8714100770221)
- Lunch: Create manually (Chicken Salad, 350 cal)
- Dinner: Nutella toast (3017620422003)

After each meal, check:
1. Item appears in log
2. Totals update correctly
3. Progress bar moves
4. No console errors

Take a screenshot of the final dashboard."
```

#### 3. Barcode Not Found Fallback

**Test:** User scans unknown barcode, manually enters data

**Playwright Script:**
```python
def test_barcode_not_found():
    # Scan fake barcode
    playwright_navigate("http://localhost:5173/scan")
    scan_barcode("0000000000000")

    # Wait for "not found" message
    mcp_call("plugin_playwright_playwright/browser_wait_for", {
        "state": "visible",
        "ref": "div[barcode-not-found]"
    })

    # Click "Enter Manually"
    mcp_call("plugin_playwright_playwright/browser_click", {
        "element": "Enter Manually button",
        "ref": "button[manual-entry]"
    })

    # Fill manual form
    # ... fill product details

    # Verify saved
    verify_food_in_log("Custom Food Item")
```

**Claude-in-Chrome:**
```
Prompt: "Test the unknown barcode flow:
1. Try to scan barcode 0000000000000
2. Verify 'not found' message shows
3. Click 'Enter Manually'
4. Fill in custom food data (Homemade Soup, 250 cal)
5. Save and verify it appears in log
6. Check if it's stored for future use"
```

---

## Best Practices

### General Testing

1. **Start with known data** - Use `KNOWN_BARCODES` from fixtures
2. **Clean state** - Reset database between test runs
3. **Screenshot everything** - Visual evidence of failures
4. **Monitor console** - Catch JavaScript errors
5. **Check network** - Verify API calls are correct
6. **Test error states** - Not just happy paths

### Playwright MCP

1. **Always call `browser_snapshot` before clicking** - Get fresh refs
2. **Use `browser_wait_for`** - Don't assume instant loading
3. **Check console after each step** - Catch errors early
4. **Take screenshots on failure** - Debug evidence
5. **Close browser between tests** - `browser_close` for clean state

### Claude-in-Chrome

1. **Always call `tabs_context_mcp` first** - Get valid tab IDs
2. **Be specific in prompts** - "Click the blue 'Scan' button in the header"
3. **Ask for GIFs of complex flows** - Better than screenshots
4. **Request console monitoring** - Proactive error detection
5. **Combine with network monitoring** - See API interactions

### Test Coverage

**Must Test:**
- ✅ Barcode scanning (success and failure)
- ✅ Manual food entry
- ✅ Food logging (add, edit, delete)
- ✅ Daily total calculations
- ✅ Goal setting and tracking
- ✅ User authentication
- ✅ Offline/cache behavior
- ✅ Error handling

**Nice to Have:**
- Multi-day view
- Search/filter food log
- Export data
- Profile management
- Nutritional insights

### When to Use Which Tool

| Scenario | Playwright MCP | Claude-in-Chrome |
|----------|----------------|------------------|
| **CI/CD pipeline** | ✅ Yes | ❌ No |
| **Regression testing** | ✅ Yes | ❌ No |
| **Feature exploration** | ❌ No | ✅ Yes |
| **Visual verification** | ⚠️ Manual review | ✅ Yes |
| **Bug investigation** | ⚠️ Can help | ✅ Yes |
| **Creating docs/GIFs** | ❌ No | ✅ Yes |
| **Network debugging** | ✅ Yes | ✅ Yes |
| **Console debugging** | ✅ Yes | ✅ Yes |
| **Repeatable tests** | ✅ Yes | ❌ No |
| **Ad-hoc testing** | ❌ No | ✅ Yes |

---

## Next Steps

1. **Set up test data**
   ```bash
   python tests/fixtures/seed_database.py
   ```

2. **Create first Playwright test**
   ```bash
   # Copy template
   cp tests/templates/playwright_test_template.py tests/e2e/my_first_test.py

   # Edit and run
   python tests/e2e/my_first_test.py
   ```

3. **Try interactive testing**
   ```
   Ask Claude: "Open NomNom in Chrome and test the barcode scanner"
   ```

4. **Add CI/CD workflow**
   ```bash
   # Copy template
   cp .github/workflows/e2e-tests.yml.template .github/workflows/e2e-tests.yml

   # Commit and push to trigger
   git add .github/workflows/e2e-tests.yml
   git commit -m "Add E2E tests to CI"
   git push
   ```

---

## Troubleshooting

### Playwright Issues

**"Browser not installed"**
```bash
mcp-cli call plugin_playwright_playwright/browser_install '{}'
```

**"Element not found"**
- Call `browser_snapshot` to get fresh refs
- Use `browser_wait_for` to wait for element

**"Timeout waiting for element"**
- Increase wait time
- Check if element selector is correct
- Verify page loaded correctly

### Claude-in-Chrome Issues

**"No tabs available"**
- Open Chrome with extension enabled
- Call `tabs_context_mcp` to verify connection

**"Tab ID invalid"**
- Tab was closed or changed
- Call `tabs_context_mcp` to get fresh tab IDs

**"Extension not responding"**
- Refresh the extension
- Restart Chrome
- Check extension permissions

---

## Resources

- [Playwright MCP Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/playwright)
- [Claude-in-Chrome Extension](https://github.com/anthropics/claude-in-chrome)
- [OpenFoodFacts API Testing](../.claude/artifacts/2025-12-28/openfoodfacts/OPENFOODFACTS_INTEGRATION.md)
- [NomNom Architecture](./CLAUDE.md)

---

**Version:** 1.0
**Last Updated:** 2025-12-28
**Maintained by:** NomNom Development Team
