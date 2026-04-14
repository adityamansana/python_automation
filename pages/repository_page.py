"""
LAYER 5 — PAGE OBJECT LAYER: Repository Page
=============================================
Represents a GitHub repository page: github.com/{owner}/{repo}
"""

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class RepositoryPage(BasePage):

    _REPO_TITLE     = (By.CSS_SELECTOR, "strong[itemprop='name'] a, h1.d-flex strong")
    _STAR_BUTTON    = (By.CSS_SELECTOR, "button[aria-label*='Star']")
    _STAR_COUNT     = (By.CSS_SELECTOR, "a[href*='stargazers'] span.Counter")
    _FORK_COUNT     = (By.CSS_SELECTOR, "a[href*='members'] span.Counter")
    _README_SECTION = (By.CSS_SELECTOR, "article.markdown-body, #readme")
    _ABOUT_SECTION  = (By.CSS_SELECTOR, ".repository-content .BorderGrid-cell p")
    _LANGUAGE_STATS = (By.CSS_SELECTOR, "span.color-text-default.text-bold.mr-1")
    _FILE_LIST      = (By.CSS_SELECTOR, "table.files td.content span")

    @property
    def url(self) -> str:
        return ""   # dynamically navigated, not via navigate()

    def is_loaded(self) -> bool:
        return "github.com" in self.d.get_current_url() and \
               self.d.is_element_visible(self._REPO_TITLE, timeout=15)

    @allure.step("Verify repository page loaded")
    def verify_repo_page_loaded(self) -> "RepositoryPage":
        assert self.is_loaded(), "Repository page did not load correctly"
        return self

    @allure.step("Get repository name from page heading")
    def get_repo_name(self) -> str:
        return self.d.get_text(self._REPO_TITLE)

    @allure.step("Get star count")
    def get_star_count(self) -> str:
        if self.d.is_element_visible(self._STAR_COUNT, timeout=5):
            return self.d.get_text(self._STAR_COUNT)
        return "0"

    @allure.step("Verify README section is visible")
    def verify_readme_visible(self) -> "RepositoryPage":
        assert self.d.is_element_visible(self._README_SECTION, timeout=10), \
            "README section not visible"
        return self
