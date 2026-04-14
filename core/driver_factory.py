"""
LAYER 2 — CORE LAYER: Driver Factory
=====================================
Centralises WebDriver creation — tests never instantiate drivers directly.

  DriverFactory.create_driver()
  WebDriver instance
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class DriverFactory:
    """
    Factory class — one method, returns ready-to-use WebDriver.
    Adding a new browser = adding one method here. Tests stay unchanged.
    This is the Factory design pattern in action.
    """

    @staticmethod
    def create_driver(browser: str = None, headless: bool = None) -> webdriver.Remote:
        browser = (browser or settings.BROWSER).lower()
        headless = headless if headless is not None else settings.HEADLESS

        logger.info(f"Creating {browser} driver | headless={headless}")

        if browser == "chrome":
            return DriverFactory._create_chrome(headless)
        elif browser == "firefox":
            return DriverFactory._create_firefox(headless)
        elif browser == "edge":
            return DriverFactory._create_edge(headless)
        else:
            raise ValueError(f"Unsupported browser: '{browser}'. Supported: chrome, firefox, edge")

    @staticmethod
    def _create_chrome(headless: bool) -> webdriver.Chrome:
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        return driver

    @staticmethod
    def _create_firefox(headless: bool) -> webdriver.Firefox:
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        return driver

    @staticmethod
    def _create_edge(headless: bool) -> webdriver.Edge:
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        return driver
