"""
LAYER 5 — PAGE OBJECT LAYER: Base Page
========================================
Abstract base class for all Page Objects.

Every page object extends this — never instantiates WebDriver directly.

  BasePage (Python)
  self.driver_wrapper  (BaseDriver)
"""

import allure
from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from core.base_driver import BaseDriver
from core.wait_helper import WaitHelper
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage(ABC):
    """
    Abstract base for all Page Objects.

    Design decisions:
    - Holds BaseDriver wrapper (not raw WebDriver) -> hides Selenium complexity
    - Defines abstract `url` property -> forces each page to declare its route
    - navigate() + is_loaded() -> standard page load contract
    - All locators defined as class-level tuples -> easy to maintain
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.d = BaseDriver(driver)          # enhanced wrapper
        self.wait = WaitHelper(driver)
        self.base_url = settings.BASE_URL
        logger.info(f"Initialised page: {self.__class__.__name__}")

    @property
    @abstractmethod
    def url(self) -> str:
        """Each page declares its own relative URL."""
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        """Verify the page has fully loaded. Called after navigate()."""
        ...

    def navigate(self) -> "BasePage":
        """Navigate to this page's URL and verify it loaded."""
        full_url = f"{self.base_url}{self.url}"
        with allure.step(f"Navigate to {self.__class__.__name__}"):
            self.d.navigate_to(full_url)
            assert self.is_loaded(), f"{self.__class__.__name__} failed to load"
        return self

    def get_page_title(self) -> str:
        return self.d.get_title()

    def get_current_url(self) -> str:
        return self.d.get_current_url()
