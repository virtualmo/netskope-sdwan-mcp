"""Focused tests for shared tool-facing error mapping."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.errors import ConfigurationError, serialize_tool_error


class ForbiddenError(Exception):
    """SDK-shaped authorization error used in tests."""


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class ErrorMappingTest(unittest.TestCase):
    def test_configuration_error_is_mapped_clearly(self) -> None:
        result = serialize_tool_error(
            ConfigurationError("Missing required environment variable: NETSKOPESDWAN_BASE_URL")
        )

        self.assertEqual(result["status"], "configuration_error")
        self.assertEqual(result["error"]["type"], "ConfigurationError")

    def test_not_found_error_is_mapped_clearly(self) -> None:
        result = serialize_tool_error(NotFoundError("gateway not found"))

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "gateway not found")

    def test_forbidden_error_is_mapped_clearly(self) -> None:
        result = serialize_tool_error(
            ForbiddenError("403 forbidden authorization: Bearer secret-token")
        )

        self.assertEqual(result["status"], "forbidden")
        self.assertEqual(result["error"]["type"], "AuthorizationError")
        self.assertEqual(
            result["error"]["message"],
            "Request is not authorized for this resource.",
        )

    def test_unexpected_error_is_safe(self) -> None:
        result = serialize_tool_error(RuntimeError("token=secret failure"))

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(
            result["error"]["message"],
            "Unexpected error while processing request.",
        )


if __name__ == "__main__":
    unittest.main()
