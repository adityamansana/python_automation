"""
LAYER 2 — CORE LAYER: Base Driver Wrapper
==========================================
Wraps the raw WebDriver with enhanced, reusable methods.
All Page Objects receive this wrapper — not the raw driver.

BaseDriver.click()
BaseDriver.type_text()
BaseDriver.get_text()
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from core.wait_helper import WaitHelper
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseDriver:
    """
    Enhanced driver wrapper. Page Objects extend BasePage which holds one of these.
    Centralises: waits, retries, logging, JS fallbacks.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WaitHelper(driver)
        self.actions = ActionChains(driver)

    # ── Navigation ──────────────────────────────────────────────────────
    def navigate_to(self, url: str) -> None:
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    # ── Interaction ──────────────────────────────────────────────────────
    def click(self, locator: tuple) -> None:
        logger.debug(f"Clicking: {locator}")
        element = self.wait.for_element_clickable(locator)
        element.click()

    def type_text(self, locator: tuple, text: str, clear_first: bool = True) -> None:
        logger.debug(f"Typing '{text}' into: {locator}")
        element = self.wait.for_element_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def press_enter(self, locator: tuple) -> None:
        element = self.wait.for_element_visible(locator)
        element.send_keys(Keys.RETURN)

    def hover(self, locator: tuple) -> None:
        element = self.wait.for_element_visible(locator)
        self.actions.move_to_element(element).perform()

    def scroll_to_element(self, locator: tuple) -> WebElement:
        element = self.wait.for_element_visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        return element

    # ── Reading ──────────────────────────────────────────────────────────
    def get_text(self, locator: tuple) -> str:
        return self.wait.for_element_visible(locator).text.strip()

    def get_attribute(self, locator: tuple, attribute: str) -> str:
        return self.wait.for_element_visible(locator).get_attribute(attribute)

    def get_elements(self, locator: tuple) -> list[WebElement]:
        return self.wait.for_elements_visible(locator)

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WaitHelper(self.driver, timeout).for_element_visible(locator)
            return True
        except Exception:
            return False

    # ── JavaScript ───────────────────────────────────────────────────────
    def execute_script(self, script: str, *args) -> any:
        return self.driver.execute_script(script, *args)

    def js_click(self, locator: tuple) -> None:
        """Fallback click via JavaScript — useful when element is obscured."""
        element = self.wait.for_element_visible(locator)
        self.driver.execute_script("arguments[0].click();", element)

    # ── Screenshot ───────────────────────────────────────────────────────
    def take_screenshot(self, path: str) -> None:
        self.driver.save_screenshot(path)
        logger.info(f"Screenshot saved: {path}")

    def quit(self) -> None:
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver session closed")
