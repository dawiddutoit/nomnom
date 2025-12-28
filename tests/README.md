# NomNom Tests

Comprehensive testing infrastructure for NomNom using Playwright MCP and Claude-in-Chrome.

## Quick Start

### Prerequisites

```bash
# Verify MCP tools are available
mcp-cli tools | grep playwright
mcp-cli tools | grep chrome

# Install Playwright browsers
mcp-cli call plugin_playwright_playwright/browser_install '{}'
```

### Run E2E Tests

```bash
# Run all tests
python tests/e2e/test_barcode_scanning.py

# Run specific test
python -c "from tests.e2e.test_barcode_scanning import test_barcode_scan_nutella; test_barcode_scan_nutella()"
```

### Interactive Testing

**Copy/paste prompts from `CHROME_WORKFLOWS.md`:**

```
Open NomNom at http://localhost:5173 and test the barcode scanner with Nutella (barcode 3017620422003)
```

Claude will automatically execute the test workflow.

---

## Directory Structure

```
tests/
├── README.md                      # This file
├── e2e/                           # Playwright E2E tests
│   └── test_barcode_scanning.py  # Barcode scanner tests
├── fixtures/                      # Test data and helpers
│   ├── test_data.py              # Known barcodes, users, test data
│   └── helpers.py                # MCP wrapper functions
├── screenshots/                   # Test artifacts
├── templates/                     # Test templates
│   └── playwright_test_template.py
└── CHROME_WORKFLOWS.md           # Chrome extension test prompts
```

---

## Test Types

### 1. Playwright MCP Tests (Automated)

**Location:** `tests/e2e/*.py`

**Use for:**
- CI/CD pipelines
- Regression testing
- Repeatable test scenarios
- Performance benchmarks

**Example:**

```python
from fixtures.helpers import playwright_navigate, playwright_click
from fixtures.test_data import get_barcode

playwright_navigate("http://localhost:5173")
barcode = get_barcode("nutella")
# ... test logic
```

**Run:**

```bash
python tests/e2e/test_barcode_scanning.py
```

### 2. Chrome Extension Tests (Interactive)

**Location:** `tests/CHROME_WORKFLOWS.md`

**Use for:**
- Exploratory testing
- Visual verification
- Creating GIF tutorials
- Debugging issues
- Ad-hoc testing

**Example:**

```
Test barcode scanner with Nutella (3017620422003).
Verify product name and calories appear.
Take a screenshot and check console for errors.
```

---

## Creating New Tests

### Playwright E2E Test

1. **Copy template:**

```bash
cp tests/templates/playwright_test_template.py tests/e2e/test_my_feature.py
```

2. **Edit the test:**

```python
def test_my_feature():
    """Test my awesome feature."""
    playwright_navigate(APP_URL)
    # ... your test logic
    assert condition, "Test failed"
```

3. **Run it:**

```bash
python tests/e2e/test_my_feature.py
```

### Chrome Workflow

1. **Write a prompt in natural language:**

```
Test the food logging feature:
1. Navigate to food log
2. Add Nutella via barcode scan
3. Verify it appears in today's log
4. Check that daily totals update
5. Screenshot the result
```

2. **Paste into Claude Code conversation**

3. **Claude executes it automatically**

---

## Test Data

### Known Barcodes

Use these for consistent testing (from `fixtures/test_data.py`):

| Product | Barcode | Calories | Quality |
|---------|---------|----------|---------|
| Nutella | `3017620422003` | 539 kcal | Complete |
| Coca-Cola | `5000112637588` | 42 kcal | Complete |
| Greek Yogurt | `8714100770221` | 97 kcal | Partial |
| Cheerios | `737628064502` | 367 kcal | Complete |

**Usage:**

```python
from fixtures.test_data import KNOWN_BARCODES, get_barcode

barcode = get_barcode("nutella")  # Returns: "3017620422003"
calories = KNOWN_BARCODES["nutella"]["calories"]  # Returns: 539
```

### Test Users

```python
from fixtures.test_data import TEST_USERS, get_test_user

user = get_test_user("default")
# {"email": "test@nomnom.app", "password": "Test123!", ...}
```

---

## Helper Functions

### Playwright Helpers

```python
from fixtures.helpers import (
    playwright_navigate,      # Navigate to URL
    playwright_snapshot,       # Get page state
    playwright_click,          # Click element
    playwright_type,           # Type text
    playwright_fill_form,      # Fill multiple fields
    playwright_screenshot,     # Take screenshot
    playwright_wait_for,       # Wait for element
    playwright_console_messages,  # Get console logs
    playwright_network_requests,  # Get network requests
)

# Example usage
playwright_navigate("http://localhost:5173")
snapshot = playwright_snapshot()
playwright_click("Button description", "button[id]")
playwright_screenshot("screenshots/test.png")
```

### Chrome Helpers

```python
from fixtures.helpers import (
    chrome_get_tabs,          # List Chrome tabs
    chrome_create_tab,        # Create new tab
    chrome_navigate,          # Navigate tab
    chrome_read_page,         # Read page content
    chrome_console_messages,  # Get console logs
    chrome_network_requests,  # Get network requests
)

# Example usage
tabs = chrome_get_tabs()
tab_id = tabs["tabs"][0]["id"]
chrome_navigate(tab_id, "http://localhost:5173")
```

### Verification Helpers

```python
from fixtures.helpers import (
    verify_product_displayed,    # Check product data
    verify_no_console_errors,    # Check for errors
    verify_api_called,           # Check API calls
)

# Example usage
snapshot = playwright_snapshot()
assert verify_product_displayed(snapshot, "Nutella", 539)

console = playwright_console_messages()
assert verify_no_console_errors(console)
```

---

## Common Test Patterns

### Pattern 1: Barcode Scan

```python
def test_scan_product():
    playwright_navigate(APP_URL)

    # Find scan button
    snapshot = playwright_snapshot()
    scan_ref = find_element_ref(snapshot, "scan-barcode")
    playwright_click("Scan button", scan_ref)

    # Enter barcode
    playwright_type(get_barcode("nutella"))

    # Wait for result
    playwright_wait_for("visible", "div[product-details]")

    # Verify
    snapshot = playwright_snapshot()
    assert verify_product_displayed(snapshot, "Nutella", 539)
```

### Pattern 2: Form Submission

```python
def test_submit_form():
    playwright_navigate(APP_URL)

    # Fill form
    playwright_fill_form([
        {"name": "Email", "type": "textbox", "ref": "input[email]", "value": "test@test.com"},
        {"name": "Password", "type": "textbox", "ref": "input[password]", "value": "Test123!"},
    ])

    # Submit
    snapshot = playwright_snapshot()
    submit_ref = find_element_ref(snapshot, "submit")
    playwright_click("Submit", submit_ref)

    # Verify success
    playwright_wait_for("visible", "div[success]")
```

### Pattern 3: Network Monitoring

```python
def test_api_call():
    playwright_navigate(APP_URL)

    # Trigger action that calls API
    playwright_type(get_barcode("nutella"))

    # Wait for completion
    playwright_wait_for("visible", "div[result]")

    # Check API was called
    requests = playwright_network_requests()
    assert verify_api_called(requests, "openfoodfacts.org")
```

---

## Troubleshooting

### "Browser not installed"

```bash
mcp-cli call plugin_playwright_playwright/browser_install '{}'
```

### "Element not found"

- Always call `playwright_snapshot()` before clicking
- Use `find_element_ref()` to get fresh refs
- Wait for elements with `playwright_wait_for()`

### "Extension not responding"

- Ensure Chrome extension is active
- Call `chrome_get_tabs()` to verify connection
- Restart Chrome if needed

### "Tests failing randomly"

- Add `playwright_wait_for()` for async operations
- Increase timeout values
- Check network speed/latency

---

## Best Practices

### General

1. ✅ Use known test data from `fixtures/test_data.py`
2. ✅ Take screenshots on failure for debugging
3. ✅ Check console for errors after each action
4. ✅ Clean test state between runs
5. ✅ Test error states, not just happy paths

### Playwright Tests

1. ✅ Always call `browser_snapshot` before interacting
2. ✅ Use `browser_wait_for` for async operations
3. ✅ Close browser with `playwright_close()` in `finally`
4. ✅ Save screenshots to `tests/screenshots/`
5. ✅ Use descriptive test function names

### Chrome Workflows

1. ✅ Always call `tabs_context_mcp` first
2. ✅ Be specific in prompts (element colors, positions)
3. ✅ Request screenshots for visual verification
4. ✅ Ask for console monitoring proactively
5. ✅ Create GIFs for complex workflows

---

## CI/CD Integration

Add to `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Playwright
        run: mcp-cli call plugin_playwright_playwright/browser_install '{}'

      - name: Start app
        run: |
          npm run dev &
          sleep 5

      - name: Run tests
        run: python tests/e2e/test_barcode_scanning.py

      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/screenshots/
```

---

## Resources

- [Main Testing Guide](../TESTING.md) - Comprehensive documentation
- [Chrome Workflows](CHROME_WORKFLOWS.md) - Ready-to-use test prompts
- [OpenFoodFacts Integration](../.claude/artifacts/2025-12-28/openfoodfacts/) - API documentation
- [Playwright MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/playwright) - Official docs

---

## Quick Reference

**Run all barcode tests:**
```bash
python tests/e2e/test_barcode_scanning.py
```

**Interactive test:**
```
Test scanning Nutella (3017620422003) and screenshot the result
```

**Create new test:**
```bash
cp tests/templates/playwright_test_template.py tests/e2e/test_new_feature.py
```

**Get known barcode:**
```python
from fixtures.test_data import get_barcode
barcode = get_barcode("nutella")
```

---

**Version:** 1.0
**Last Updated:** 2025-12-28
