"""E2E tests for barcode scanning functionality.

Tests the complete barcode scan workflow using Playwright MCP.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixtures.test_data import KNOWN_BARCODES, INVALID_BARCODES, get_barcode, get_expected_calories
from fixtures.helpers import (
    playwright_navigate,
    playwright_snapshot,
    playwright_click,
    playwright_type,
    playwright_screenshot,
    playwright_wait_for,
    playwright_console_messages,
    playwright_network_requests,
    playwright_close,
    verify_product_displayed,
    verify_no_console_errors,
    verify_api_called,
    find_element_ref,
)


# ============================================================================
# Configuration
# ============================================================================

APP_URL = "http://localhost:5173"
SCREENSHOTS_DIR = "tests/screenshots"


# ============================================================================
# Test Cases
# ============================================================================

def test_barcode_scan_nutella():
    """Test scanning Nutella barcode returns correct product data."""
    print("🧪 Testing Nutella barcode scan...")

    try:
        # Navigate to app
        print("  ↳ Navigating to app...")
        playwright_navigate(APP_URL)

        # Get page snapshot
        print("  ↳ Getting page snapshot...")
        snapshot = playwright_snapshot()

        # Find and click scan barcode button
        print("  ↳ Clicking scan button...")
        scan_button_ref = find_element_ref(snapshot, "scan-barcode")
        if scan_button_ref:
            playwright_click("Scan Barcode button", scan_button_ref)
        else:
            print("  ⚠️  Could not find scan button - may need to navigate to scanner")

        # Enter Nutella barcode
        barcode = get_barcode("nutella")
        print(f"  ↳ Entering barcode: {barcode}...")
        playwright_type(barcode)

        # Wait for product details to load
        print("  ↳ Waiting for product details...")
        playwright_wait_for("visible", "div[product-details]", timeout=5000)

        # Verify product is displayed
        snapshot = playwright_snapshot()
        product_data = KNOWN_BARCODES["nutella"]

        assert verify_product_displayed(snapshot, product_data["name"], product_data["calories"]), \
            f"Product data not displayed correctly. Expected: {product_data['name']}, {product_data['calories']} kcal"

        # Take screenshot
        playwright_screenshot(f"{SCREENSHOTS_DIR}/nutella-scan-success.png")

        # Verify no console errors
        console_messages = playwright_console_messages()
        assert verify_no_console_errors(console_messages), \
            "Console errors detected during barcode scan"

        # Verify OpenFoodFacts API was called
        network_requests = playwright_network_requests()
        assert verify_api_called(network_requests, "openfoodfacts"), \
            "OpenFoodFacts API was not called"

        print("  ✅ Test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        playwright_screenshot(f"{SCREENSHOTS_DIR}/nutella-scan-failure.png")
        raise
    finally:
        playwright_close()


def test_barcode_scan_multiple_products():
    """Test scanning multiple different products."""
    print("🧪 Testing multiple product scans...")

    test_products = ["coca_cola", "greek_yogurt", "cheerios"]

    try:
        playwright_navigate(APP_URL)

        for product_key in test_products:
            print(f"  ↳ Testing {product_key}...")

            # Get barcode
            barcode = get_barcode(product_key)

            # Navigate to scanner (or reset state)
            snapshot = playwright_snapshot()
            scan_button_ref = find_element_ref(snapshot, "scan-barcode")
            if scan_button_ref:
                playwright_click("Scan Barcode button", scan_button_ref)

            # Enter barcode
            playwright_type(barcode)

            # Wait for results
            playwright_wait_for("visible", "div[product-details]", timeout=5000)

            # Verify product displayed
            snapshot = playwright_snapshot()
            product_data = KNOWN_BARCODES[product_key]

            assert verify_product_displayed(snapshot, product_data["name"], product_data["calories"]), \
                f"Product {product_key} not displayed correctly"

            # Screenshot
            playwright_screenshot(f"{SCREENSHOTS_DIR}/{product_key}-scan.png")

            print(f"    ✓ {product_data['name']} verified")

        print("  ✅ All products scanned successfully!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        playwright_screenshot(f"{SCREENSHOTS_DIR}/multiple-scan-failure.png")
        raise
    finally:
        playwright_close()


def test_barcode_not_found():
    """Test handling of unknown barcode."""
    print("🧪 Testing unknown barcode handling...")

    try:
        playwright_navigate(APP_URL)

        # Navigate to scanner
        snapshot = playwright_snapshot()
        scan_button_ref = find_element_ref(snapshot, "scan-barcode")
        if scan_button_ref:
            playwright_click("Scan Barcode button", scan_button_ref)

        # Enter invalid barcode
        invalid_barcode = INVALID_BARCODES["not_found"]
        print(f"  ↳ Entering invalid barcode: {invalid_barcode}...")
        playwright_type(invalid_barcode)

        # Wait for "not found" message
        print("  ↳ Waiting for 'not found' message...")
        playwright_wait_for("visible", "div[barcode-not-found]", timeout=5000)

        # Verify error message is displayed
        snapshot = playwright_snapshot()
        content = snapshot.get("content", "").lower()
        assert "not found" in content or "unknown" in content, \
            "Error message not displayed for unknown barcode"

        # Screenshot
        playwright_screenshot(f"{SCREENSHOTS_DIR}/barcode-not-found.png")

        # Verify no console errors (404 from API is expected, not an error)
        console_messages = playwright_console_messages()
        # Filter out expected 404 messages
        error_messages = [
            msg for msg in console_messages
            if msg.get("type") == "error" and "404" not in str(msg)
        ]
        assert len(error_messages) == 0, \
            f"Unexpected console errors: {error_messages}"

        print("  ✅ Unknown barcode handled correctly!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        playwright_screenshot(f"{SCREENSHOTS_DIR}/not-found-failure.png")
        raise
    finally:
        playwright_close()


def test_barcode_manual_entry_fallback():
    """Test manual entry flow when barcode not found."""
    print("🧪 Testing manual entry fallback...")

    try:
        playwright_navigate(APP_URL)

        # Scan unknown barcode
        snapshot = playwright_snapshot()
        scan_button_ref = find_element_ref(snapshot, "scan-barcode")
        if scan_button_ref:
            playwright_click("Scan Barcode button", scan_button_ref)

        playwright_type(INVALID_BARCODES["not_found"])
        playwright_wait_for("visible", "div[barcode-not-found]", timeout=5000)

        # Click "Enter Manually" button
        print("  ↳ Clicking 'Enter Manually' button...")
        snapshot = playwright_snapshot()
        manual_button_ref = find_element_ref(snapshot, "manual-entry")
        assert manual_button_ref, "Manual entry button not found"

        playwright_click("Enter Manually button", manual_button_ref)

        # Wait for manual entry form
        playwright_wait_for("visible", "form[manual-food-entry]", timeout=5000)

        # Verify form is displayed
        snapshot = playwright_snapshot()
        content = snapshot.get("content", "").lower()
        assert "product name" in content or "food name" in content, \
            "Manual entry form not displayed"

        # Screenshot
        playwright_screenshot(f"{SCREENSHOTS_DIR}/manual-entry-form.png")

        print("  ✅ Manual entry fallback works!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        playwright_screenshot(f"{SCREENSHOTS_DIR}/manual-entry-failure.png")
        raise
    finally:
        playwright_close()


def test_barcode_scan_performance():
    """Test barcode scan response time."""
    print("🧪 Testing barcode scan performance...")

    import time

    try:
        playwright_navigate(APP_URL)

        # Navigate to scanner
        snapshot = playwright_snapshot()
        scan_button_ref = find_element_ref(snapshot, "scan-barcode")
        if scan_button_ref:
            playwright_click("Scan Barcode button", scan_button_ref)

        # Measure scan time
        barcode = get_barcode("nutella")
        start_time = time.time()

        playwright_type(barcode)
        playwright_wait_for("visible", "div[product-details]", timeout=10000)

        elapsed_time = time.time() - start_time

        print(f"  ↳ Scan completed in {elapsed_time:.2f} seconds")

        # Assert reasonable performance (< 2 seconds for cached, < 5 for uncached)
        assert elapsed_time < 5.0, \
            f"Barcode scan took too long: {elapsed_time:.2f}s"

        if elapsed_time < 2.0:
            print("  ✅ Excellent performance (cached)")
        elif elapsed_time < 5.0:
            print("  ✅ Good performance (API call)")
        else:
            print("  ⚠️  Slow performance - investigate")

        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        raise
    finally:
        playwright_close()


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all barcode scanning tests."""
    print("\n" + "="*60)
    print("NomNom Barcode Scanning Tests")
    print("="*60 + "\n")

    tests = [
        test_barcode_scan_nutella,
        test_barcode_scan_multiple_products,
        test_barcode_not_found,
        test_barcode_manual_entry_fallback,
        test_barcode_scan_performance,
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
