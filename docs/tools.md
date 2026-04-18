# MCP Tools Reference

This document lists all MCP tools currently exposed by the Netskope SD-WAN MCP server. The source of truth is the MCP server registration in `src/netskope_sdwan_mcp/server.py` and the corresponding tool wrapper modules in `src/netskope_sdwan_mcp/tools/`.

---

## Summary

- Total tools: 79
- Categories: 29

---

## Categories

- [Gateways](#gateways)
- [Gateway Groups](#gateway-groups)
- [Gateway Templates](#gateway-templates)
- [Policies](#policies)
- [Segments](#segments)
- [Applications](#applications)
- [Address Groups](#address-groups)
- [Device Groups](#device-groups)
- [Clients](#clients)
- [Client Templates](#client-templates)
- [Controllers](#controllers)
- [Controller Operators](#controller-operators)
- [Inventory](#inventory)
- [Certificates](#certificates)
- [Cloud Accounts](#cloud-accounts)
- [NTP Configurations](#ntp-configurations)
- [Overlay Tags](#overlay-tags)
- [Radius Servers](#radius-servers)
- [VPN Peers](#vpn-peers)
- [Site Commands](#site-commands)
- [Software](#software)
- [Tenants](#tenants)
- [Users](#users)
- [User Groups](#user-groups)
- [JWKS](#jwks)
- [Audit Events](#audit-events)
- [Monitoring (v1 legacy)](#monitoring-v1-legacy)
- [Edges (v1 legacy)](#edges-v1-legacy)
- [Generic Resource Pagination](#generic-resource-pagination)

---

## Gateways

#### `list_gateways`

- **Description:** List gateways in the tenant.
- **SDK Mapping:** `client.gateways.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of gateway objects.
- **Notes:** Standard paginated list wrapper.

#### `list_gateways_with_status`

- **Description:** List gateways with a compact operational status summary.
- **SDK Mapping:** `client.gateways.list` plus `client.gateways.get_telemetry_overview` for each gateway
- **Parameters:** None.
- **Returns:** List of summarized gateway status objects.
- **Notes:** Composite helper that enriches each gateway with telemetry status fields.

#### `get_gateway`

- **Description:** Get one gateway by ID.
- **SDK Mapping:** `client.gateways.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Gateway object.

#### `get_gateway_telemetry_overview`

- **Description:** Get the telemetry overview for one gateway.
- **SDK Mapping:** `client.gateways.get_telemetry_overview`
- **Parameters:**
  - `gateway_id` (`str`, required)
- **Returns:** Gateway telemetry overview object.

#### `get_gateway_status`

- **Description:** Get a compact composite status view for one gateway.
- **SDK Mapping:** `client.gateways.get` plus `client.gateways.get_telemetry_overview`
- **Parameters:**
  - `gateway_id` (`str`, required)
- **Returns:** Gateway status summary object.
- **Notes:** Combines gateway metadata with telemetry status fields.

#### `get_gateway_operational_snapshot`

- **Description:** Get gateway details together with latest interface, path, and route snapshots.
- **SDK Mapping:** `client.gateways.get`, `client.v1.monitoring.get_interfaces_latest`, `client.v1.monitoring.get_paths_latest`, `client.v1.monitoring.get_routes_latest`
- **Parameters:**
  - `id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
- **Returns:** Composite object containing gateway details and latest monitoring snapshots.
- **Notes:** Uses v1 monitoring endpoints under the hood.

## Gateway Groups

#### `list_gateway_groups`

- **Description:** List gateway groups in the tenant.
- **SDK Mapping:** `client.gateway_groups.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of gateway group objects.
- **Notes:** Standard paginated list wrapper.

#### `get_gateway_group`

- **Description:** Get one gateway group by ID.
- **SDK Mapping:** `client.gateway_groups.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Gateway group object.

## Gateway Templates

#### `list_gateway_templates`

- **Description:** List gateway templates in the tenant.
- **SDK Mapping:** `client.gateway_templates.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of gateway template objects.
- **Notes:** Standard paginated list wrapper.

#### `get_gateway_template`

- **Description:** Get one gateway template by ID.
- **SDK Mapping:** `client.gateway_templates.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Gateway template object.

## Policies

#### `list_policies`

- **Description:** List policies in the tenant.
- **SDK Mapping:** `client.policies.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of policy objects.
- **Notes:** Standard paginated list wrapper.

#### `get_policy`

- **Description:** Get one policy by ID.
- **SDK Mapping:** `client.policies.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Policy object.

## Segments

#### `list_segments`

- **Description:** List segments in the tenant.
- **SDK Mapping:** `client.segments.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of segment objects.
- **Notes:** Standard paginated list wrapper.

#### `get_segment`

- **Description:** Get one segment by ID.
- **SDK Mapping:** `client.segments.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Segment object.

## Applications

#### `list_applications`

- **Description:** List custom applications.
- **SDK Mapping:** `client.applications.list_custom_apps`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of application objects.
- **Notes:** Standard paginated list wrapper.

#### `list_application_categories`

- **Description:** List application categories.
- **SDK Mapping:** `client.applications.list_categories`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of application category objects.
- **Notes:** Standard paginated list wrapper.

#### `list_qosmos_apps`

- **Description:** List Qosmos application definitions.
- **SDK Mapping:** `client.applications.list_qosmos_apps`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of Qosmos application objects.
- **Notes:** Standard paginated list wrapper.

#### `list_webroot_categories`

- **Description:** List Webroot URL categories.
- **SDK Mapping:** `client.applications.list_webroot_categories`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of Webroot category objects.
- **Notes:** Standard paginated list wrapper.

#### `get_application`

- **Description:** Get one custom application by ID.
- **SDK Mapping:** `client.applications.get_custom_app`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Application object.

## Address Groups

#### `list_address_groups`

- **Description:** List address groups in the tenant.
- **SDK Mapping:** `client.address_groups.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of address group objects.
- **Notes:** Standard paginated list wrapper.

#### `get_address_group`

- **Description:** Get one address group by ID.
- **SDK Mapping:** `client.address_groups.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Address group object.

#### `list_address_group_objects`

- **Description:** List address objects for one address group.
- **SDK Mapping:** `client.address_groups.list_address_objects`
- **Parameters:**
  - `group_id` (`str`, required)
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of address object entries for the target group.
- **Notes:** Standard paginated list wrapper scoped to one group.

## Device Groups

#### `list_device_groups`

- **Description:** List device groups in the tenant.
- **SDK Mapping:** `client.device_groups.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of device group objects.
- **Notes:** Standard paginated list wrapper.

#### `get_device_group`

- **Description:** Get one device group by ID.
- **SDK Mapping:** `client.device_groups.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Device group object.

## Clients

#### `list_clients`

- **Description:** List clients in the tenant.
- **SDK Mapping:** `client.clients.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of client objects.
- **Notes:** Standard paginated list wrapper.

#### `get_client`

- **Description:** Get one client by ID.
- **SDK Mapping:** `client.clients.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Client object.

## Client Templates

#### `list_client_templates`

- **Description:** List client templates in the tenant.
- **SDK Mapping:** `client.client_templates.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of client template objects.
- **Notes:** Standard paginated list wrapper.

#### `get_client_template`

- **Description:** Get one client template by ID.
- **SDK Mapping:** `client.client_templates.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Client template object.

## Controllers

#### `list_controllers`

- **Description:** List controllers in the tenant.
- **SDK Mapping:** `client.controllers.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of controller objects.
- **Notes:** Standard paginated list wrapper.

#### `get_controller`

- **Description:** Get one controller by ID.
- **SDK Mapping:** `client.controllers.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Controller object.

#### `get_controller_operator_status`

- **Description:** Get operator status for one controller.
- **SDK Mapping:** `client.controllers.get_operator_status`
- **Parameters:**
  - `controller_id` (`str`, required)
- **Returns:** Controller operator status object.

## Controller Operators

#### `list_controller_operators`

- **Description:** List controller operators in the tenant.
- **SDK Mapping:** `client.controller_operators.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of controller operator objects.
- **Notes:** Standard paginated list wrapper.

#### `get_controller_operator`

- **Description:** Get one controller operator by ID.
- **SDK Mapping:** `client.controller_operators.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Controller operator object.

## Inventory

#### `list_inventory_devices`

- **Description:** List inventory devices in the tenant.
- **SDK Mapping:** `client.inventory_devices.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of inventory device objects.
- **Notes:** Standard paginated list wrapper.

## Certificates

#### `list_ca_certificates`

- **Description:** List CA certificates in the tenant.
- **SDK Mapping:** `client.ca_certificates.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of CA certificate objects.
- **Notes:** Standard paginated list wrapper.

#### `get_ca_certificate`

- **Description:** Get one CA certificate by ID.
- **SDK Mapping:** `client.ca_certificates.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** CA certificate object.

## Cloud Accounts

#### `list_cloud_accounts`

- **Description:** List cloud accounts in the tenant.
- **SDK Mapping:** `client.cloud_accounts.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of cloud account objects.
- **Notes:** Standard paginated list wrapper.

#### `get_cloud_account`

- **Description:** Get one cloud account by ID.
- **SDK Mapping:** `client.cloud_accounts.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Cloud account object.

## NTP Configurations

#### `list_ntp_configs`

- **Description:** List NTP configurations in the tenant.
- **SDK Mapping:** `client.ntp_configs.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of NTP configuration objects.
- **Notes:** Standard paginated list wrapper.

#### `get_ntp_config`

- **Description:** Get one NTP configuration by ID.
- **SDK Mapping:** `client.ntp_configs.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** NTP configuration object.

## Overlay Tags

#### `list_overlay_tags`

- **Description:** List overlay tags in the tenant.
- **SDK Mapping:** `client.overlay_tags.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of overlay tag objects.
- **Notes:** Standard paginated list wrapper.

#### `get_overlay_tag`

- **Description:** Get one overlay tag by ID.
- **SDK Mapping:** `client.overlay_tags.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Overlay tag object.

## Radius Servers

#### `list_radius_servers`

- **Description:** List RADIUS servers in the tenant.
- **SDK Mapping:** `client.radius_servers.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of RADIUS server objects.
- **Notes:** Standard paginated list wrapper.

#### `get_radius_server`

- **Description:** Get one RADIUS server by ID.
- **SDK Mapping:** `client.radius_servers.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** RADIUS server object.

## VPN Peers

#### `list_vpn_peers`

- **Description:** List VPN peers in the tenant.
- **SDK Mapping:** `client.vpn_peers.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of VPN peer objects.
- **Notes:** Standard paginated list wrapper.

#### `get_vpn_peer`

- **Description:** Get one VPN peer by ID.
- **SDK Mapping:** `client.vpn_peers.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** VPN peer object.

## Site Commands

#### `list_site_commands`

- **Description:** List site commands in the tenant.
- **SDK Mapping:** `client.site_commands.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of site command objects.
- **Notes:** Standard paginated list wrapper.

#### `get_site_command`

- **Description:** Get one site command by ID.
- **SDK Mapping:** `client.site_commands.get`
- **Parameters:**
  - `command_id` (`str`, required)
- **Returns:** Site command object.

#### `get_site_command_output`

- **Description:** Get a downloadable output payload for one site command artifact.
- **SDK Mapping:** `client.site_commands.get_output`
- **Parameters:**
  - `command_id` (`str`, required)
  - `name` (`str`, required)
- **Returns:** Site command output object, including decoded content when available.

## Software

#### `list_software_versions`

- **Description:** List available software versions.
- **SDK Mapping:** `client.software.list_versions`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of software version objects.
- **Notes:** Standard paginated list wrapper.

#### `list_software_downloads`

- **Description:** List software download artifacts.
- **SDK Mapping:** `client.software.list_downloads`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of software download objects.
- **Notes:** Standard paginated list wrapper.

## Tenants

#### `list_tenants`

- **Description:** List tenants available to the caller.
- **SDK Mapping:** `client.tenants.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of tenant objects.
- **Notes:** Standard paginated list wrapper.

#### `get_tenant`

- **Description:** Get one tenant by ID.
- **SDK Mapping:** `client.tenants.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** Tenant object.

## Users

#### `list_users`

- **Description:** List users in the tenant.
- **SDK Mapping:** `client.users.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of user objects.
- **Notes:** Standard paginated list wrapper.

#### `get_user`

- **Description:** Get one user by ID.
- **SDK Mapping:** `client.users.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** User object.

## User Groups

#### `list_user_groups`

- **Description:** List user groups in the tenant.
- **SDK Mapping:** `client.user_groups.list`
- **Parameters:**
  - `filter` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
- **Returns:** List of user group objects.
- **Notes:** Standard paginated list wrapper.

#### `get_user_group`

- **Description:** Get one user group by ID.
- **SDK Mapping:** `client.user_groups.get`
- **Parameters:**
  - `id` (`str`, required)
- **Returns:** User group object.

#### `get_v1_user_groups`

- **Description:** Get v1 group memberships for one user.
- **SDK Mapping:** `client.v1.users.get_groups`
- **Parameters:**
  - `user_id` (`str`, required)
- **Returns:** List of v1 user group objects.
- **Notes:** Legacy v1 endpoint.

## JWKS

#### `get_jwks`

- **Description:** Get the controller JWKS payload.
- **SDK Mapping:** `client.jwks.get`
- **Parameters:** None.
- **Returns:** JWKS object.

## Audit Events

#### `list_audit_events`

- **Description:** List audit events within a required time window.
- **SDK Mapping:** `client.audit_events.list`
- **Parameters:**
  - `created_at_from` (`str`, required)
  - `created_at_to` (`str`, required)
  - `type` (`str`, optional)
  - `subtype` (`str`, optional)
  - `activity` (`str`, optional)
  - `after` (`str`, optional)
  - `first` (`int`, optional)
  - `sort` (`str`, optional)
  - `filter` (`str`, optional)
- **Returns:** List of audit event objects.
- **Notes:** Requires both `created_at_from` and `created_at_to`.

## Monitoring (v1 legacy)

#### `get_interfaces_latest`

- **Description:** Get the latest interface snapshot for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_interfaces_latest`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
- **Returns:** List or object containing latest interface telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_paths_latest`

- **Description:** Get the latest path snapshot for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_paths_latest`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
- **Returns:** List or object containing latest path telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_routes_latest`

- **Description:** Get the latest route snapshot for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_routes_latest`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
- **Returns:** List or object containing latest route telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_device_flows_totals`

- **Description:** Get device flow totals for one gateway and IP over a time range.
- **SDK Mapping:** `client.v1.monitoring.get_device_flows_totals`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `ip` (`str`, required)
  - `start_datetime` (`str`, required)
  - `end_datetime` (`str`, required)
  - `child_tenant_id` (`str`, optional)
- **Returns:** List or object containing device flow totals.
- **Notes:** Legacy v1 monitoring tool.

#### `get_devices_totals`

- **Description:** Get device totals for one gateway over a time range.
- **SDK Mapping:** `client.v1.monitoring.get_devices_totals`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `start_datetime` (`str`, required)
  - `end_datetime` (`str`, required)
  - `child_tenant_id` (`str`, optional)
- **Returns:** List or object containing device totals.
- **Notes:** Legacy v1 monitoring tool.

#### `get_system_load`

- **Description:** Get system load history for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_system_load`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `start_datetime` (`str`, optional)
  - `end_datetime` (`str`, optional)
  - `time_slots` (`int`, optional)
- **Returns:** List or object containing system load telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_system_lte`

- **Description:** Get system LTE history for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_system_lte`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `start_datetime` (`str`, required)
  - `end_datetime` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `time_slots` (`int`, optional)
- **Returns:** List or object containing LTE telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_system_memory`

- **Description:** Get system memory history for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_system_memory`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `start_datetime` (`str`, required)
  - `end_datetime` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `time_slots` (`int`, optional)
- **Returns:** List or object containing memory telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_system_uptime`

- **Description:** Get system uptime history for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_system_uptime`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `start_datetime` (`str`, required)
  - `end_datetime` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `time_slots` (`int`, optional)
- **Returns:** List or object containing uptime telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_system_wifi`

- **Description:** Get system Wi-Fi history for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_system_wifi`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `start_datetime` (`str`, required)
  - `end_datetime` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `time_slots` (`int`, optional)
- **Returns:** List or object containing Wi-Fi telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_paths_links`

- **Description:** Get WAN path or link history for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_paths_links`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `start_datetime` (`str`, optional)
  - `end_datetime` (`str`, optional)
  - `metric` (`str`, optional)
  - `time_slots` (`int`, optional)
- **Returns:** List or object containing path or link telemetry.
- **Notes:** Legacy v1 monitoring tool.

#### `get_paths_links_totals`

- **Description:** Get WAN path or link totals for one gateway.
- **SDK Mapping:** `client.v1.monitoring.get_paths_links_totals`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `child_tenant_id` (`str`, optional)
  - `start_datetime` (`str`, optional)
  - `end_datetime` (`str`, optional)
- **Returns:** List or object containing path or link totals.
- **Notes:** Legacy v1 monitoring tool.

## Edges (v1 legacy)

#### `list_edges`

- **Description:** List v1 edges.
- **SDK Mapping:** `client.v1.edges.list`
- **Parameters:** None.
- **Returns:** List of v1 edge objects.
- **Notes:** Legacy v1 endpoint.

#### `get_edge`

- **Description:** Get one v1 edge by ID.
- **SDK Mapping:** `client.v1.edges.get`
- **Parameters:**
  - `edge_id` (`str`, required)
- **Returns:** V1 edge object.
- **Notes:** Legacy v1 endpoint.

#### `list_edge_interfaces`

- **Description:** List interfaces for one v1 edge.
- **SDK Mapping:** `client.v1.edges.list_interfaces`
- **Parameters:**
  - `edge_id` (`str`, required)
- **Returns:** List or object containing v1 edge interfaces.
- **Notes:** Legacy v1 endpoint.

#### `get_edge_interface`

- **Description:** Get one interface for a v1 edge.
- **SDK Mapping:** `client.v1.edges.get_interface`
- **Parameters:**
  - `edge_id` (`str`, required)
  - `interface_id` (`str`, required)
- **Returns:** V1 edge interface object.
- **Notes:** Legacy v1 endpoint.

#### `list_gateway_interfaces`

- **Description:** List interfaces for one v1 gateway.
- **SDK Mapping:** `client.v1.edges.list_gateway_interfaces`
- **Parameters:**
  - `gateway_id` (`str`, required)
- **Returns:** List or object containing v1 gateway interfaces.
- **Notes:** Legacy v1 endpoint.

#### `get_gateway_interface`

- **Description:** Get one interface for a v1 gateway.
- **SDK Mapping:** `client.v1.edges.get_gateway_interface`
- **Parameters:**
  - `gateway_id` (`str`, required)
  - `interface_id` (`str`, required)
- **Returns:** V1 gateway interface object.
- **Notes:** Legacy v1 endpoint.

## Generic Resource Pagination

#### `list_all`

- **Description:** Auto-paginate through all pages for a supported list resource and return aggregated results.
- **SDK Mapping:** Resource-dependent:
  - `address_group_objects` -> `client.address_groups.list_address_objects`
  - `address_groups` -> `client.address_groups.list`
  - `application_categories` -> `client.applications.list_categories`
  - `applications` -> `client.applications.list_custom_apps`
  - `audit_events` -> `client.audit_events.list`
  - `ca_certificates` -> `client.ca_certificates.list`
  - `client_templates` -> `client.client_templates.list`
  - `clients` -> `client.clients.list`
  - `cloud_accounts` -> `client.cloud_accounts.list`
  - `controller_operators` -> `client.controller_operators.list`
  - `controllers` -> `client.controllers.list`
  - `device_groups` -> `client.device_groups.list`
  - `gateway_groups` -> `client.gateway_groups.list`
  - `gateway_templates` -> `client.gateway_templates.list`
  - `gateways` -> `client.gateways.list`
  - `inventory_devices` -> `client.inventory_devices.list`
  - `ntp_configs` -> `client.ntp_configs.list`
  - `overlay_tags` -> `client.overlay_tags.list`
  - `policies` -> `client.policies.list`
  - `qosmos_apps` -> `client.applications.list_qosmos_apps`
  - `radius_servers` -> `client.radius_servers.list`
  - `segments` -> `client.segments.list`
  - `site_commands` -> `client.site_commands.list`
  - `software_downloads` -> `client.software.list_downloads`
  - `software_versions` -> `client.software.list_versions`
  - `tenants` -> `client.tenants.list`
  - `user_groups` -> `client.user_groups.list`
  - `users` -> `client.users.list`
  - `vpn_peers` -> `client.vpn_peers.list`
  - `webroot_categories` -> `client.applications.list_webroot_categories`
- **Parameters:**
  - `resource` (`str`, required)
  - `filter` (`str`, optional)
  - `first` (`int`, optional, default: `100`)
  - `sort` (`str`, optional)
  - `limit` (`int`, optional)
  - `group_id` (`str`, optional)
  - `created_at_from` (`str`, optional)
  - `created_at_to` (`str`, optional)
  - `type` (`str`, optional)
  - `subtype` (`str`, optional)
  - `activity` (`str`, optional)
- **Returns:** Aggregated response object containing `items`, `count`, `pages_fetched`, pagination metadata, and `next_after` when applicable.
- **Notes:** Supports up to `first=100` per page and `limit=5000` overall. `group_id` is required for `address_group_objects`. `created_at_from` and `created_at_to` are required for `audit_events`.
