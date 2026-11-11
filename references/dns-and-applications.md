# DNS and applications

Read for DNS, AdGuard Home, overlay networks, storage, plugins, and other applications.

## Trace the DNS path

Use [DNS through v4.10](https://docs.gl-inet.com/router/en/4/interface_guide/dns/) or [DNS v4.11+](https://docs.gl-inet.com/router/en/4/interface_guide/dns_v4.11/). The newer interface separates WAN, VPN, and manual DNS behavior. Preserve the user's intended resolver and privacy choice.

Trace the affected client's advertised resolver, plain DNS interception if enabled, local dnsmasq/listener configuration, AdGuard or encrypted resolver, the selection between VPN-provided and custom DNS, and the router's own queries. Identify what process owns port 53 and whether another local resolver uses a different port. Do not assume AdGuard replaces every path or that a daemon's config file is the authoritative source under GL.iNet's service manager.

Check bootstrap resolution and time when encrypted DNS cannot connect. Detect loops between dnsmasq, AdGuard, VPN DNS, and local forwarding. Keep local-zone resolution and split DNS intact. DNS rebinding protection may affect legitimate private-address answers; establish the specific domain/need instead of globally disabling protection as a routine fix.

Overriding ordinary client DNS does not automatically redirect arbitrary DoH/DoT traffic from applications. Describe the actual coverage rather than promising complete enforcement. User-requested policy changes may require separate firewall or application controls.

Verify a fresh query with cache behavior understood, both A and AAAA paths, expected local names, AdGuard filtering when requested, upstream choice, and relevant VPN outage behavior. Avoid uploading query logs or browsing histories to public services.

## AdGuard Home

Read [AdGuard Home](https://docs.gl-inet.com/router/en/4/interface_guide/adguardhome/) and any linked integration tutorial relevant to the task. Confirm it is installed/supported on this build and how GL.iNet enables, configures, and launches it.

Preserve allowlists, blocklists, upstream choices, clients, and query-log retention. DNS query history and client information are private. Back up the needed configuration securely before changing service ownership or ports. Do not dump its complete YAML into chat. Update the GL-managed configuration path where established; a direct daemon edit may not survive the vendor service's next apply.

## Tailscale and ZeroTier

Read [Tailscale](https://docs.gl-inet.com/router/en/4/interface_guide/tailscale/) or [ZeroTier](https://docs.gl-inet.com/router/en/4/interface_guide/zerotier/). Identify GL.iNet's wrapper, installed version, existing membership, and actual routes before running daemon commands.

Joining a network, advertising subnets, accepting routes/DNS, or enabling an exit node changes access and routing. Use the user's selected account/network and explicit scope; do not create accounts or broaden trust to work around an issue. Auth keys, login URLs with tokens, and private network identifiers stay out of source and public output. Prefer the supported service route over a generic command that resets unrelated daemon options.

Check overlap with LAN and VPN routes, DNS ownership, and coexistence constraints from the matching guide. Verify from an authorized peer, including access denied outside the permitted subnet. If the overlay carries this session's management connection, apply the recovery workflow before changing it.

## Other applications and shared-interface features

Use the catalog for model-specific guides rather than treating menu presence in a shared manual as support:

| Feature | Decision that needs verification |
| --- | --- |
| GoodCloud / GL.iNet Account / GoodPAS / AstroWarp | Account identity, binding scope, subscriptions, and remote-access side effects. The GoodCloud guide notes changed defaults for remote terminal/web access in v4.10; read them before binding. |
| Plug-ins | Exact package, firmware-specific feed, architecture, storage, dependencies, and requested purpose. Never run a blanket package upgrade or mix upstream feeds into stock firmware. |
| Network Storage | Attached storage, filesystem support, intended LAN users/shares, credentials and read/write access. Never expose a share to WAN as an implicit fix. |
| DDNS | Provider, public reachability and intended hostname. DDNS alone does not enable inbound reachability. |
| Tor | Model/build support, affected traffic and coexistence limitations. Do not promise anonymity solely because a toggle is enabled. |
| Parental control, Bark, Content Filter | Firmware/DPI dependencies, intended clients/schedules and subscription or data-processing choices. Preserve existing policies. |
| Mesh | Exact supported topology, roles, firmware and hardware. Preserve the uplink and test client roaming; generic Wi-Fi compatibility does not prove mesh support. |
| Cellular/eSIM, touchscreen, USB/power, toggle buttons | Require the actual relevant hardware. The shared manual includes features intended for other router models. |

External account binding, purchases/subscriptions, new telemetry/cloud features, storage formatting, and service installation are separate decisions when not already in the user's request. Continue useful local inspection while a consequential choice remains unresolved.
