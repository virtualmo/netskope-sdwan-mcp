"""Focused tests for CA-certificate MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.ca_certificates import (
    get_ca_certificate,
    list_ca_certificates,
    serialize_ca_certificate,
)


@dataclass
class FakeCACertificate:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class CACertificateToolsTest(unittest.TestCase):
    def test_list_ca_certificates_success(self) -> None:
        client = Mock()
        client.ca_certificates.list.return_value = [
            FakeCACertificate(
                id="cert-001",
                name="Corporate Root",
                raw={"id": "cert-001", "name": "Corporate Root", "issuer": "Corp CA"},
            ),
            FakeCACertificate(
                id="cert-002",
                name="Partner Root",
                raw={"id": "cert-002", "name": "Partner Root"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.ca_certificates.build_sdk_client",
            return_value=client,
        ):
            result = list_ca_certificates(filter="name: Corporate")

        client.ca_certificates.list.assert_called_once_with(filter="name: Corporate")
        self.assertEqual(
            result,
            [
                {"id": "cert-001", "name": "Corporate Root", "issuer": "Corp CA"},
                {"id": "cert-002", "name": "Partner Root"},
            ],
        )

    def test_get_ca_certificate_success(self) -> None:
        client = Mock()
        client.ca_certificates.get.return_value = FakeCACertificate(
            id="cert-001",
            name="Corporate Root",
            raw={"id": "cert-001", "name": "Corporate Root", "fingerprint": "abc123"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.ca_certificates.build_sdk_client",
            return_value=client,
        ):
            result = get_ca_certificate("cert-001")

        client.ca_certificates.get.assert_called_once_with("cert-001")
        self.assertEqual(result["id"], "cert-001")
        self.assertEqual(result["name"], "Corporate Root")
        self.assertEqual(result["fingerprint"], "abc123")

    def test_get_ca_certificate_not_found_path(self) -> None:
        client = Mock()
        client.ca_certificates.get.side_effect = NotFoundError("ca certificate not found")

        with patch(
            "netskope_sdwan_mcp.tools.ca_certificates.build_sdk_client",
            return_value=client,
        ):
            result = get_ca_certificate("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "ca certificate not found")

    def test_list_ca_certificates_sdk_error_path(self) -> None:
        client = Mock()
        client.ca_certificates.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.ca_certificates.build_sdk_client",
            return_value=client,
        ):
            result = list_ca_certificates()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_ca_certificate_supports_sdk_objects(self) -> None:
        ca_certificate = FakeCACertificate(
            id="cert-123",
            name="Internal Root",
            raw={"id": "cert-123", "name": "Internal Root", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_ca_certificate(ca_certificate),
            {"id": "cert-123", "name": "Internal Root", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
