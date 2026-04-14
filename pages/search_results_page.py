"""
LAYER 5 — PAGE OBJECT LAYER: GitHub Search Results Page
=========================================================
Represents github.com/search
"""

import allure
from dataclasses import dataclass
from typing import Optional
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RepositoryCard:
    """
    Typed data object for a single search result card.
    Mirrors the TypeScript interface RepoCard in the TS framework.
    """
    name: str
    description: Optional[str]
    language: Optional[str]
    stars: Optional[str]
    url: str


class SearchResultsPage(BasePage):
    """
    GitHub search results page.
    Handles: result cards, pagination, filter tabs, sort options.
    """

    # ── Locators ─────────────────────────────────────────────────────────
    _SEARCH_INPUT       = (By.CSS_SELECTOR, "input[name='q']")
    _RESULTS_HEADER     = (By.CSS_SELECTOR, "div[data-testid='results-list'], div.codesearch-results h3")
    _RESULT_COUNT       = (By.CSS_SELECTOR, "h3.f5.color-fg-muted em")

    # Repository result cards
    _REPO_LIST_ITEM     = (By.CSS_SELECTOR, "li.repo-list-item, div[data-testid='results-list'] > div")
    _REPO_NAME          = (By.CSS_SELECTOR, "a[href*='/'][class*='v-align-middle']")
    _REPO_DESC          = (By.CSS_SELECTOR, "p.mb-1")
    _REPO_LANG          = (By.CSS_SELECTOR, "span[itemprop='programmingLanguage']")
    _REPO_STARS         = (By.CSS_SELECTOR, "a[href*='stargazers']")

    # Filters
    _REPOSITORIES_TAB   = (By.CSS_SELECTOR, "a[href*='type=repositories']")
    _SORT_DROPDOWN      = (By.CSS_SELECTOR, "summary[data-target*='sort']")
    _SORT_BY_STARS      = (By.CSS_SELECTOR, "a[href*='s=stars']")
    _SORT_BY_UPDATED    = (By.CSS_SELECTOR, "a[href*='s=updated']")

    # Pagination
    _NEXT_PAGE_BUTTON   = (By.CSS_SELECTOR, "a[aria-label='Next Page']")
    _PREV_PAGE_BUTTON   = (By.CSS_SELECTOR, "a[aria-label='Previous Page']")

    # Language filter sidebar
    _LANGUAGE_FILTER    = (By.CSS_SELECTOR, "div[data-filter-type='language']")

    @property
    def url(self) -> str:
        return "/search"

    def is_loaded(self) -> bool:
        return "search" in self.d.get_current_url()

    # ── Core assertions ─────────────────────────────────────────────────

    @allure.step("Verify search results page loaded")
    def verify_page_loaded(self) -> "SearchResultsPage":
        assert self.is_loaded(), "Search results page did not load"
        assert self.d.is_element_visible(self._SEARCH_INPUT), "Search input not visible"
        return self

    @allure.step("Verify search query in input: {expected_query}")
    def verify_query_in_search_box(self, expected_query: str) -> "SearchResultsPage":
        actual = self.d.get_attribute(self._SEARCH_INPUT, "value")
        assert expected_query.lower() in actual.lower(), (
            f"Expected '{expected_query}' in search box, got '{actual}'"
        )
        return self

    @allure.step("Verify results are visible")
    def verify_results_visible(self) -> "SearchResultsPage":
        results = self.get_result_cards()
        assert len(results) > 0, "No search results found on page"
        logger.info(f"Found {len(results)} result cards")
        return self

    @allure.step("Verify result count text is present")
    def verify_result_count_shown(self) -> "SearchResultsPage":
        assert self.d.is_element_visible(self._RESULT_COUNT, timeout=10), \
            "Result count not visible"
        count_text = self.d.get_text(self._RESULT_COUNT)
        logger.info(f"Result count text: {count_text}")
        return self

    # ── Data extraction ─────────────────────────────────────────────────

    @allure.step("Get all repository result cards")
    def get_result_cards(self) -> list[RepositoryCard]:
        """
        Parse all visible result cards into typed RepositoryCard objects.
        This is the core data extraction method used by tests.
        """
        cards = []
        try:
            items = self.d.get_elements(self._REPO_LIST_ITEM)
            for item in items:
                try:
                    # Name & URL
                    name_el = item.find_elements(*self._REPO_NAME)
                    name = name_el[0].text.strip() if name_el else "N/A"
                    url  = name_el[0].get_attribute("href") if name_el else ""

                    # Description
                    desc_els = item.find_elements(*self._REPO_DESC)
                    desc = desc_els[0].text.strip() if desc_els else None

                    # Language
                    lang_els = item.find_elements(*self._REPO_LANG)
                    lang = lang_els[0].text.strip() if lang_els else None

                    # Stars
                    star_els = item.find_elements(*self._REPO_STARS)
                    stars = star_els[0].text.strip() if star_els else None

                    cards.append(RepositoryCard(
                        name=name, description=desc,
                        language=lang, stars=stars, url=url,
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse one result card: {e}")
        except Exception as e:
            logger.warning(f"Could not extract result cards: {e}")

        return cards

    def get_first_result_name(self) -> str:
        cards = self.get_result_cards()
        assert cards, "No results to read"
        return cards[0].name

    def get_result_count_text(self) -> str:
        if self.d.is_element_visible(self._RESULT_COUNT, timeout=5):
            return self.d.get_text(self._RESULT_COUNT)
        return ""

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Click Repositories filter tab")
    def click_repositories_tab(self) -> "SearchResultsPage":
        if self.d.is_element_visible(self._REPOSITORIES_TAB, timeout=5):
            self.d.click(self._REPOSITORIES_TAB)
        return self

    @allure.step("Sort results by stars")
    def sort_by_stars(self) -> "SearchResultsPage":
        self.d.click(self._SORT_DROPDOWN)
        self.d.click(self._SORT_BY_STARS)
        return self

    @allure.step("Search for new query: {query}")
    def search_again(self, query: str) -> "SearchResultsPage":
        self.d.type_text(self._SEARCH_INPUT, query)
        self.d.press_enter(self._SEARCH_INPUT)
        return self

    @allure.step("Click first result")
    def click_first_result(self) -> None:
        cards = self.get_result_cards()
        assert cards, "No results to click"
        self.d.navigate_to(cards[0].url)
