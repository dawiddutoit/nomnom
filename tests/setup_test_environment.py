#!/usr/bin/env python3
"""Setup and verify testing environment for NomNom.

Run this script to:
1. Verify MCP tools are available
2. Install Playwright browsers
3. Verify test fixtures load correctly
4. Create screenshots directory
5. Run a simple smoke test
"""

import subprocess
import sys
import json
from pathlib import Path


# Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_step(msg: str):
    """Print step message."""
    print(f"\n{BOLD}→ {msg}{RESET}")


def print_success(msg: str):
    """Print success message."""
    print(f"  {GREEN}✓ {msg}{RESET}")


def print_warning(msg: str):
    """Print warning message."""
    print(f"  {YELLOW}⚠ {msg}{RESET}")


def print_error(msg: str):
    """Print error message."""
    print(f"  {RED}✗ {msg}{RESET}")


def run_command(cmd: list[str], capture: bool = True) -> tuple[bool, str]:
    """Run command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)


def check_mcp_cli():
    """Verify mcp-cli is available."""
    print_step("Checking mcp-cli availability")

    success, output = run_command(["which", "mcp-cli"])
    if success:
        print_success("mcp-cli is installed")
        return True
    else:
        print_error("mcp-cli not found in PATH")
        print_warning("Install Claude Code to get mcp-cli")
        return False


def check_playwright_tools():
    """Verify Playwright MCP tools are available."""
    print_step("Checking Playwright MCP tools")

    success, output = run_command(["mcp-cli", "tools"])
    if not success:
        print_error("Could not list MCP tools")
        return False

    playwright_tools = [
        "plugin_playwright_playwright/browser_navigate",
        "plugin_playwright_playwright/browser_snapshot",
        "plugin_playwright_playwright/browser_click",
    ]

    for tool in playwright_tools:
        if tool in output:
            print_success(f"Found: {tool}")
        else:
            print_warning(f"Missing: {tool}")

    return True


def check_chrome_tools():
    """Verify Chrome extension MCP tools are available."""
    print_step("Checking Claude-in-Chrome tools")

    success, output = run_command(["mcp-cli", "tools"])
    if not success:
        print_error("Could not list MCP tools")
        return False

    chrome_tools = [
        "claude-in-chrome/tabs_context_mcp",
        "claude-in-chrome/navigate",
        "claude-in-chrome/read_page",
    ]

    for tool in chrome_tools:
        if tool in output:
            print_success(f"Found: {tool}")
        else:
            print_warning(f"Missing: {tool} - Chrome extension may not be installed")

    return True


def install_playwright_browsers():
    """Install Playwright browsers if needed."""
    print_step("Installing Playwright browsers")

    success, output = run_command([
        "mcp-cli", "call",
        "plugin_playwright_playwright/browser_install",
        "{}"
    ])

    if success:
        print_success("Playwright browsers installed")
        return True
    else:
        print_error("Failed to install Playwright browsers")
        print_error(output)
        return False


def verify_test_fixtures():
    """Verify test fixtures load correctly."""
    print_step("Verifying test fixtures")

    try:
        # Add tests directory to path
        sys.path.insert(0, str(Path(__file__).parent))

        from fixtures.test_data import KNOWN_BARCODES, TEST_USERS, get_barcode
        from fixtures.helpers import mcp_call

        # Check test data
        assert len(KNOWN_BARCODES) > 0, "No test barcodes found"
        assert len(TEST_USERS) > 0, "No test users found"
        print_success(f"Loaded {len(KNOWN_BARCODES)} test barcodes")
        print_success(f"Loaded {len(TEST_USERS)} test users")

        # Test helper functions
        barcode = get_barcode("nutella")
        assert barcode == "3017620422003", "get_barcode() failed"
        print_success("Helper functions working")

        return True

    except Exception as e:
        print_error(f"Failed to load test fixtures: {e}")
        return False


def create_directories():
    """Create required test directories."""
    print_step("Creating test directories")

    directories = [
        "tests/screenshots",
        "tests/e2e",
        "tests/fixtures",
    ]

    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {dir_path}")

    return True


def run_smoke_test():
    """Run a simple smoke test with Playwright."""
    print_step("Running smoke test")

    try:
        # Simple navigation test
        result = subprocess.run(
            [
                "mcp-cli", "call",
                "plugin_playwright_playwright/browser_navigate",
                json.dumps({"url": "https://example.com"})
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print_success("Playwright navigation works")

            # Close browser
            subprocess.run(
                ["mcp-cli", "call", "plugin_playwright_playwright/browser_close", "{}"],
                capture_output=True,
                timeout=10
            )

            return True
        else:
            print_warning("Playwright navigation failed (may need first-time setup)")
            return False

    except subprocess.TimeoutExpired:
        print_warning("Smoke test timed out (browser may be initializing)")
        return False
    except Exception as e:
        print_error(f"Smoke test failed: {e}")
        return False


def print_summary(results: dict[str, bool]):
    """Print summary of all checks."""
    print("\n" + "="*60)
    print(f"{BOLD}Setup Summary{RESET}")
    print("="*60)

    for check_name, passed in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"{check_name:<40} {status}")

    print("="*60)

    all_passed = all(results.values())
    if all_passed:
        print(f"\n{GREEN}{BOLD}✓ All checks passed! Ready to run tests.{RESET}\n")
    else:
        print(f"\n{YELLOW}{BOLD}⚠ Some checks failed. Review output above.{RESET}\n")

    return all_passed


def main():
    """Run all setup checks."""
    print(f"\n{BOLD}{'='*60}")
    print("NomNom Testing Environment Setup")
    print(f"{'='*60}{RESET}\n")

    results = {}

    # Run checks
    results["MCP CLI Available"] = check_mcp_cli()
    results["Playwright Tools Available"] = check_playwright_tools()
    results["Chrome Tools Available"] = check_chrome_tools()
    results["Playwright Browsers Installed"] = install_playwright_browsers()
    results["Test Fixtures Load"] = verify_test_fixtures()
    results["Directories Created"] = create_directories()
    results["Smoke Test Passed"] = run_smoke_test()

    # Print summary
    all_passed = print_summary(results)

    # Next steps
    if all_passed:
        print("Next steps:")
        print(f"  1. Start NomNom app: {BOLD}npm run dev{RESET}")
        print(f"  2. Run E2E tests: {BOLD}python tests/e2e/test_barcode_scanning.py{RESET}")
        print(f"  3. Try Chrome workflow: See {BOLD}tests/CHROME_WORKFLOWS.md{RESET}")
    else:
        print("Fix the failed checks above before running tests.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
