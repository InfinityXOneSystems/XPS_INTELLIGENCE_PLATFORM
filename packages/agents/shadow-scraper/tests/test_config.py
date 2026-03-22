"""Unit tests for Shadow Scraper configuration.

These tests prove:
  1. robots.txt is IGNORED by default (operator directive).
  2. All parallelism caps have correct operator-approved defaults.
  3. Environment variable overrides work for every parameter.
  4. Invalid values are rejected by validate().
  5. as_metrics() returns a complete, serialisable dict.
  6. load_config() integrates all of the above end-to-end.
"""

import os
import sys

import pytest

# Allow the test to be run from the repo root without installing the package:
#   python -m pytest packages/agents/shadow-scraper/tests/ -v
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import ScraperConfig, _env_bool, _env_int, load_config


# ---------------------------------------------------------------------------
# Operator compliance defaults
# ---------------------------------------------------------------------------


class TestComplianceDefaults:
    """robots.txt MUST be ignored by default (operator directive)."""

    def test_robots_txt_ignored_by_default(self):
        cfg = ScraperConfig()
        assert cfg.respect_robots_txt is False, (
            "Operator directive: robots.txt must be IGNORED by default"
        )

    def test_respect_robots_txt_can_be_enabled(self):
        cfg = ScraperConfig(respect_robots_txt=True)
        assert cfg.respect_robots_txt is True


# ---------------------------------------------------------------------------
# Parallelism defaults
# ---------------------------------------------------------------------------


class TestParallelismDefaults:
    """All parallelism caps must match operator-approved values."""

    def test_max_concurrency_default(self):
        assert ScraperConfig().max_concurrency == 20

    def test_domain_concurrency_default(self):
        assert ScraperConfig().domain_concurrency == 5

    def test_max_requests_default(self):
        assert ScraperConfig().max_requests == 10_000

    def test_max_pages_default(self):
        assert ScraperConfig().max_pages == 5_000

    def test_max_runtime_seconds_default(self):
        assert ScraperConfig().max_runtime_seconds == 3_600

    def test_backoff_base_ms_default(self):
        assert ScraperConfig().backoff_base_ms == 250

    def test_backoff_max_ms_default(self):
        assert ScraperConfig().backoff_max_ms == 30_000

    def test_request_timeout_ms_default(self):
        assert ScraperConfig().request_timeout_ms == 30_000

    def test_retry_max_default(self):
        assert ScraperConfig().retry_max == 3


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    """validate() must accept valid configs and reject unsafe ones."""

    def test_default_config_validates(self):
        ScraperConfig().validate()  # must not raise

    def test_max_concurrency_zero_raises(self):
        with pytest.raises(AssertionError, match="max_concurrency"):
            ScraperConfig(max_concurrency=0).validate()

    def test_max_concurrency_over_limit_raises(self):
        with pytest.raises(AssertionError, match="max_concurrency"):
            ScraperConfig(max_concurrency=201).validate()

    def test_domain_concurrency_exceeds_global_raises(self):
        with pytest.raises(AssertionError, match="domain_concurrency"):
            ScraperConfig(max_concurrency=5, domain_concurrency=10).validate()

    def test_domain_concurrency_zero_raises(self):
        with pytest.raises(AssertionError, match="domain_concurrency"):
            ScraperConfig(domain_concurrency=0).validate()

    def test_max_requests_zero_raises(self):
        with pytest.raises(AssertionError, match="max_requests"):
            ScraperConfig(max_requests=0).validate()

    def test_max_pages_zero_raises(self):
        with pytest.raises(AssertionError, match="max_pages"):
            ScraperConfig(max_pages=0).validate()

    def test_max_runtime_seconds_zero_raises(self):
        with pytest.raises(AssertionError, match="max_runtime_seconds"):
            ScraperConfig(max_runtime_seconds=0).validate()

    def test_backoff_base_negative_raises(self):
        with pytest.raises(AssertionError, match="backoff_base_ms"):
            ScraperConfig(backoff_base_ms=-1).validate()

    def test_backoff_max_less_than_base_raises(self):
        with pytest.raises(AssertionError, match="backoff_max_ms"):
            ScraperConfig(backoff_base_ms=5000, backoff_max_ms=1000).validate()

    def test_request_timeout_too_small_raises(self):
        with pytest.raises(AssertionError, match="request_timeout_ms"):
            ScraperConfig(request_timeout_ms=50).validate()

    def test_retry_max_negative_raises(self):
        with pytest.raises(AssertionError, match="retry_max"):
            ScraperConfig(retry_max=-1).validate()

    def test_retry_max_over_limit_raises(self):
        with pytest.raises(AssertionError, match="retry_max"):
            ScraperConfig(retry_max=11).validate()

    def test_backoff_base_zero_is_valid(self):
        ScraperConfig(backoff_base_ms=0, backoff_max_ms=1000).validate()

    def test_retry_max_zero_is_valid(self):
        ScraperConfig(retry_max=0).validate()

    def test_domain_concurrency_equal_to_global_is_valid(self):
        ScraperConfig(max_concurrency=10, domain_concurrency=10).validate()

    def test_max_concurrency_boundary_200_is_valid(self):
        ScraperConfig(max_concurrency=200, domain_concurrency=10).validate()


# ---------------------------------------------------------------------------
# Metrics / observability
# ---------------------------------------------------------------------------


class TestMetrics:
    """as_metrics() must return a complete, serialisable dict."""

    EXPECTED_KEYS = {
        "respect_robots_txt",
        "max_concurrency",
        "domain_concurrency",
        "max_requests",
        "max_pages",
        "max_runtime_seconds",
        "backoff_base_ms",
        "backoff_max_ms",
        "request_timeout_ms",
        "retry_max",
    }

    def test_as_metrics_returns_dict(self):
        assert isinstance(ScraperConfig().as_metrics(), dict)

    def test_as_metrics_contains_all_keys(self):
        metrics = ScraperConfig().as_metrics()
        assert self.EXPECTED_KEYS == set(metrics.keys())

    def test_as_metrics_robots_txt_false_by_default(self):
        assert ScraperConfig().as_metrics()["respect_robots_txt"] is False

    def test_as_metrics_values_match_config(self):
        cfg = ScraperConfig(max_concurrency=30, max_pages=2000)
        m = cfg.as_metrics()
        assert m["max_concurrency"] == 30
        assert m["max_pages"] == 2000

    def test_as_metrics_is_json_serialisable(self):
        import json
        metrics = ScraperConfig().as_metrics()
        json.dumps(metrics)  # must not raise


# ---------------------------------------------------------------------------
# Environment variable helpers
# ---------------------------------------------------------------------------


class TestEnvBool:
    def test_missing_returns_default_false(self, monkeypatch):
        monkeypatch.delenv("SOME_BOOL_VAR", raising=False)
        assert _env_bool("SOME_BOOL_VAR", False) is False

    def test_missing_returns_default_true(self, monkeypatch):
        monkeypatch.delenv("SOME_BOOL_VAR", raising=False)
        assert _env_bool("SOME_BOOL_VAR", True) is True

    def test_true_string(self, monkeypatch):
        monkeypatch.setenv("SOME_BOOL_VAR", "true")
        assert _env_bool("SOME_BOOL_VAR", False) is True

    def test_false_string(self, monkeypatch):
        monkeypatch.setenv("SOME_BOOL_VAR", "false")
        assert _env_bool("SOME_BOOL_VAR", True) is False

    def test_uppercase_true(self, monkeypatch):
        monkeypatch.setenv("SOME_BOOL_VAR", "TRUE")
        assert _env_bool("SOME_BOOL_VAR", False) is True

    def test_one_string(self, monkeypatch):
        monkeypatch.setenv("SOME_BOOL_VAR", "1")
        assert _env_bool("SOME_BOOL_VAR", False) is True

    def test_zero_string_returns_false(self, monkeypatch):
        monkeypatch.setenv("SOME_BOOL_VAR", "0")
        assert _env_bool("SOME_BOOL_VAR", True) is False


class TestEnvInt:
    def test_missing_returns_default(self, monkeypatch):
        monkeypatch.delenv("SOME_INT_VAR", raising=False)
        assert _env_int("SOME_INT_VAR", 42) == 42

    def test_valid_value(self, monkeypatch):
        monkeypatch.setenv("SOME_INT_VAR", "99")
        assert _env_int("SOME_INT_VAR", 1) == 99

    def test_non_numeric_returns_default(self, monkeypatch):
        monkeypatch.setenv("SOME_INT_VAR", "notanumber")
        assert _env_int("SOME_INT_VAR", 7) == 7

    def test_below_min_clamped(self, monkeypatch):
        monkeypatch.setenv("SOME_INT_VAR", "0")
        assert _env_int("SOME_INT_VAR", 10, min_val=1) == 1

    def test_min_val_zero_allows_zero(self, monkeypatch):
        monkeypatch.setenv("SOME_INT_VAR", "0")
        assert _env_int("SOME_INT_VAR", 10, min_val=0) == 0


# ---------------------------------------------------------------------------
# load_config() integration — environment overrides
# ---------------------------------------------------------------------------


class TestLoadConfigEnvOverrides:
    """load_config() must respect every environment variable override."""

    def test_robots_txt_respect_via_env(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_RESPECT_ROBOTS_TXT", "true")
        assert load_config().respect_robots_txt is True

    def test_robots_txt_ignore_via_env(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_RESPECT_ROBOTS_TXT", "false")
        assert load_config().respect_robots_txt is False

    def test_robots_txt_ignore_when_env_absent(self, monkeypatch):
        monkeypatch.delenv("SCRAPER_RESPECT_ROBOTS_TXT", raising=False)
        assert load_config().respect_robots_txt is False

    def test_max_concurrency_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_MAX_CONCURRENCY", "50")
        assert load_config().max_concurrency == 50

    def test_domain_concurrency_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_MAX_CONCURRENCY", "50")
        monkeypatch.setenv("SCRAPER_DOMAIN_CONCURRENCY", "10")
        assert load_config().domain_concurrency == 10

    def test_max_requests_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_MAX_REQUESTS", "500")
        assert load_config().max_requests == 500

    def test_max_pages_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_MAX_PAGES", "250")
        assert load_config().max_pages == 250

    def test_max_runtime_seconds_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_MAX_RUNTIME_SECONDS", "1800")
        assert load_config().max_runtime_seconds == 1800

    def test_backoff_base_ms_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_BACKOFF_BASE_MS", "500")
        assert load_config().backoff_base_ms == 500

    def test_backoff_max_ms_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_BACKOFF_MAX_MS", "60000")
        assert load_config().backoff_max_ms == 60_000

    def test_request_timeout_ms_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_REQUEST_TIMEOUT_MS", "15000")
        assert load_config().request_timeout_ms == 15_000

    def test_retry_max_override(self, monkeypatch):
        monkeypatch.setenv("SCRAPER_RETRY_MAX", "5")
        assert load_config().retry_max == 5

    def test_load_config_validates(self, monkeypatch):
        """load_config() must call validate() — invalid env should raise."""
        monkeypatch.setenv("SCRAPER_MAX_CONCURRENCY", "0")
        with pytest.raises(AssertionError):
            load_config()

    def test_load_config_returns_scraperconfig(self, monkeypatch):
        for k in [
            "SCRAPER_RESPECT_ROBOTS_TXT",
            "SCRAPER_MAX_CONCURRENCY",
            "SCRAPER_DOMAIN_CONCURRENCY",
            "SCRAPER_MAX_REQUESTS",
            "SCRAPER_MAX_PAGES",
            "SCRAPER_MAX_RUNTIME_SECONDS",
            "SCRAPER_BACKOFF_BASE_MS",
            "SCRAPER_BACKOFF_MAX_MS",
            "SCRAPER_REQUEST_TIMEOUT_MS",
            "SCRAPER_RETRY_MAX",
        ]:
            monkeypatch.delenv(k, raising=False)
        cfg = load_config()
        assert isinstance(cfg, ScraperConfig)
