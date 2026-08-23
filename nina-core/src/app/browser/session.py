from playwright.async_api import BrowserContext, Page

class BrowserSession:
    def __init__(self, context: BrowserContext, page: Page) -> None:
        self.context = context
        self.page = page

        self.element_map = {}

    # Refresh the element map to get the latest interactive elements on the page
    async def refresh_elements(self):
        self.element_map.clear()

        # Get all interactive elements on the page
        elements = await self.page.locator(
            "a, button, input, textarea, select, [role='button'], "
            "[role='link'], [role='textbox'], [role='checkbox']"
        ).all()

        for index, element in enumerate(elements):
            element_id = f'e{index + 1}'

            try:
                if not await element.is_visible():
                    continue

                self.element_map[element_id] = element
            except Exception:
                continue


    # Return a description of the current page as a form of a dictionary, including the URL, title and a list of interactive elements with their attributes
    async def describe(self) -> dict:
        await self.refresh_elements()

        elements = []

        for element_id, element in self.element_map.items():
            try:
                tag = await element.evaluate("el => el.tagName.toLowerCase()")
                role = await element.get_attribute("role")
                name = await element.get_attribute("name")
                placeholder = await element.get_attribute("placeholder")
                text = await element.inner_text()   

                elements.append({
                    "id": element_id,
                    "tag": tag,
                    "role": role,
                    "name": name,
                    "placeholder": placeholder,
                    "text": text[:200]  # Limit text to first 200 characters
                })
            except Exception:
                continue

        content = await self.page.locator("body").inner_text()

        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "content": content[:15000], # Limit content to first 15000 characters
            "elements": elements,
        }

    def get_element(self, element_id: str):
        element = self.element_map.get(element_id)
        if element is None:
            raise ValueError(f"Element with ID '{element_id}' not found.")
            
        return element
    