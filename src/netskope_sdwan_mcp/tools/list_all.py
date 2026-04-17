"""Generic auto-paginating MCP list tool backed by the SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from .address_groups import serialize_address_group
from .applications import serialize_application
from .audit_events import serialize_audit_event
from .ca_certificates import serialize_ca_certificate
from .client_templates import serialize_client_template
from .clients import serialize_client
from .cloud_accounts import serialize_cloud_account
from .controller_operators import serialize_controller_operator
from .controllers import serialize_controller
from .device_groups import serialize_device_group
from .gateways import serialize_gateway
from .gateway_groups import serialize_gateway_group
from .gateway_templates import serialize_gateway_template
from .inventory_devices import serialize_inventory_device
from .ntp_configs import serialize_ntp_config
from .overlay_tags import serialize_overlay_tag
from .policies import serialize_policy
from .radius_servers import serialize_radius_server
from .segments import serialize_segment
from .site_commands import serialize_site_command
from .software import serialize_software_item
from .tenants import serialize_tenant
from .user_groups import serialize_user_group
from .users import serialize_user
from .vpn_peers import serialize_vpn_peer

DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 100
DEFAULT_LIMIT = 500
MAX_LIMIT = 5000


@dataclass(frozen=True)
class ListAllResourceSpec:
    manager_getter: Callable[[Any], Any]
    page_fetcher: Callable[..., list[Any]]
    serializer: Callable[[Any], dict[str, Any]]
    required_fields: tuple[str, ...] = ()


def list_all(
    resource: str,
    filter: str | None = None,
    first: int = DEFAULT_PAGE_SIZE,
    sort: str | None = None,
    limit: int | None = None,
    group_id: str | None = None,
    created_at_from: str | None = None,
    created_at_to: str | None = None,
    type: str | None = None,
    subtype: str | None = None,
    activity: str | None = None,
) -> dict[str, Any]:
    """Fetch all pages for a supported paginated SDK list resource."""
    try:
        normalized_resource = _normalize_resource(resource)
        spec = _get_resource_spec(normalized_resource)
        page_size = _validate_page_size(first)
        effective_limit = _validate_limit(limit)
        _validate_resource_requirements(
            normalized_resource,
            group_id=group_id,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
        )

        client = build_sdk_client()
        manager = spec.manager_getter(client)

        items: list[dict[str, Any]] = []
        after: str | None = None
        pages_fetched = 0
        seen_cursors: set[str] = set()
        last_page_info: dict[str, Any] | None = None
        last_cursors: dict[str, Any] | None = None
        has_more = False
        next_after: str | None = None

        while len(items) < effective_limit:
            remaining = effective_limit - len(items)
            current_first = min(page_size, remaining)
            page_items = spec.page_fetcher(
                client,
                after=after,
                first=current_first,
                sort=sort,
                filter=filter,
                group_id=group_id,
                created_at_from=created_at_from,
                created_at_to=created_at_to,
                type=type,
                subtype=subtype,
                activity=activity,
            )
            pages_fetched += 1
            items.extend(spec.serializer(item) for item in page_items)

            last_page_info = _copy_metadata(getattr(manager, "last_page_info", None))
            last_cursors = _copy_metadata(getattr(manager, "last_cursors", None))
            has_more, next_after = _extract_next_after(last_page_info, last_cursors)

            if len(items) >= effective_limit:
                break
            if not page_items or not has_more:
                next_after = None if not has_more else next_after
                break
            if not next_after:
                raise ValueError(
                    f"{normalized_resource} reported more results but did not provide a usable next cursor."
                )
            if next_after in seen_cursors:
                raise ValueError(
                    f"{normalized_resource} returned a repeated pagination cursor; stopping to avoid an infinite loop."
                )
            seen_cursors.add(next_after)
            after = next_after

        has_more = bool(has_more and len(items) >= effective_limit)
        if not has_more:
            next_after = None

        return {
            "resource": normalized_resource,
            "items": items[:effective_limit],
            "count": min(len(items), effective_limit),
            "pages_fetched": pages_fetched,
            "page_size": page_size,
            "limit": effective_limit,
            "has_more": has_more,
            "next_after": next_after,
            "page_info": last_page_info,
            "cursors": last_cursors,
        }
    except Exception as exc:
        return serialize_tool_error(exc)


def _normalize_resource(resource: str) -> str:
    normalized = resource.strip().lower()
    if not normalized:
        raise ValueError("resource is required")
    return normalized


def _get_resource_spec(resource: str) -> ListAllResourceSpec:
    try:
        return LIST_ALL_RESOURCES[resource]
    except KeyError as exc:
        supported_resources = ", ".join(sorted(LIST_ALL_RESOURCES))
        raise ValueError(
            f"Unsupported resource '{resource}'. Supported resources: {supported_resources}."
        ) from exc


def _validate_page_size(first: int) -> int:
    if first < 1 or first > MAX_PAGE_SIZE:
        raise ValueError(f"first must be between 1 and {MAX_PAGE_SIZE}")
    return first


def _validate_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    if limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
    return limit


def _validate_resource_requirements(
    resource: str,
    *,
    group_id: str | None,
    created_at_from: str | None,
    created_at_to: str | None,
) -> None:
    if resource == "address_group_objects" and not group_id:
        raise ValueError("group_id is required for resource 'address_group_objects'")
    if resource == "audit_events":
        if not created_at_from:
            raise ValueError("created_at_from is required for resource 'audit_events'")
        if not created_at_to:
            raise ValueError("created_at_to is required for resource 'audit_events'")


def _copy_metadata(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return dict(value)
    return None


def _extract_next_after(
    page_info: dict[str, Any] | None,
    cursors: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    if isinstance(page_info, dict):
        has_next = bool(page_info.get("has_next"))
        end_cursor = page_info.get("end_cursor")
        if isinstance(end_cursor, str) and end_cursor:
            return has_next, end_cursor if has_next else None
        if not has_next:
            return False, None

    if isinstance(cursors, dict):
        for key in ("after", "next_after", "nextAfter", "next", "end_cursor", "endCursor"):
            value = cursors.get(key)
            if isinstance(value, str) and value:
                return True, value

    return False, None


def _list_manager_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_address_group_objects_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_address_objects(
        kwargs["group_id"],
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_application_categories_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_categories(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_applications_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_custom_apps(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_qosmos_apps_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_qosmos_apps(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_webroot_categories_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_webroot_categories(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_software_downloads_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_downloads(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_software_versions_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list_versions(
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _list_audit_events_page(manager: Any, **kwargs: Any) -> list[Any]:
    return manager.list(
        created_at_from=kwargs["created_at_from"],
        created_at_to=kwargs["created_at_to"],
        type=kwargs.get("type"),
        subtype=kwargs.get("subtype"),
        activity=kwargs.get("activity"),
        after=kwargs.get("after"),
        first=kwargs.get("first"),
        sort=kwargs.get("sort"),
        filter=kwargs.get("filter"),
    )


def _manager_attr(name: str) -> Callable[[Any], Any]:
    return lambda client: getattr(client, name)


LIST_ALL_RESOURCES: dict[str, ListAllResourceSpec] = {
    "address_group_objects": ListAllResourceSpec(
        manager_getter=_manager_attr("address_groups"),
        page_fetcher=lambda client, **kwargs: _list_address_group_objects_page(
            client.address_groups,
            **kwargs,
        ),
        serializer=serialize_address_group,
        required_fields=("group_id",),
    ),
    "address_groups": ListAllResourceSpec(
        manager_getter=_manager_attr("address_groups"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.address_groups, **kwargs),
        serializer=serialize_address_group,
    ),
    "application_categories": ListAllResourceSpec(
        manager_getter=_manager_attr("applications"),
        page_fetcher=lambda client, **kwargs: _list_application_categories_page(
            client.applications,
            **kwargs,
        ),
        serializer=serialize_application,
    ),
    "applications": ListAllResourceSpec(
        manager_getter=_manager_attr("applications"),
        page_fetcher=lambda client, **kwargs: _list_applications_page(
            client.applications,
            **kwargs,
        ),
        serializer=serialize_application,
    ),
    "audit_events": ListAllResourceSpec(
        manager_getter=_manager_attr("audit_events"),
        page_fetcher=lambda client, **kwargs: _list_audit_events_page(
            client.audit_events,
            **kwargs,
        ),
        serializer=serialize_audit_event,
        required_fields=("created_at_from", "created_at_to"),
    ),
    "ca_certificates": ListAllResourceSpec(
        manager_getter=_manager_attr("ca_certificates"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.ca_certificates, **kwargs),
        serializer=serialize_ca_certificate,
    ),
    "client_templates": ListAllResourceSpec(
        manager_getter=_manager_attr("client_templates"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.client_templates, **kwargs),
        serializer=serialize_client_template,
    ),
    "clients": ListAllResourceSpec(
        manager_getter=_manager_attr("clients"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.clients, **kwargs),
        serializer=serialize_client,
    ),
    "cloud_accounts": ListAllResourceSpec(
        manager_getter=_manager_attr("cloud_accounts"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.cloud_accounts, **kwargs),
        serializer=serialize_cloud_account,
    ),
    "controller_operators": ListAllResourceSpec(
        manager_getter=_manager_attr("controller_operators"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(
            client.controller_operators,
            **kwargs,
        ),
        serializer=serialize_controller_operator,
    ),
    "controllers": ListAllResourceSpec(
        manager_getter=_manager_attr("controllers"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.controllers, **kwargs),
        serializer=serialize_controller,
    ),
    "device_groups": ListAllResourceSpec(
        manager_getter=_manager_attr("device_groups"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.device_groups, **kwargs),
        serializer=serialize_device_group,
    ),
    "gateway_groups": ListAllResourceSpec(
        manager_getter=_manager_attr("gateway_groups"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.gateway_groups, **kwargs),
        serializer=serialize_gateway_group,
    ),
    "gateway_templates": ListAllResourceSpec(
        manager_getter=_manager_attr("gateway_templates"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(
            client.gateway_templates,
            **kwargs,
        ),
        serializer=serialize_gateway_template,
    ),
    "gateways": ListAllResourceSpec(
        manager_getter=_manager_attr("gateways"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.gateways, **kwargs),
        serializer=serialize_gateway,
    ),
    "inventory_devices": ListAllResourceSpec(
        manager_getter=_manager_attr("inventory_devices"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(
            client.inventory_devices,
            **kwargs,
        ),
        serializer=serialize_inventory_device,
    ),
    "ntp_configs": ListAllResourceSpec(
        manager_getter=_manager_attr("ntp_configs"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.ntp_configs, **kwargs),
        serializer=serialize_ntp_config,
    ),
    "overlay_tags": ListAllResourceSpec(
        manager_getter=_manager_attr("overlay_tags"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.overlay_tags, **kwargs),
        serializer=serialize_overlay_tag,
    ),
    "policies": ListAllResourceSpec(
        manager_getter=_manager_attr("policies"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.policies, **kwargs),
        serializer=serialize_policy,
    ),
    "qosmos_apps": ListAllResourceSpec(
        manager_getter=_manager_attr("applications"),
        page_fetcher=lambda client, **kwargs: _list_qosmos_apps_page(
            client.applications,
            **kwargs,
        ),
        serializer=serialize_application,
    ),
    "radius_servers": ListAllResourceSpec(
        manager_getter=_manager_attr("radius_servers"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.radius_servers, **kwargs),
        serializer=serialize_radius_server,
    ),
    "segments": ListAllResourceSpec(
        manager_getter=_manager_attr("segments"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.segments, **kwargs),
        serializer=serialize_segment,
    ),
    "site_commands": ListAllResourceSpec(
        manager_getter=_manager_attr("site_commands"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.site_commands, **kwargs),
        serializer=serialize_site_command,
    ),
    "software_downloads": ListAllResourceSpec(
        manager_getter=_manager_attr("software"),
        page_fetcher=lambda client, **kwargs: _list_software_downloads_page(
            client.software,
            **kwargs,
        ),
        serializer=serialize_software_item,
    ),
    "software_versions": ListAllResourceSpec(
        manager_getter=_manager_attr("software"),
        page_fetcher=lambda client, **kwargs: _list_software_versions_page(
            client.software,
            **kwargs,
        ),
        serializer=serialize_software_item,
    ),
    "tenants": ListAllResourceSpec(
        manager_getter=_manager_attr("tenants"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.tenants, **kwargs),
        serializer=serialize_tenant,
    ),
    "user_groups": ListAllResourceSpec(
        manager_getter=_manager_attr("user_groups"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.user_groups, **kwargs),
        serializer=serialize_user_group,
    ),
    "users": ListAllResourceSpec(
        manager_getter=_manager_attr("users"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.users, **kwargs),
        serializer=serialize_user,
    ),
    "vpn_peers": ListAllResourceSpec(
        manager_getter=_manager_attr("vpn_peers"),
        page_fetcher=lambda client, **kwargs: _list_manager_page(client.vpn_peers, **kwargs),
        serializer=serialize_vpn_peer,
    ),
    "webroot_categories": ListAllResourceSpec(
        manager_getter=_manager_attr("applications"),
        page_fetcher=lambda client, **kwargs: _list_webroot_categories_page(
            client.applications,
            **kwargs,
        ),
        serializer=serialize_application,
    ),
}
