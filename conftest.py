"""
CONFTEST.PY — The Fixture Layer
================================
This is the heart of the pytest framework.

"""

import time
import pytest
import allure

from selenium.webdriver.remote.webdriver import WebDriver

from config.settings import settings
from core.driver_factory import DriverFactory
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.repository_page import RepositoryPage
from services.github_api_service import GitHubApiService
from utils.screenshot_helper import ScreenshotHelper
from utils.pdf_reporter import PdfReporter
from utils.logger import get_logger

logger = get_logger("conftest")


# ══════════════════════════════════════════════════════════════════════════════
# DRIVER FIXTURE — scope: function
# Equivalent to: test.extend({ page: ... }) in playwright fixtures
# Every test gets a FRESH driver. Parallel-safe.
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def driver():
    """
    Core WebDriver fixture. Equivalent to the `page` fixture in Playwright.
    - Creates driver before test
    - Yields to test
    - Quits driver after test (pass or fail)
    """
    _driver = DriverFactory.create_driver()
    _driver.implicitly_wait(settings.IMPLICIT_WAIT)
    _driver.maximize_window()
    logger.info("Driver created — test starting")

    yield _driver

    logger.info("Driver cleanup — test ended")
    _driver.quit()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE FIXTURES — scope: function
# Equivalent to: fixtures/page.fixture.ts in the TS framework
# Page objects are injected into tests — tests never instantiate pages directly
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def home_page(driver: WebDriver) -> HomePage:
    """
    Injects a HomePage instance. Driver dependency injected automatically.
    Playwright equivalent:
      test.extend({ homePage: async ({ page }) => new HomePage(page) })
    """
    return HomePage(driver)


@pytest.fixture(scope="function")
def search_results_page(driver: WebDriver) -> SearchResultsPage:
    return SearchResultsPage(driver)


@pytest.fixture(scope="function")
def repository_page(driver: WebDriver) -> RepositoryPage:
    return RepositoryPage(driver)


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE FIXTURES — scope: session
# Equivalent to: fixtures/api.fixture.ts in the TS framework
# API services are stateless — reuse across the entire session
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def github_api() -> GitHubApiService:
    """
    Session-scoped API service.
    Playwright equivalent: test.extend({ githubApi: ... }) with scope='worker'
    """
    return GitHubApiService()


# ══════════════════════════════════════════════════════════════════════════════
# STEP TRACKER FIXTURE
# Collects steps during a test — fed into PdfReporter at teardown
# No direct Playwright equivalent; custom pattern for PDF generation
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def step_tracker():
    """
    List that test methods append steps to.
    Injected into tests that need PDF step tracking.
    """
    steps = []
    yield steps


# ══════════════════════════════════════════════════════════════════════════════
# REPORT CONTEXT FIXTURE
# Bundles all reporting context — passed to PdfReporter
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function", autouse=True)
def test_metadata(request):
    """
    Auto-use fixture: enriches every test's Allure report with metadata.
    Equivalent to: allure.step() wrappers auto-applied in playwright fixtures.
    """
    allure.dynamic.feature(
        request.node.get_closest_marker("feature").args[0]
        if request.node.get_closest_marker("feature")
        else request.fspath.purebasename
    )
    allure.dynamic.story(request.node.name)
    allure.dynamic.label("environment", settings.ENV.upper())
    allure.dynamic.label("browser", settings.BROWSER)
    yield


# ══════════════════════════════════════════════════════════════════════════════
# FAILURE HOOK — screenshot + PDF on failure
# Equivalent to: test.afterEach with testInfo.status check in Playwright
# ══════════════════════════════════════════════════════════════════════════════

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest hook — runs after every test phase (setup / call / teardown).
    Captures screenshot and generates PDF on failure.

    Playwright equivalent:
      test.afterEach(async ({ page }, testInfo) => {
        if (testInfo.status !== testInfo.expectedStatus) {
          await page.screenshot({ path: 'failure.png' });
        }
      });
    """
    outcome = yield
    report = outcome.get_result()

    # Only act on the actual test call phase (not setup/teardown)
    if report.when == "call":
        item._test_status = "PASSED" if report.passed else (
            "FAILED" if report.failed else "SKIPPED"
        )
        item._test_duration = report.duration

        # Get driver if the test used it
        driver_fixture = item.funcargs.get("driver")
        step_fixture   = item.funcargs.get("step_tracker", [])

        screenshot_path = None

        if report.failed and driver_fixture and settings.SCREENSHOT_ON_FAILURE:
            screenshot_path = ScreenshotHelper.capture(
                driver_fixture, test_name=item.name
            )
            logger.warning(f"Test FAILED — screenshot captured: {screenshot_path}")

        # Generate PDF report
        if settings.PDF_REPORT_ENABLED:
            error_msg = None
            if report.failed and report.longrepr:
                error_msg = str(report.longrepr)[:800]

            pdf = PdfReporter(
                test_name=item.name,
                status=item._test_status,
                duration_seconds=getattr(item, "_test_duration", 0.0),
                steps=step_fixture,
                screenshot_path=screenshot_path,
                error_message=error_msg,
                extra_data={
                    "Environment": settings.ENV.upper(),
                    "Browser": settings.BROWSER,
                    "Base URL": settings.BASE_URL,
                },
            )
            pdf.generate()
