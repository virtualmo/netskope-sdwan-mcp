"""Focused tests for policy MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.policies import (
    get_policy,
    list_policies,
    serialize_policy,
)


@dataclass
class FakePolicy:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class PolicyToolsTest(unittest.TestCase):
    def test_list_policies_success(self) -> None:
        client = Mock()
        client.policies.list.return_value = [
            FakePolicy(
                id="policy-001",
                name="Allow Web",
                raw={"id": "policy-001", "name": "Allow Web", "action": "allow"},
            ),
            FakePolicy(
                id="policy-002",
                name="Deny Legacy",
                raw={"id": "policy-002", "name": "Deny Legacy"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.policies.build_sdk_client",
            return_value=client,
        ):
            result = list_policies(filter="name: Allow")

        client.policies.list.assert_called_once_with(filter="name: Allow")
        self.assertEqual(
            result,
            [
                {"id": "policy-001", "name": "Allow Web", "action": "allow"},
                {"id": "policy-002", "name": "Deny Legacy"},
            ],
        )

    def test_get_policy_success(self) -> None:
        client = Mock()
        client.policies.get.return_value = FakePolicy(
            id="policy-001",
            name="Allow Web",
            raw={"id": "policy-001", "name": "Allow Web", "priority": 10},
        )

        with patch(
            "netskope_sdwan_mcp.tools.policies.build_sdk_client",
            return_value=client,
        ):
            result = get_policy("policy-001")

        client.policies.get.assert_called_once_with("policy-001")
        self.assertEqual(result["id"], "policy-001")
        self.assertEqual(result["name"], "Allow Web")
        self.assertEqual(result["priority"], 10)

    def test_get_policy_not_found_path(self) -> None:
        client = Mock()
        client.policies.get.side_effect = NotFoundError("policy not found")

        with patch(
            "netskope_sdwan_mcp.tools.policies.build_sdk_client",
            return_value=client,
        ):
            result = get_policy("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "policy not found")

    def test_list_policies_sdk_error_path(self) -> None:
        client = Mock()
        client.policies.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.policies.build_sdk_client",
            return_value=client,
        ):
            result = list_policies()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_policy_supports_sdk_objects(self) -> None:
        policy = FakePolicy(
            id="policy-123",
            name="Allow App",
            raw={"id": "policy-123", "name": "Allow App", "tenant_id": "tenant-9"},
        )

        self.assertEqual(
            serialize_policy(policy),
            {"id": "policy-123", "name": "Allow App", "tenant_id": "tenant-9"},
        )


if __name__ == "__main__":
    unittest.main()
