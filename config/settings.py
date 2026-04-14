"""
LAYER 1 — CONFIG LAYER
======================
Loads environment variables, exposes typed config properties.

settings.py
os.environ / python-dotenv
"""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent


def _load_env() -> None:
    env_name = os.getenv("ENV", "dev")
    env_file = PROJECT_ROOT / "config" / "environments" / f"{env_name}.env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
    else:
        load_dotenv(PROJECT_ROOT / ".env", override=True)


_load_env()


class Settings:
    """
    Central configuration object — single source of truth.
    All tests and fixtures consume this; nothing reads os.environ directly.
    """

    # Browser
    BROWSER: str = os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # Timeouts (seconds)
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT: int = int(os.getenv("EXPLICIT_WAIT", "30"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "60"))

    # URLs
    BASE_URL: str = os.getenv("BASE_URL", "https://github.com")
    GITHUB_API_BASE_URL: str = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    # Reporting
    SCREENSHOT_ON_FAILURE: bool = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    PDF_REPORT_ENABLED: bool = os.getenv("PDF_REPORT_ENABLED", "true").lower() == "true"
    ALLURE_RESULTS_DIR: Path = PROJECT_ROOT / "reports" / "allure-results"
    PDF_REPORTS_DIR: Path = PROJECT_ROOT / "reports" / "pdf"
    SCREENSHOTS_DIR: Path = PROJECT_ROOT / "reports" / "screenshots"

    ENV: str = os.getenv("ENV", "dev")

    @classmethod
    def ensure_dirs(cls) -> None:
        for d in [cls.ALLURE_RESULTS_DIR, cls.PDF_REPORTS_DIR, cls.SCREENSHOTS_DIR]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
