"""
LAYER 3 — UTILS LAYER: Allure Helper
======================================
Convenience wrappers for Allure decorators and dynamic steps.

  allure_step() context manager
  AllureHelper.attach_text()
  AllureHelper.attach_json()
"""

import json
import allure
from contextlib import contextmanager
from functools import wraps
from typing import Callable

from utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def allure_step(step_name: str):
    """
    Context manager for Allure steps. Use instead of the @allure.step decorator
    when you need dynamic step names at runtime.

    Usage:
        with allure_step("Search for 'selenium'"):
            search_page.search("selenium")
    """
    with allure.step(step_name):
        logger.info(f"STEP: {step_name}")
        yield


def step(name: str) -> Callable:
    """
    Decorator form of allure_step for reusable test actions.

    Usage:
        @step("Perform GitHub search")
        def do_search(page, query):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with allure.step(name):
                logger.info(f"STEP: {name}")
                return func(*args, **kwargs)
        return wrapper
    return decorator


class AllureHelper:

    @staticmethod
    def attach_text(name: str, content: str) -> None:
        allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_json(name: str, data: dict) -> None:
        allure.attach(
            json.dumps(data, indent=2),
            name=name,
            attachment_type=allure.attachment_type.JSON,
        )

    @staticmethod
    def attach_html(name: str, html: str) -> None:
        allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)

    @staticmethod
    def attach_url(name: str, url: str) -> None:
        allure.attach(f'<a href="{url}">{url}</a>', name=name,
                      attachment_type=allure.attachment_type.HTML)

    @staticmethod
    def set_description(description: str) -> None:
        allure.dynamic.description(description)

    @staticmethod
    def set_severity(severity: str) -> None:
        """severity: blocker | critical | normal | minor | trivial"""
        allure.dynamic.severity(severity)
