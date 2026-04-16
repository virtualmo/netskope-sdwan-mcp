"""Focused tests for configuration loading and SDK client creation."""

from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.client_factory import build_sdk_client
from netskope_sdwan_mcp.config import (
    ENV_API_TOKEN,
    ENV_BASE_URL,
    ENV_INSECURE,
    ENV_TIMEOUT,
    load_settings,
)
from netskope_sdwan_mcp.errors import ConfigurationError


class SettingsTest(unittest.TestCase):
    def test_missing_api_token_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            ConfigurationError,
            f"Missing required environment variable: {ENV_API_TOKEN}",
        ):
            load_settings({ENV_BASE_URL: "https://tenant.example.com"})

    def test_missing_base_url_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            ConfigurationError,
            f"Missing required environment variable: {ENV_BASE_URL}",
        ):
            load_settings({ENV_API_TOKEN: "token"})

    def test_invalid_timeout_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            ConfigurationError,
            f"{ENV_TIMEOUT} must be a positive integer",
        ):
            load_settings(
                {
                    ENV_BASE_URL: "https://tenant.example.com",
                    ENV_API_TOKEN: "token",
                    ENV_TIMEOUT: "abc",
                }
            )

    def test_insecure_boolean_parsing(self) -> None:
        truthy = load_settings(
            {
                ENV_BASE_URL: "https://tenant.example.com",
                ENV_API_TOKEN: "token",
                ENV_INSECURE: "yes",
            }
        )
        falsy = load_settings(
            {
                ENV_BASE_URL: "https://tenant.example.com",
                ENV_API_TOKEN: "token",
                ENV_INSECURE: "off",
            }
        )

        self.assertTrue(truthy.insecure)
        self.assertFalse(truthy.verify_ssl)
        self.assertFalse(falsy.insecure)
        self.assertTrue(falsy.verify_ssl)


class ClientFactoryTest(unittest.TestCase):
    def test_build_sdk_client_uses_real_constructor_arguments(self) -> None:
        captured: dict[str, object] = {}

        class FakeClient:
            def __init__(
                self,
                *,
                base_url: str,
                api_token: str,
                timeout: int,
                verify_ssl: bool,
            ) -> None:
                captured["base_url"] = base_url
                captured["api_token"] = api_token
                captured["timeout"] = timeout
                captured["verify_ssl"] = verify_ssl

        fake_module = types.SimpleNamespace(SDWANClient=FakeClient)

        with patch("netskope_sdwan_mcp.client_factory.import_module", return_value=fake_module):
            client = build_sdk_client(
                load_settings(
                    {
                        ENV_BASE_URL: "https://tenant.example.com/",
                        ENV_API_TOKEN: "token",
                        ENV_TIMEOUT: "45",
                        ENV_INSECURE: "true",
                    }
                )
            )

        self.assertIsInstance(client, FakeClient)
        self.assertEqual(captured["base_url"], "https://tenant.example.com")
        self.assertEqual(captured["api_token"], "token")
        self.assertEqual(captured["timeout"], 45)
        self.assertFalse(captured["verify_ssl"])
