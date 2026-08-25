from playwright.async_api import Playwright, BrowserContext, async_playwright, Browser
from pathlib import Path
from .session import BrowserSession
from seleniumbase import sb_cdp
from seleniumbase.undetected.cdp_driver import cdp_util

class BrowserManager:
    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.session: BrowserSession | None = None
        self.profile_path = Path("./data/browser_profile")

        # SeleniumBase CDP (Chrome DevTools Protocol) integration
        self.sb = None

    async def start(self):
        if self.session is not None:
            return

        self.profile_path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.sb = await cdp_util.start_async(
            user_data_dir=str(self.profile_path),
        )

        self.playwright = await async_playwright().start()
        

        endpoint_url = self.sb.get_endpoint_url()

        self.browser = await self.playwright.chromium.connect_over_cdp(
            endpoint_url=endpoint_url,
            timeout=60000  # Set a timeout of 60 seconds
        )

        self.context = self.browser.contexts[0]

        if self.context.pages:
            page = self.context.pages[0]
        else:
            page = await self.context.new_page()

        self.session = BrowserSession(
            self.context,
            page
        )

    async def stop(self):
        if self.context:
            await self.context.close()
            self.context = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        if self.session:
            self.session = None

    async def open(self, url: str):
        await self.start()

        assert self.session is not None

        await self.session.page.goto(url, wait_until="domcontentloaded")

        return await self.session.describe()


    async def current_page(self):
        await self.start()

        assert self.session is not None

        return await self.session.describe()

    async def click(self, element_id: str):
        await self.start()
        assert self.session is not None

        element = self.session.element_map.get(element_id)

        assert element is not None, f"Element with ID {element_id} not found."

        await element.click()

        await self.session.page.wait_for_load_state("domcontentloaded")

        return await self.session.describe()


    async def type(self, element_id: str, text: str):
        await self.start()
        assert self.session is not None
        element = self.session.element_map.get(element_id)
        assert element is not None, f"Element with ID {element_id} not found."
        await element.fill(text)
        return await self.session.describe()

    async def press(self, element_id: str, key: str):
        await self.start()
        assert self.session is not None
        element = self.session.element_map.get(element_id)
        assert element is not None, f"Element with ID {element_id} not found."
        await element.press(key)
        return await self.session.describe()

    async def screenshot(self) -> bytes:
        await self.start()

        assert self.session is not None

        return await self.session.page.screenshot(
            full_page=True
        )