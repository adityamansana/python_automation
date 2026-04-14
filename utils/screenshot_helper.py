"""
LAYER 3 — UTILS LAYER: Screenshot Helper
==========================================
Captures screenshots and attaches them to Allure reports.
Called automatically by conftest on test failure.
"""

import allure
from datetime import datetime
from pathlib import Path

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotHelper:

    @staticmethod
    def capture(driver, test_name: str = "screenshot") -> str:
        """
        Save screenshot to disk and attach to current Allure report.
        Returns the saved file path.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = test_name.replace(" ", "_").replace("/", "_")
        filename = f"{safe_name}_{timestamp}.png"
        filepath = settings.SCREENSHOTS_DIR / filename

        driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot captured: {filepath}")

        # Attach to Allure
        with open(filepath, "rb") as f:
            allure.attach(
                f.read(),
                name=f"Screenshot — {test_name}",
                attachment_type=allure.attachment_type.PNG,
            )

        return str(filepath)
