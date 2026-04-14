"""
LAYER 5 — PAGE OBJECT LAYER: GitHub Home Page
===============================================
"""

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class HomePage(BasePage):
    """
    GitHub home page.
    Locators defined as class-level tuples: (By.Strategy, "selector")
    This is identical to how we define locators in the TS BasePage.
    """

    # ── Locators ─────────────────────────────────────────────────────────
    # Use data-testid where available — most resilient to UI changes
    _SEARCH_INPUT     = (By.NAME, "q")
    _SEARCH_BUTTON    = (By.CSS_SELECTOR, "[data-target='qbsearch-input.inputButton']")
    _NAV_SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
    _HERO_HEADING     = (By.CSS_SELECTOR, "h1.h0-mktg, h1[class*='heading']")
    _SIGN_IN_LINK     = (By.LINK_TEXT, "Sign in")
    _SIGN_UP_BUTTON   = (By.LINK_TEXT, "Sign up for GitHub")

    @property
    def url(self) -> str:
        return ""   # root path

    def is_loaded(self) -> bool:
        return "github" in self.d.get_current_url().lower()

    @allure.step("Click search box on home page")
    def click_search(self) -> "HomePage":
        self.d.click(self._SEARCH_BUTTON)
        return self

    @allure.step("Type search query: {query}")
    def type_search_query(self, query: str) -> "HomePage":
        self.d.type_text(self._SEARCH_INPUT, query)
        return self

    @allure.step("Submit search")
    def submit_search(self) -> None:
        self.d.press_enter(self._SEARCH_INPUT)

    def search(self, query: str) -> None:
        """Full search flow from home page."""
        self.click_search()
        self.type_search_query(query)
        self.submit_search()
        logger.info(f"Search submitted from home page: '{query}'")
