"""
LAYER 4 — SERVICE LAYER: GitHub API Service
=============================================
Domain-specific API service for GitHub.

Wraps raw HTTP calls into semantically named methods:
  GitHubApiService.search_repositories("selenium")
"""

from dataclasses import dataclass
from typing import Optional
from requests import Response

from services.api_client import ApiClient
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RepoResult:
    """Typed result object — mirrors TypeScript interfaces."""
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    language: Optional[str]
    url: str


class GitHubApiService:
    """
    High-level GitHub API operations.
    Tests call this — never the raw ApiClient.
    """

    def __init__(self):
        self.client = ApiClient()

    def search_repositories(
        self, query: str, sort: str = "stars", per_page: int = 10
    ) -> list[RepoResult]:
        """
        Search GitHub repositories.
        Returns a typed list of RepoResult objects.
        """
        response = self.client.get(
            "/search/repositories",
            params={"q": query, "sort": sort, "per_page": per_page},
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        return [
            RepoResult(
                name=item["name"],
                full_name=item["full_name"],
                description=item.get("description"),
                stars=item["stargazers_count"],
                language=item.get("language"),
                url=item["html_url"],
            )
            for item in items
        ]

    def get_repository(self, owner: str, repo: str) -> dict:
        """Fetch a single repository by owner/repo."""
        response = self.client.get(f"/repos/{owner}/{repo}")
        response.raise_for_status()
        return response.json()

    def get_rate_limit(self) -> dict:
        """Check GitHub API rate limit status."""
        response = self.client.get("/rate_limit")
        response.raise_for_status()
        return response.json()
