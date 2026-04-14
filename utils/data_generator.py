"""
LAYER 3 — UTILS LAYER: Test Data Generator
============================================
Faker-based data generator for dynamic test data.
"""

from faker import Faker

fake = Faker()


class DataGenerator:
    """Centralized test data factory. Keeps test data logic out of test files."""

    # ── Search terms ─────────────────────────────────────────────────────
    GITHUB_SEARCH_QUERIES = [
        "selenium",
        "playwright",
        "pytest",
        "test automation framework",
        "python requests",
    ]

    REPO_SORT_OPTIONS = ["Best match", "Most stars", "Most forks", "Recently updated"]

    @staticmethod
    def random_search_query() -> str:
        return fake.random_element(DataGenerator.GITHUB_SEARCH_QUERIES)

    @staticmethod
    def random_email() -> str:
        return fake.email()

    @staticmethod
    def random_username() -> str:
        return fake.user_name()

    @staticmethod
    def random_password(length: int = 12) -> str:
        return fake.password(length=length, special_chars=True, digits=True, upper_case=True)
