"""
LAYER 2 — CORE LAYER: Wait Helper
===================================
Centralised wait strategies. Selenium's explicit waits are verbose;
this helper wraps them cleanly.

  WaitHelper.for_element_visible()
  WaitHelper.for_url_contains()
  WaitHelper.for_element_visible()
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WaitHelper:
    def __init__(self, driver: WebDriver, timeout: int = None):
        self.driver = driver
        self.timeout = timeout or settings.EXPLICIT_WAIT
        self.wait = WebDriverWait(driver, self.timeout)

    def for_element_visible(self, locator: tuple) -> WebElement:
        """Wait until element is present and visible."""
        logger.debug(f"Waiting for element visible: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator))

    def for_element_clickable(self, locator: tuple) -> WebElement:
        """Wait until element is clickable."""
        logger.debug(f"Waiting for element clickable: {locator}")
        return self.wait.until(EC.element_to_be_clickable(locator))

    def for_elements_visible(self, locator: tuple) -> list[WebElement]:
        """Wait until all matching elements are visible."""
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def for_url_contains(self, partial_url: str) -> bool:
        """Wait until current URL contains the given string."""
        logger.debug(f"Waiting for URL to contain: {partial_url}")
        return self.wait.until(EC.url_contains(partial_url))

    def for_title_contains(self, partial_title: str) -> bool:
        """Wait until page title contains the given string."""
        return self.wait.until(EC.title_contains(partial_title))

    def for_text_in_element(self, locator: tuple, text: str) -> bool:
        """Wait until element contains the expected text."""
        return self.wait.until(EC.text_to_be_present_in_element(locator, text))

    def for_element_invisible(self, locator: tuple) -> bool:
        """Wait until element is invisible or removed."""
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def until(self, condition, message: str = "") -> any:
        """Generic wait — pass any ExpectedCondition."""
        try:
            return self.wait.until(condition)
        except TimeoutException:
            logger.error(f"Timeout waiting for condition. {message}")
            raise
