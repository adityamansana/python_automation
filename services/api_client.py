"""
LAYER 4 — SERVICE LAYER: HTTP API Client
==========================================
Thin wrapper around the requests library.

  ApiClient.get()
  ApiClient.post()
"""

import json
import allure
import requests
from typing import Optional
from requests import Response

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ApiClient:
    """
    Generic HTTP client. Logs every request/response.
    Attaches response details to Allure automatically.
    """

    def __init__(self, base_url: str = None, headers: dict = None):
        self.base_url = base_url or settings.GITHUB_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        if headers:
            self.session.headers.update(headers)
        if settings.GITHUB_TOKEN:
            self.session.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    def get(self, endpoint: str, params: dict = None, **kwargs) -> Response:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"GET {url} | params={params}")
        response = self.session.get(url, params=params, **kwargs)
        self._log_response(response)
        return response

    def post(self, endpoint: str, payload: dict = None, **kwargs) -> Response:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"POST {url} | body={payload}")
        response = self.session.post(url, json=payload, **kwargs)
        self._log_response(response)
        return response

    def _log_response(self, response: Response) -> None:
        logger.info(f"Response: {response.status_code} | {response.url}")
        try:
            allure.attach(
                json.dumps(response.json(), indent=2),
                name=f"API Response — {response.status_code}",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            allure.attach(
                response.text[:2000],
                name=f"API Response — {response.status_code}",
                attachment_type=allure.attachment_type.TEXT,
            )
