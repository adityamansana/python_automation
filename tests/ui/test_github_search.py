"""
LAYER 6 — TEST LAYER: GitHub Search UI Tests
=============================================

KEY PATTERN: Tests are declarative — they describe WHAT, not HOW.
  - No Selenium calls in tests
  - No locators in tests
  - No driver setup in tests
  Everything is injected via fixtures (conftest.py)

  def test_search_shows_results(home_page, search_results_page, step_tracker):
      ...
"""

import allure
import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage, RepositoryCard
from utils.allure_helper import allure_step, AllureHelper
from utils.data_generator import DataGenerator


# ── Allure suite metadata ─────────────────────────────────────────────────────
@allure.epic("GitHub Web Application")
@allure.feature("Search Functionality")
class TestGitHubSearch:
    """
    Test suite for GitHub search feature.
      class TestGitHubSearch:
    """

    # ─────────────────────────────────────────────────────────────────────────
    # TC-001: Basic search flow
    # ─────────────────────────────────────────────────────────────────────────
    @allure.story("User can search for repositories")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Search for 'selenium' returns results")
    @pytest.mark.smoke
    @pytest.mark.ui
    @pytest.mark.github_search
    def test_search_returns_results(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        step_tracker: list,
    ):
        """
        Verifies: user can perform a search from the home page and
        see results on the results page.
        """
        query = "selenium"

        with allure_step("Navigate to GitHub home page"):
            step_tracker.append("Navigate to GitHub home page")
            home_page.navigate()

        with allure_step(f"Perform search for '{query}'"):
            step_tracker.append(f"Type search query: {query}")
            home_page.search(query)

        with allure_step("Verify search results page loaded"):
            step_tracker.append("Verify URL contains /search")
            search_results_page.verify_page_loaded()

        with allure_step("Verify search query persists in search box"):
            step_tracker.append("Assert query visible in search input")
            search_results_page.verify_query_in_search_box(query)

        with allure_step("Verify results are displayed"):
            step_tracker.append("Assert result cards > 0")
            search_results_page.verify_results_visible()

    # ─────────────────────────────────────────────────────────────────────────
    # TC-002: Result cards have expected structure
    # ─────────────────────────────────────────────────────────────────────────
    @allure.story("Search results contain repository information")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Search result cards display repository name and URL")
    @pytest.mark.regression
    @pytest.mark.ui
    @pytest.mark.github_search
    def test_result_cards_have_name_and_url(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        step_tracker: list,
    ):
        query = "playwright"

        with allure_step("Navigate and search"):
            step_tracker.append("Navigate to github.com")
            home_page.navigate()
            step_tracker.append(f"Search for '{query}'")
            home_page.search(query)

        with allure_step("Parse result cards"):
            step_tracker.append("Extract repository cards from DOM")
            search_results_page.verify_page_loaded()
            cards: list[RepositoryCard] = search_results_page.get_result_cards()
            AllureHelper.attach_json(
                "Parsed Result Cards",
                {f"result_{i}": {"name": c.name, "url": c.url, "lang": c.language}
                 for i, c in enumerate(cards[:5])}
            )

        with allure_step("Assert first result has name and URL"):
            step_tracker.append("Assert card[0].name is not empty")
            step_tracker.append("Assert card[0].url contains github.com")
            assert cards, "No result cards found"
            first: RepositoryCard = cards[0]
            assert first.name and first.name != "N/A", \
                f"First result has no name: {first}"
            assert "github.com" in first.url, \
                f"First result URL invalid: {first.url}"

    # ─────────────────────────────────────────────────────────────────────────
    # TC-003: Navigate to a repository from search results
    # ─────────────────────────────────────────────────────────────────────────
    @allure.story("User can navigate from search to a repository page")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Clicking first search result opens a repository page")
    @pytest.mark.regression
    @pytest.mark.ui
    @pytest.mark.github_search
    def test_click_first_result_opens_repo_page(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        repository_page,
        step_tracker: list,
    ):
        query = "pytest"

        with allure_step("Navigate and search"):
            step_tracker.append("Navigate to github.com and search")
            home_page.navigate()
            home_page.search(query)

        with allure_step("Get first result and navigate"):
            step_tracker.append("Parse first result card URL")
            search_results_page.verify_page_loaded()
            search_results_page.verify_results_visible()
            search_results_page.click_first_result()

        with allure_step("Verify repository page loaded"):
            step_tracker.append("Assert URL changed to repo page")
            assert "github.com" in repository_page.get_current_url(), \
                "Did not navigate to a GitHub repository page"
            AllureHelper.attach_text(
                "Landed URL",
                repository_page.get_current_url()
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TC-004: Parametrised search — multiple queries
    # ─────────────────────────────────────────────────────────────────────────
    @allure.story("Search works for multiple technology queries")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Parametrised search — {query}")
    @pytest.mark.parametrize("query", ["allure", "pytest-xdist", "webdriver-manager"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_search_works_for_multiple_queries(
        self,
        query: str,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        step_tracker: list,
    ):
        """
        Parametrised test — 3 test cases generated automatically.
        """
        step_tracker.append(f"Navigate to home and search for '{query}'")
        home_page.navigate()
        home_page.search(query)

        step_tracker.append("Verify results page loaded and has results")
        search_results_page.verify_page_loaded()
        search_results_page.verify_results_visible()

        AllureHelper.attach_text("Search Query Used", query)
