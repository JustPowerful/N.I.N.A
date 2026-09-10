"""
This is a runtime in-memory registry for BrowserManager instances, keyed by session ID.
It allows for the creation and retrieval of BrowserManager instances associated with specific chat sessions.
"""

from app.browser.manager import BrowserManager


_browser_managers: dict[str, BrowserManager] = {}


def get_browser_manager(session_id: str) -> BrowserManager:
    """
    Return the BrowserManager associated with a chat session.

    Creates it only if this session does not have one yet.
    """
    browser_manager = _browser_managers.get(session_id)
    if browser_manager is None:
        browser_manager = BrowserManager()
        _browser_managers[session_id] = browser_manager
    return browser_manager

async def remove_browser_manager(session_id: str):
    """
    Remove the BrowserManager associated with a chat session.

    This is used to clean up resources when a session is deleted.
    """
    browser_manager = _browser_managers.pop(session_id, None)
    if browser_manager is not None:
        await browser_manager.stop()