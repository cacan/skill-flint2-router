# VPN and policy routing

Read for WireGuard/OpenVPN clients or servers, split routing, DNS paths, and kill switches.

## Select the firmware's policy model

The [VPN Dashboard](https://docs.gl-inet.com/router/en/4/interface_guide/vpn_dashboard/) describes v4.9+ behavior. It links distinct guides for [v4.8](https://docs.gl-inet.com/router/en/4/interface_guide/vpn_dashboard_v4.8/) and [v4.7 and earlier](https://docs.gl-inet.com/router/en/4/interface_guide/vpn_dashboard_v4.7/). Select the exact catalog URL and check its source before reusing an older routing model; a guessed `vpn_dashboard_v4.9/` URL is not evidence.

Choose [WireGuard client](https://docs.gl-inet.com/router/en/4/interface_guide/wireguard_client/), [WireGuard server](https://docs.gl-inet.com/router/en/4/interface_guide/wireguard_server/), [OpenVPN client](https://docs.gl-inet.com/router/en/4/interface_guide/openvpn_client/), or [OpenVPN server](https://docs.gl-inet.com/router/en/4/interface_guide/openvpn_server/) based on the role. Provider-specific activation, profile import, obfuscation, and profile groups have additional requirements; fetch their catalog entries only when relevant.

## Turn the request into a routing contract

Specify source clients/subnets, destinations, tunnel/profile priority, allowed WAN fallback, router-originated traffic, local-network reachability, DNS resolver path, and IPv6 treatment. For a server, also establish whether remote peers need only local access or a full Internet exit. Avoid subnet collisions on both sides. Confirm the client's current identity rather than assuming a randomized MAC is stable.

In the v4.9+ dashboard:

- A tunnel's **Kill Switch** governs traffic assigned to that tunnel when its connection fails. If disabled, fallback is determined by **All Other Traffic**.
- **Enhanced Kill Switch** blocks traffic that matches no VPN tunnel. It does not override every tunnel's own Kill Switch setting.
- For one work laptop that must fail closed while everyone else uses WAN, the intended pattern is that laptop's source policy on the Work tunnel, its tunnel Kill Switch on, and unmatched traffic allowed through WAN. A global block of unmatched traffic contradicts that goal.
- Profile priority within one tunnel group is not failover between independent tunnel groups.

Re-read the current matching guide before applying these semantics. Treat existing broader policies and their order as part of the effective configuration, not something to overwrite.

## Establish the execution mapping

Never derive GL.iNet policy keys from generic upstream `network.wg*` examples. A WireGuard interface by itself does not implement GL.iNet's policy ordering, DNS interception, or kill switches.

Use safe section/type discovery and targeted fields from the existing configuration. For an observed RPC object, inspect its schema and relevant installed handler/source before using methods. Avoid whole `route_policy`, OpenVPN, or WireGuard exports: these can contain sensitive references or embedded values. Read only the options needed and keep any profile/key material out of conversation and Git.

The old developer API website was unavailable during initial research. No private GL.iNet RPC method names are bundled as verified APIs. If the exact SSH mapping cannot be established, complete the configuration through the documented dashboard using an authorized available UI tool, or prepare clear UI steps and explain the missing execution access. Do not mark prepared steps as executed.

Import profiles through the supported mechanism. Do not pass private keys as command arguments, print QR codes into logs, or request complete unredacted profiles. Starting a raw `wg-quick` or `openvpn` process can conflict with vendor-managed state; establish ownership first.

## Verify policy and failure behavior

1. Confirm the tunnel is actually connected: recent WireGuard handshake/traffic or the OpenVPN session state. These checks alone do not prove client routing.
2. From a selected client, verify the intended exit route. From an unaffected client, verify the intended WAN or other tunnel. Check local resources that must remain reachable.
3. Check DNS resolution and its upstream transport from the selected client and the router as required. A DNS answer alone does not establish which route carried the query.
4. Check IPv6 independently. An IPv4 tunnel does not automatically protect IPv6.
5. For a requested fail-closed policy, simulate the tunnel's loss while its policy remains enabled, within an authorized test window. Disabling/deleting the policy is not the same failure. Avoid disrupting the agent's management tunnel. Verify selected traffic is blocked and unaffected clients retain their specified route.
6. Restore normal service, confirm reconnection, and re-read the persisted policy. Do not weaken the kill switch to make an application work.

Server verification requires an external peer and the correct upstream path. Distinguish private WAN, CGNAT, double NAT, and a reachable public address. Opening a port on Flint 2 cannot remove upstream CGNAT. New inbound exposure and upstream router changes require their own clear authorization.
