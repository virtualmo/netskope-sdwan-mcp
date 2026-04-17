"""Focused tests for JWKS MCP tool behavior."""

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.jwks import get_jwks


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class JWKSToolsTest(unittest.TestCase):
    def test_get_jwks_success(self) -> None:
        client = Mock()
        client.jwks.get.return_value = {
            "keys": [{"kid": "kid-1", "kty": "RSA"}],
            "issuer": "netskope-sdwan",
        }

        with patch(
            "netskope_sdwan_mcp.tools.jwks.build_sdk_client",
            return_value=client,
        ):
            result = get_jwks()

        client.jwks.get.assert_called_once_with()
        self.assertEqual(
            result,
            {
                "keys": [{"kid": "kid-1", "kty": "RSA"}],
                "issuer": "netskope-sdwan",
            },
        )

    def test_get_jwks_sdk_error_path(self) -> None:
        client = Mock()
        client.jwks.get.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.jwks.build_sdk_client",
            return_value=client,
        ):
            result = get_jwks()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_jwks_serializes_raw_object_payload(self) -> None:
        client = Mock()
        client.jwks.get.return_value = {"keys": [{"kid": "kid-9"}]}

        with patch(
            "netskope_sdwan_mcp.tools.jwks.build_sdk_client",
            return_value=client,
        ):
            result = get_jwks()

        self.assertEqual(result, {"keys": [{"kid": "kid-9"}]})


if __name__ == "__main__":
    unittest.main()
