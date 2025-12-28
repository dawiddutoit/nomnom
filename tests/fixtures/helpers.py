"""Helper utilities for browser automation tests.

Provides wrapper functions for Playwright MCP and Claude-in-Chrome tools.
"""

import json
import subprocess
from typing import Any


# ============================================================================
# MCP Command Execution
# ============================================================================

def mcp_call(server_tool: str, params: dict[str, Any]) -> dict[str, Any]:
    """Execute MCP command and return parsed result.

    Args:
        server_tool: Tool identifier (e.g., "plugin_playwright_playwright/browser_navigate")
        params: Tool parameters as dict

    Returns:
        Parsed JSON response from MCP tool

    Raises:
        subprocess.CalledProcessError: If MCP command fails
    """
    result = subprocess.run(
        ["mcp-cli", "call", server_tool, json.dumps(params)],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)


# ============================================================================
# Playwright MCP Helpers
# ============================================================================

def playwright_navigate(url: str) -> dict[str, Any]:
    """Navigate Playwright browser to URL."""
    return mcp_call("plugin_playwright_playwright/browser_navigate", {"url": url})


def playwright_snapshot() -> dict[str, Any]:
    """Get current page snapshot with interactive elements."""
    return mcp_call("plugin_playwright_playwright/browser_snapshot", {})


def playwright_click(element: str, ref: str) -> dict[str, Any]:
    """Click an element on the page.

    Args:
        element: Human-readable description
        ref: Element reference from snapshot
    """
    return mcp_call("plugin_playwright_playwright/browser_click", {
        "element": element,
        "ref": ref
    })


def playwright_type(text: str) -> dict[str, Any]:
    """Type text into focused element."""
    return mcp_call("plugin_playwright_playwright/browser_type", {"text": text})


def playwright_fill_form(fields: list[dict[str, str]]) -> dict[str, Any]:
    """Fill multiple form fields at once.

    Args:
        fields: List of field dicts with keys: name, type, ref, value
    """
    return mcp_call("plugin_playwright_playwright/browser_fill_form", {"fields": fields})


def playwright_screenshot(filename: str, fullPage: bool = False) -> dict[str, Any]:
    """Take screenshot of current page.

    Args:
        filename: Save path (e.g., "screenshots/test.png")
        fullPage: Capture full scrollable page vs viewport
    """
    return mcp_call("plugin_playwright_playwright/browser_take_screenshot", {
        "filename": filename,
        "fullPage": fullPage
    })


def playwright_wait_for(state: str, ref: str, timeout: int = 30000) -> dict[str, Any]:
    """Wait for element to reach specified state.

    Args:
        state: "visible", "hidden", "attached", "detached"
        ref: Element reference from snapshot
        timeout: Max wait time in milliseconds
    """
    return mcp_call("plugin_playwright_playwright/browser_wait_for", {
        "state": state,
        "ref": ref,
        "timeout": timeout
    })


def playwright_console_messages() -> list[dict[str, Any]]:
    """Get console log messages."""
    result = mcp_call("plugin_playwright_playwright/browser_console_messages", {})
    return result.get("messages", [])


def playwright_network_requests() -> list[dict[str, Any]]:
    """Get network requests made by the page."""
    result = mcp_call("plugin_playwright_playwright/browser_network_requests", {})
    return result.get("requests", [])


def playwright_close() -> dict[str, Any]:
    """Close browser instance."""
    return mcp_call("plugin_playwright_playwright/browser_close", {})


# ============================================================================
# Claude-in-Chrome Helpers
# ============================================================================

def chrome_get_tabs() -> dict[str, Any]:
    """Get information about current Chrome tabs."""
    return mcp_call("claude-in-chrome/tabs_context_mcp", {})


def chrome_create_tab(url: str) -> dict[str, Any]:
    """Create new Chrome tab and navigate to URL."""
    return mcp_call("claude-in-chrome/tabs_create_mcp", {"url": url})


def chrome_navigate(tab_id: int, url: str) -> dict[str, Any]:
    """Navigate Chrome tab to URL."""
    return mcp_call("claude-in-chrome/navigate", {
        "url": url,
        "tabId": tab_id
    })


def chrome_read_page(tab_id: int) -> dict[str, Any]:
    """Read visible text content from Chrome tab."""
    return mcp_call("claude-in-chrome/read_page", {"tabId": tab_id})


def chrome_find(tab_id: int, query: str) -> dict[str, Any]:
    """Find elements on page by text or selector."""
    return mcp_call("claude-in-chrome/find", {
        "tabId": tab_id,
        "query": query
    })


def chrome_form_input(tab_id: int, selector: str, value: str) -> dict[str, Any]:
    """Fill form field in Chrome tab."""
    return mcp_call("claude-in-chrome/form_input", {
        "tabId": tab_id,
        "selector": selector,
        "value": value
    })


def chrome_console_messages(tab_id: int, pattern: str | None = None) -> dict[str, Any]:
    """Read console messages from Chrome tab.

    Args:
        tab_id: Chrome tab ID
        pattern: Optional regex pattern to filter messages
    """
    params: dict[str, Any] = {"tabId": tab_id}
    if pattern:
        params["pattern"] = pattern
    return mcp_call("claude-in-chrome/read_console_messages", params)


def chrome_network_requests(tab_id: int) -> dict[str, Any]:
    """Get network requests from Chrome tab."""
    return mcp_call("claude-in-chrome/read_network_requests", {"tabId": tab_id})


def chrome_create_gif(tab_id: int, filename: str) -> dict[str, Any]:
    """Create GIF recording of workflow.

    Args:
        tab_id: Chrome tab ID
        filename: Save path (e.g., "workflow.gif")
    """
    return mcp_call("claude-in-chrome/gif_creator", {
        "tabId": tab_id,
        "filename": filename
    })


# ============================================================================
# Test Verification Helpers
# ============================================================================

def verify_product_displayed(snapshot: dict[str, Any], product_name: str, calories: float) -> bool:
    """Verify product is displayed with correct data.

    Args:
        snapshot: Page snapshot from playwright_snapshot()
        product_name: Expected product name
        calories: Expected calorie value

    Returns:
        True if product data is displayed correctly
    """
    content = snapshot.get("content", "")
    name_found = product_name.lower() in content.lower()
    calories_found = str(int(calories)) in content
    return name_found and calories_found


def verify_no_console_errors(messages: list[dict[str, Any]]) -> bool:
    """Check console messages for errors.

    Args:
        messages: Console messages from playwright_console_messages()

    Returns:
        True if no error messages found
    """
    errors = [msg for msg in messages if msg.get("type") == "error"]
    return len(errors) == 0


def verify_api_called(requests: list[dict[str, Any]], api_url_pattern: str) -> bool:
    """Verify specific API was called.

    Args:
        requests: Network requests from playwright_network_requests()
        api_url_pattern: Pattern to match (e.g., "openfoodfacts.org")

    Returns:
        True if API was called
    """
    return any(api_url_pattern in req.get("url", "") for req in requests)


def find_element_ref(snapshot: dict[str, Any], element_id: str) -> str | None:
    """Extract element ref from snapshot.

    Args:
        snapshot: Page snapshot from playwright_snapshot()
        element_id: Element identifier to search for

    Returns:
        Element ref string or None if not found
    """
    # Implementation depends on snapshot structure
    # This is a placeholder - adjust based on actual snapshot format
    elements = snapshot.get("elements", [])
    for elem in elements:
        if element_id in elem.get("id", "") or element_id in elem.get("ref", ""):
            return elem.get("ref")
    return None


def wait_for_api_call(url_pattern: str, timeout_seconds: int = 10) -> bool:
    """Poll network requests until API call is detected.

    Args:
        url_pattern: Pattern to match in request URL
        timeout_seconds: Max time to wait

    Returns:
        True if API call detected within timeout
    """
    import time
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        requests = playwright_network_requests()
        if verify_api_called(requests, url_pattern):
            return True
        time.sleep(0.5)

    return False
