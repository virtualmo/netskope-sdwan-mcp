"""Focused tests for cloud-account MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.cloud_accounts import (
    get_cloud_account,
    list_cloud_accounts,
    serialize_cloud_account,
)


@dataclass
class FakeCloudAccount:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class CloudAccountToolsTest(unittest.TestCase):
    def test_list_cloud_accounts_success(self) -> None:
        client = Mock()
        client.cloud_accounts.list.return_value = [
            FakeCloudAccount(
                id="ca-001",
                name="AWS Prod",
                raw={"id": "ca-001", "name": "AWS Prod", "provider": "aws"},
            ),
            FakeCloudAccount(
                id="ca-002",
                name="Azure Shared",
                raw={"id": "ca-002", "name": "Azure Shared"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.cloud_accounts.build_sdk_client",
            return_value=client,
        ):
            result = list_cloud_accounts(filter="name: AWS")

        client.cloud_accounts.list.assert_called_once_with(filter="name: AWS")
        self.assertEqual(
            result,
            [
                {"id": "ca-001", "name": "AWS Prod", "provider": "aws"},
                {"id": "ca-002", "name": "Azure Shared"},
            ],
        )

    def test_get_cloud_account_success(self) -> None:
        client = Mock()
        client.cloud_accounts.get.return_value = FakeCloudAccount(
            id="ca-001",
            name="AWS Prod",
            raw={"id": "ca-001", "name": "AWS Prod", "region": "eu-west-1"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.cloud_accounts.build_sdk_client",
            return_value=client,
        ):
            result = get_cloud_account("ca-001")

        client.cloud_accounts.get.assert_called_once_with("ca-001")
        self.assertEqual(result["id"], "ca-001")
        self.assertEqual(result["name"], "AWS Prod")
        self.assertEqual(result["region"], "eu-west-1")

    def test_get_cloud_account_not_found_path(self) -> None:
        client = Mock()
        client.cloud_accounts.get.side_effect = NotFoundError("cloud account not found")

        with patch(
            "netskope_sdwan_mcp.tools.cloud_accounts.build_sdk_client",
            return_value=client,
        ):
            result = get_cloud_account("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "cloud account not found")

    def test_list_cloud_accounts_sdk_error_path(self) -> None:
        client = Mock()
        client.cloud_accounts.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.cloud_accounts.build_sdk_client",
            return_value=client,
        ):
            result = list_cloud_accounts()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_cloud_account_supports_sdk_objects(self) -> None:
        cloud_account = FakeCloudAccount(
            id="ca-123",
            name="GCP Shared",
            raw={"id": "ca-123", "name": "GCP Shared", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_cloud_account(cloud_account),
            {"id": "ca-123", "name": "GCP Shared", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
