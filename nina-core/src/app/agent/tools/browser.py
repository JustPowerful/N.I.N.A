import base64

from app.agent.tool import Tool
from app.browser.manager import BrowserManager


class BrowserTools:
    def __init__(self, browser: BrowserManager) -> None:
        self.browser = browser

    async def open_url(self, url: str):
        """
        Open a URL in the browser and return a description of the loaded page.

        Args:
            url: The URL to open.
        """

        return await self.browser.open(url)

    async def current_page(self):
        """
        Return a description of the currently loaded page.
        """

        return await self.browser.current_page()

    async def click_element(self, element_id: str):
        """
        Click an interactive element identified by its browser element ID.

        Args:
            element_id: The ID of the element to click.
        """

        return await self.browser.click(element_id)

    async def type_text(self, element_id: str, text: str):
        """
        Fill a text input or textarea identified by its browser element ID.

        Args:
            element_id: The ID of the element to fill.
            text: The text to enter.
        """

        return await self.browser.type(element_id, text)

    async def press_key(self, element_id: str, key: str):
        """
        Press a keyboard key on an element identified by its browser element ID.

        Args:
            element_id: The ID of the element to target.
            key: The key to press, such as Enter or Tab.
        """

        return await self.browser.press(element_id, key)

    async def screenshot(self):
        """
        Capture a screenshot of the current page.
        """

        image_bytes = await self.browser.screenshot()
        return {
            "mime_type": "image/png",
            "data_base64": base64.b64encode(image_bytes).decode("utf-8"),
        }

    async def stop_browser(self):
        """
        Close the browser session.
        """

        await self.browser.stop()
        return {"success": True}

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="open_url",
                description=(
                    "Navigate to a URL in the browser. "
                    "IMPORTANT: Only use this when you actually need to navigate to a different URL. "
                    "If the browser is already on the required page, DO NOT call this tool again. "
                    "Use current_page instead to inspect the existing page and continue from it. "
                    "Do not use this tool after a user manually completes a CAPTCHA or other verification."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to open.",
                        }
                    },
                    "required": ["url"],
                },
                function=self.open_url,
            ),
            Tool(
                name="current_page",
                description="Return a description of the currently loaded page.",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                function=self.current_page,
            ),
            Tool(
                name="click_element",
                description="Click an interactive element identified by its browser element ID.",
                parameters={
                    "type": "object",
                    "properties": {
                        "element_id": {
                            "type": "string",
                            "description": "The ID of the element to click.",
                        }
                    },
                    "required": ["element_id"],
                },
                function=self.click_element,
            ),
            Tool(
                name="type_text",
                description="Fill a text input or textarea identified by its browser element ID.",
                parameters={
                    "type": "object",
                    "properties": {
                        "element_id": {
                            "type": "string",
                            "description": "The ID of the element to fill.",
                        },
                        "text": {
                            "type": "string",
                            "description": "The text to enter.",
                        },
                    },
                    "required": ["element_id", "text"],
                },
                function=self.type_text,
            ),
            Tool(
                name="press_key",
                description="Press a keyboard key on an element identified by its browser element ID.",
                parameters={
                    "type": "object",
                    "properties": {
                        "element_id": {
                            "type": "string",
                            "description": "The ID of the element to target.",
                        },
                        "key": {
                            "type": "string",
                            "description": "The key to press, such as Enter or Tab.",
                        },
                    },
                    "required": ["element_id", "key"],
                },
                function=self.press_key,
            ),
            Tool(
                name="screenshot",
                description="Capture a screenshot of the current page.",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                function=self.screenshot,
            ),
            Tool(
                name="stop_browser",
                description="Close the browser session.",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                function=self.stop_browser,
            ),
        ]

