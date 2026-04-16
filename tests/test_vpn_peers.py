"""Focused tests for VPN-peer MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.vpn_peers import (
    get_vpn_peer,
    list_vpn_peers,
    serialize_vpn_peer,
)


@dataclass
class FakeVPNPeer:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class VPNPeerToolsTest(unittest.TestCase):
    def test_list_vpn_peers_success(self) -> None:
        client = Mock()
        client.vpn_peers.list.return_value = [
            FakeVPNPeer(
                id="peer-001",
                name="Branch Peer",
                raw={"id": "peer-001", "name": "Branch Peer", "type": "ipsec"},
            ),
            FakeVPNPeer(
                id="peer-002",
                name="HQ Peer",
                raw={"id": "peer-002", "name": "HQ Peer"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.vpn_peers.build_sdk_client",
            return_value=client,
        ):
            result = list_vpn_peers(filter="name: Branch")

        client.vpn_peers.list.assert_called_once_with(filter="name: Branch")
        self.assertEqual(
            result,
            [
                {"id": "peer-001", "name": "Branch Peer", "type": "ipsec"},
                {"id": "peer-002", "name": "HQ Peer"},
            ],
        )

    def test_get_vpn_peer_success(self) -> None:
        client = Mock()
        client.vpn_peers.get.return_value = FakeVPNPeer(
            id="peer-001",
            name="Branch Peer",
            raw={"id": "peer-001", "name": "Branch Peer", "status": "up"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.vpn_peers.build_sdk_client",
            return_value=client,
        ):
            result = get_vpn_peer("peer-001")

        client.vpn_peers.get.assert_called_once_with("peer-001")
        self.assertEqual(result["id"], "peer-001")
        self.assertEqual(result["name"], "Branch Peer")
        self.assertEqual(result["status"], "up")

    def test_get_vpn_peer_not_found_path(self) -> None:
        client = Mock()
        client.vpn_peers.get.side_effect = NotFoundError("vpn peer not found")

        with patch(
            "netskope_sdwan_mcp.tools.vpn_peers.build_sdk_client",
            return_value=client,
        ):
            result = get_vpn_peer("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "vpn peer not found")

    def test_list_vpn_peers_sdk_error_path(self) -> None:
        client = Mock()
        client.vpn_peers.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.vpn_peers.build_sdk_client",
            return_value=client,
        ):
            result = list_vpn_peers()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_vpn_peer_supports_sdk_objects(self) -> None:
        vpn_peer = FakeVPNPeer(
            id="peer-123",
            name="Regional Peer",
            raw={"id": "peer-123", "name": "Regional Peer", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_vpn_peer(vpn_peer),
            {"id": "peer-123", "name": "Regional Peer", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
