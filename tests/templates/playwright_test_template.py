"""Template for creating new Playwright E2E tests.

Copy this file and customize for your test scenario.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixtures.test_data import KNOWN_BARCODES, get_barcode
from fixtures.helpers import (
    playwright_navigate,
    playwright_snapshot,
    playwright_click,
    playwright_type,
    playwright_fill_form,
    playwright_screenshot,
    playwright_wait_for,
    playwright_console_messages,
    playwright_network_requests,
    playwright_close,
    verify_product_displayed,
    verify_no_console_errors,
    find_element_ref,
)


# ============================================================================
# Configuration
# ============================================================================

APP_URL = "http://localhost:5173"
SCREENSHOTS_DIR = "tests/screenshots"


# ============================================================================
# Test: [TEST NAME]
# ============================================================================

def test_example_feature():
    """Test description: What this test validates."""
    print("🧪 Testing [FEATURE NAME]...")

    try:
        # Step 1: Navigate to app
        print("  ↳ Navigating to app...")
        playwright_navigate(APP_URL)

        # Step 2: Get page snapshot
        print("  ↳ Getting page snapshot...")
        snapshot = playwright_snapshot()

        # Step 3: Find and interact with element
        print("  ↳ Clicking [ELEMENT]...")
        element_ref = find_element_ref(snapshot, "element-id")
        if element_ref:
            playwright_click("Element description", element_ref)
        else:
            raise AssertionError("Could not find required element")

        # Step 4: Fill form (if applicable)
        print("  ↳ Filling form...")
        playwright_fill_form([
            {
                "name": "Field 1",
                "type": "textbox",
                "ref": "input[field1]",
                "value": "test value"
            },
            # Add more fields as needed
        ])

        # Step 5: Wait for expected result
        print("  ↳ Waiting for result...")
        playwright_wait_for("visible", "div[result]", timeout=5000)

        # Step 6: Verify result
        snapshot = playwright_snapshot()
        content = snapshot.get("content", "")
        assert "expected text" in content.lower(), \
            "Expected result not found in page content"

        # Step 7: Take screenshot
        playwright_screenshot(f"{SCREENSHOTS_DIR}/test-example-success.png")

        # Step 8: Verify no console errors
        console_messages = playwright_console_messages()
        assert verify_no_console_errors(console_messages), \
            "Console errors detected during test"

        # Step 9: Verify network requests (if applicable)
        network_requests = playwright_network_requests()
        # Add network verification logic here

        print("  ✅ Test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        playwright_screenshot(f"{SCREENSHOTS_DIR}/test-example-failure.png")
        raise

    finally:
        playwright_close()


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests in this file."""
    print("\n" + "="*60)
    print("[TEST SUITE NAME]")
    print("="*60 + "\n")

    tests = [
        test_example_feature,
        # Add more test functions here
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1

        print()  # Blank line between tests

    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
