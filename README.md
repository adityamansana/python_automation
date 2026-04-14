# Python Selenium pytest Allure — Layered Test Automation Framework

A production-grade, 7-layer test automation framework for Python/Selenium/pytest/Allure.
Mirrors the architecture of the companion Playwright TypeScript framework.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 7 — REPORTING LAYER                              │
│  Allure HTML Suite Report + Per-test PDF Reports        │
├─────────────────────────────────────────────────────────┤
│  LAYER 6 — TEST LAYER                                   │
│  tests/ui/   tests/api/   (*.py spec files)             │
├─────────────────────────────────────────────────────────┤
│  LAYER 5 — PAGE OBJECT LAYER                            │
│  pages/  BasePage → HomePage → SearchResultsPage        │
├─────────────────────────────────────────────────────────┤
│  LAYER 4 — SERVICE LAYER                               │
│  services/  ApiClient → GitHubApiService                │
├─────────────────────────────────────────────────────────┤
│  LAYER 3 — UTILS LAYER                                 │
│  utils/  Logger, AllureHelper, ScreenshotHelper, PDF    │
├─────────────────────────────────────────────────────────┤
│  LAYER 2 — CORE LAYER                                  │
│  core/  DriverFactory, BaseDriver, WaitHelper           │
├─────────────────────────────────────────────────────────┤
│  LAYER 1 — CONFIG LAYER                                │
│  config/  settings.py + environment .env files          │
└─────────────────────────────────────────────────────────┘
```


## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment
cp .env .env.local   # edit as needed
export ENV=dev

# 3. Run all tests
pytest

# 4. Run only smoke tests
pytest -m smoke

# 5. Run only API tests (no browser)
pytest -m api

# 6. Run in parallel (4 workers)
pytest -n 4

# 7. Generate and open Allure report
allure serve reports/allure-results
```

## Project Structure

```
selenium_pytest_framework/
├── config/
│   ├── settings.py              # Central config (Layer 1)
│   └── environments/
│       ├── dev.env
│       ├── staging.env
│       └── prod.env
├── core/
│   ├── driver_factory.py        # Browser creation (Layer 2)
│   ├── base_driver.py           # Enhanced WebDriver wrapper
│   └── wait_helper.py           # Explicit wait strategies
├── utils/
│   ├── logger.py                # Centralised logging (Layer 3)
│   ├── allure_helper.py         # Allure step helpers
│   ├── screenshot_helper.py     # Screenshot + Allure attach
│   ├── pdf_reporter.py          # Per-test PDF generation
│   └── data_generator.py        # Faker-based test data
├── services/
│   ├── api_client.py            # requests wrapper (Layer 4)
│   └── github_api_service.py    # GitHub API domain service
├── pages/
│   ├── base_page.py             # Abstract POM base (Layer 5)
│   ├── home_page.py             # GitHub home page
│   ├── search_results_page.py   # Search results page
│   └── repository_page.py       # Repository detail page
├── tests/
│   ├── ui/
│   │   └── test_github_search.py  # UI test suite (Layer 6)
│   └── api/
│       └── test_github_api.py     # API test suite
├── reports/
│   ├── allure-results/          # Raw Allure JSON (Layer 7)
│   ├── pdf/                     # Per-test PDF reports
│   └── screenshots/             # Failure screenshots
├── conftest.py                  # Fixture layer (pytest DI)
├── pytest.ini                   # pytest configuration
├── requirements.txt
└── .env                         # Root environment config
```
