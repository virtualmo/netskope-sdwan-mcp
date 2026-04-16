"""Focused tests for tenant MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.tenants import get_tenant, list_tenants, serialize_tenant


@dataclass
class FakeTenant:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class TenantToolsTest(unittest.TestCase):
    def test_list_tenants_success(self) -> None:
        client = Mock()
        client.tenants.list.return_value = [
            FakeTenant(id="tenant-001", name="Tenant One", raw={"id": "tenant-001", "name": "Tenant One", "region": "eu"}),
            FakeTenant(id="tenant-002", name="Tenant Two", raw={"id": "tenant-002", "name": "Tenant Two"}),
        ]

        with patch("netskope_sdwan_mcp.tools.tenants.build_sdk_client", return_value=client):
            result = list_tenants(filter="name: Tenant")

        client.tenants.list.assert_called_once_with(filter="name: Tenant")
        self.assertEqual(
            result,
            [
                {"id": "tenant-001", "name": "Tenant One", "region": "eu"},
                {"id": "tenant-002", "name": "Tenant Two"},
            ],
        )

    def test_get_tenant_success(self) -> None:
        client = Mock()
        client.tenants.get.return_value = FakeTenant(
            id="tenant-001",
            name="Tenant One",
            raw={"id": "tenant-001", "name": "Tenant One", "status": "active"},
        )

        with patch("netskope_sdwan_mcp.tools.tenants.build_sdk_client", return_value=client):
            result = get_tenant("tenant-001")

        client.tenants.get.assert_called_once_with("tenant-001")
        self.assertEqual(result["id"], "tenant-001")
        self.assertEqual(result["name"], "Tenant One")
        self.assertEqual(result["status"], "active")

    def test_get_tenant_not_found_path(self) -> None:
        client = Mock()
        client.tenants.get.side_effect = NotFoundError("tenant not found")

        with patch("netskope_sdwan_mcp.tools.tenants.build_sdk_client", return_value=client):
            result = get_tenant("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "tenant not found")

    def test_list_tenants_sdk_error_path(self) -> None:
        client = Mock()
        client.tenants.list.side_effect = APIResponseError("upstream failure")

        with patch("netskope_sdwan_mcp.tools.tenants.build_sdk_client", return_value=client):
            result = list_tenants()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "APIResponseError")
        self.assertEqual(result["error"]["message"], "upstream failure")

    def test_serialize_tenant_supports_sdk_objects(self) -> None:
        tenant = FakeTenant(
            id="tenant-123",
            name="Tenant HQ",
            raw={"id": "tenant-123", "name": "Tenant HQ", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_tenant(tenant),
            {"id": "tenant-123", "name": "Tenant HQ", "account_id": "acct-9"},
        )
