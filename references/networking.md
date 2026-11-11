# Networking

Read for LAN/WAN, Wi-Fi, DHCP, segmentation, port roles, Multi-WAN, and IPv6. Start with [Internet](https://docs.gl-inet.com/router/en/4/interface_guide/internet/), [LAN](https://docs.gl-inet.com/router/en/4/interface_guide/lan/), and the matching catalog entry.

## LAN and DHCP

Before renumbering, map the current LAN address, prefix, DHCP pool, reservations, upstream subnet, VPN routes, static routes, and the agent's own path. Check overlap across all of them. Confirm whether clients need a new lease or static configuration and how management will reconnect. A successful `uci commit` does not change an existing client lease.

The guide has separate [LAN instructions for v4.11+](https://docs.gl-inet.com/router/en/4/interface_guide/lan_4.11/). [Subnet](https://docs.gl-inet.com/router/en/4/interface_guide/subnet/) has model/rollout restrictions. An instruction in that page does not prove the installed Flint 2 exposes it.

For a reservation, identify the active DHCP server, target client's actual MAC (including per-network randomization), subnet, and an available address. Preserve existing reservations and leases. Choose a stable named section only after checking that name and MAC/address conflicts. Validate how this firmware handles reserved addresses relative to its dynamic pool.

### Example: an evidence-backed DHCP reservation

This is a mutation pattern, not a universal runnable recipe. Values below describe a synthetic `192.0.2.0/24` lab network. Use it only after confirming dnsmasq owns DHCP, these UCI options are read by the installed service, the section is new, the address is valid/free, the package has no pre-existing staged edits, and a package backup/recovery path exists.

```sh
# Review pending changes first. If there are unrelated changes, stop and preserve them.
uci changes dhcp
# Confirm this named section is absent; an existing section must be updated deliberately.
uci -q get dhcp.work_laptop
```

After the prerequisites are satisfied and the requested reservation is authorized:

```sh
uci set dhcp.work_laptop=host
uci set dhcp.work_laptop.name='work-laptop'
uci set dhcp.work_laptop.mac='02:00:00:00:00:10'
uci set dhcp.work_laptop.ip='192.0.2.50'
uci changes dhcp
```

Review that diff before committing. Then use the installed service's supported reload:

```sh
uci commit dhcp
/etc/init.d/dnsmasq reload
```

Verify the persistent MAC/address pair, service health, and a renewed client lease. Do not restart the whole network for a single reservation. If the owning service, mapping, or reload behavior is unverified, use [Clients](https://docs.gl-inet.com/router/en/4/interface_guide/clients/) or the matching LAN UI workflow. The saved pre-change package enables recovery; `uci revert` cannot undo an already committed change.

## Wi-Fi

Use [Wireless](https://docs.gl-inet.com/router/en/4/interface_guide/wireless/) for v4.9+ and its linked [v4.8-and-earlier guide](https://docs.gl-inet.com/router/en/4/interface_guide/wireless_v4.8/) where applicable. Map actual radios, interfaces, bridge membership, encryption support, and the current management SSID before changing them.

Choose country/regulatory settings for the device's actual location and supported firmware. Do not bypass regulatory limits or present increased transmit power as an automatic coverage improvement. Channel width, interference, placement, client capability, and DFS behavior can matter more than nominal power. Preserve credentials privately. A Wi-Fi change made through that same radio needs the recovery workflow first.

Verify reconnection using the intended band/security mode, client addressing, local isolation if requested, and Internet access. Changing the displayed SSID is not enough to prove radio or roaming performance.

## Ports, VLANs, and guest/IoT isolation

Read [Ethernet Port](https://docs.gl-inet.com/router/en/4/interface_guide/ethernet_port/) or its [v4.10+ variant](https://docs.gl-inet.com/router/en/4/interface_guide/ethernet_port_v4.10/), plus [Guest Network](https://docs.gl-inet.com/router/en/4/interface_guide/guest_network/) and [IoT Network](https://docs.gl-inet.com/router/en/4/interface_guide/iot_network/). Map each physical port to its observed kernel/switch/bridge membership. Never infer the switch layout from `mediatek/filogic` or a chassis label alone. A link-observation test must not unplug the active management path.

Specify the desired trust boundary before creating a VLAN: member ports/SSIDs, tagged versus untagged uplinks, PVIDs, DHCP/DNS, router administration, access to main LAN, and permitted WAN. Inspect the actual firewall engine and existing GL-managed zones. Preserve unrelated VLAN memberships and uplink reachability.

AP isolation is not complete guest/IoT isolation: it may cover only Wi-Fi peer traffic. Enforce and test the actual routed and bridged paths, including wired members and IPv6. Verify denied access to both LAN devices and router management while permitted DHCP, DNS, and Internet traffic still work. Do not flush rules to resolve a conflict.

## WAN, Multi-WAN, and operating modes

Use [Ethernet Internet](https://docs.gl-inet.com/router/en/4/interface_guide/internet_ethernet/), [Multi-WAN](https://docs.gl-inet.com/router/en/4/interface_guide/multi-wan/), and [Network Mode](https://docs.gl-inet.com/router/en/4/interface_guide/network_mode/). Distinguish failover, load balancing, and actual link bonding; do not promise one connection can aggregate ordinary WAN links. Consider health checks, route metrics, policy rules, DNS, VPN, and metered links.

Router/AP/bridge mode changes can relocate the management address and change which DHCP/NAT/firewall features apply. Prepare a way to locate the new address through the selected upstream network. Repeater/tethering/cellular capabilities depend on hardware, attached devices, and firmware; modem-specific functions in the shared manual do not imply a built-in modem on Flint 2.

Use the [IPv6 guide](https://docs.gl-inet.com/router/en/4/interface_guide/ipv6/) and inspect delegation, RA/DHCPv6, routes, and firewall policy together. An IPv4 policy must not silently leave an IPv6 bypass. Disable IPv6 only when that behavior is requested or explicitly accepted as part of the chosen solution.

Failover testing interrupts a real path: establish its scope first. Verify the intended WAN and recovery behavior from actual clients and account for existing sessions that remain pinned to an old path.
