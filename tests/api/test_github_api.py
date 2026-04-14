"""
LAYER 6 — TEST LAYER: GitHub API Tests
========================================
Pure API tests — no browser, no driver.

API tests run much faster and can validate the data layer independently.
Hybrid strategy: API tests validate data; UI tests validate presentation.
"""

import allure
import pytest

from services.github_api_service import GitHubApiService, RepoResult
from utils.allure_helper import allure_step, AllureHelper


@allure.epic("GitHub Web Application")
@allure.feature("GitHub API")
class TestGitHubApi:
    """
    API test suite. Uses the session-scoped github_api fixture.
    No driver needed — pure HTTP via requests.
    """

    @allure.story("Repository search API returns valid results")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Search API returns repositories for 'selenium'")
    @pytest.mark.api
    @pytest.mark.smoke
    def test_search_repositories_returns_results(
        self, github_api: GitHubApiService, step_tracker: list
    ):
        with allure_step("Call GitHub search API for 'selenium'"):
            step_tracker.append("POST /search/repositories?q=selenium")
            results: list[RepoResult] = github_api.search_repositories("selenium")

        with allure_step("Validate response structure"):
            step_tracker.append("Assert results list is not empty")
            assert results, "API returned empty results list"
            assert len(results) >= 5, f"Expected >= 5 results, got {len(results)}"

        with allure_step("Validate first result fields"):
            step_tracker.append("Assert first result has name and URL")
            first: RepoResult = results[0]
            assert first.name, "First result has no name"
            assert "github.com" in first.url, f"Invalid URL: {first.url}"
            assert first.stars >= 0, "Stars count is negative"

            AllureHelper.attach_json("Top 3 Results", {
                f"result_{i}": {
                    "name": r.full_name,
                    "stars": r.stars,
                    "language": r.language,
                }
                for i, r in enumerate(results[:3])
            })

    @allure.story("API and UI results are consistent")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("API search results are sorted by stars descending")
    @pytest.mark.api
    @pytest.mark.regression
    def test_search_results_sorted_by_stars(
        self, github_api: GitHubApiService, step_tracker: list
    ):
        """
        Hybrid validation pattern:
        Use API to verify sorting logic — no browser needed.
        with Playwright's route interception + API client.
        """
        with allure_step("Fetch repositories sorted by stars"):
            step_tracker.append("GET /search/repositories?q=pytest&sort=stars")
            results = github_api.search_repositories("pytest", sort="stars", per_page=10)

        with allure_step("Verify descending star order"):
            step_tracker.append("Assert stars[i] >= stars[i+1] for all results")
            assert results, "No results returned"
            star_counts = [r.stars for r in results]
            AllureHelper.attach_json("Star Counts", {
                f"repo_{i}_{r.name}": r.stars
                for i, r in enumerate(results)
            })
            for i in range(len(star_counts) - 1):
                assert star_counts[i] >= star_counts[i + 1], (
                    f"Results not sorted by stars: "
                    f"{results[i].name}({star_counts[i]}) < "
                    f"{results[i+1].name}({star_counts[i+1]})"
                )

    @allure.story("Rate limit API is accessible")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Rate limit endpoint returns valid data")
    @pytest.mark.api
    @pytest.mark.smoke
    def test_rate_limit_returns_valid_data(
        self, github_api: GitHubApiService, step_tracker: list
    ):
        with allure_step("Fetch rate limit status"):
            step_tracker.append("GET /rate_limit")
            data = github_api.get_rate_limit()

        with allure_step("Assert rate limit structure"):
            step_tracker.append("Assert 'resources' key present in response")
            assert "resources" in data, f"Unexpected response: {data}"
            core = data["resources"]["core"]
            assert "limit" in core and "remaining" in core
            AllureHelper.attach_json("Rate Limit", {
                "limit": core["limit"],
                "remaining": core["remaining"],
                "used": core.get("used", "N/A"),
            })

    @allure.story("Single repository fetch")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Fetch a known public repository by owner/repo")
    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.parametrize("owner,repo", [
        ("SeleniumHQ", "selenium"),
        ("pytest-dev", "pytest"),
    ])
    def test_get_specific_repository(
        self,
        owner: str,
        repo: str,
        github_api: GitHubApiService,
        step_tracker: list,
    ):
        with allure_step(f"Fetch repository {owner}/{repo}"):
            step_tracker.append(f"GET /repos/{owner}/{repo}")
            data = github_api.get_repository(owner, repo)

        with allure_step("Validate response fields"):
            step_tracker.append("Assert full_name, stars, and html_url are present")
            assert data["full_name"] == f"{owner}/{repo}"
            assert data["stargazers_count"] >= 0
            assert "github.com" in data["html_url"]
            AllureHelper.attach_json(f"{owner}/{repo} Details", {
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "language": data.get("language"),
                "open_issues": data["open_issues_count"],
            })
