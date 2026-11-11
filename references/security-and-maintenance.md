# Security, performance, and maintenance

Read for firewall/admin access, SQM/QoS, packages, logs, firmware, and service maintenance.

## Firewall and administration

The [Firewall](https://docs.gl-inet.com/router/en/4/interface_guide/firewall/) page is for v4.5 and earlier. Later builds distribute controls across [Port Forwarding](https://docs.gl-inet.com/router/en/4/interface_guide/port_forwarding/), [Admin Access](https://docs.gl-inet.com/router/en/4/interface_guide/admin_access/), [Security](https://docs.gl-inet.com/router/en/4/interface_guide/security/), [ACL](https://docs.gl-inet.com/router/en/4/interface_guide/acl/), [NAT Settings](https://docs.gl-inet.com/router/en/4/interface_guide/nat_settings/), and their linked version guidance.

Discover fw3/iptables versus fw4/nftables and the installed GL.iNet rule generators. Do not apply a backend-specific snippet simply because the underlying OpenWrt version sounds familiar. Avoid broad flushes and direct edits of generated rules. Inspect the intended source/destination, family, protocol, zone, service, and rule order before modifying the owning persistent configuration.

Distinguish router INPUT, client forwarding, port forwarding/DNAT, outbound policy, and UPnP-created mappings. A firewall opening to the router is not a forward to a LAN host. New WAN SSH, remote web access, DMZ, or broad forwarding needs a clearly specified exposure scope. Prefer the existing private management path. Preserve IPv6 policy independently of IPv4 NAT.

For management ports or SSH settings, follow recovery first, retain the old session, and test a new session before considering the change successful. Do not rotate the admin password, SSH keys, or certificate trust merely to run this skill.

The [Security Scan](https://docs.gl-inet.com/router/en/4/interface_guide/security_scan/) page can run a scan when opened. Reading or scoring a setting does not authorize automatically applying every suggested optimization. Use the requested scope and preserve deliberate exceptions.

## SQM, QoS, acceleration, and measurement

Read [SQM](https://docs.gl-inet.com/router/en/4/interface_guide/sqm/), [QoS](https://docs.gl-inet.com/router/en/4/interface_guide/qos/), and [Network Acceleration](https://docs.gl-inet.com/router/en/4/interface_guide/network_acceleration/). [Hardware Acceleration](https://docs.gl-inet.com/router/en/4/interface_guide/hardware_acceleration/) is the older v4.2-and-earlier guide.

The current SQM guide states that SQM and QoS cannot run simultaneously, SQM does not work with Network Acceleration, and enabling SQM disables acceleration. SQM also has operating-mode and traffic-direction limits. Do not promise both acceleration and CAKE shaping or assume VPN-server inbound traffic is shaped identically to client gateway traffic.

Clarify whether the goal is maximum throughput or low latency under contention. Measure the actual WAN path and CPU constraint; a plan's advertised gigabit speed is not verified sustainable shaping capacity. Configure actual rates with the correct UI/implementation units: current UI fields are Mbps, while an underlying package can use different units. Verify mapping before translating values. Avoid a universal percentage or guaranteed throughput claim.

Firmware v4.11 adds features such as Cake Autorate. Its background probes consume traffic and need suitable probe endpoints. On a metered connection, bandwidth-heavy speed tests, indefinite probes, and continuous monitoring require an agreed test/data budget. Prefer existing measurements when they are sufficient.

Verify effective qdisc ownership, counters on the actual WAN path, acceleration state, idle/loaded latency, throughput, and CPU load within that budget. Enabling a UI switch is not proof of latency improvement. Do not install a second SQM implementation over a working GL-managed feature without a separately authorized migration.

## Firmware and packages

Use [Upgrade](https://docs.gl-inet.com/router/en/4/interface_guide/upgrade/) and the [official model download center](https://dl.gl-inet.com/router/mt6000). Read-only version checks are ordinary inspection. Flashing, downgrading, resetting, changing feeds, replacing the SDK/build, or installing packages require the corresponding task authorization.

Verify exact model/variant, image type, current and target versions, build channel, supported upgrade path, vendor-provided integrity information, settings compatibility, power stability, and recovery. A file timestamp is not its release date. Do not substitute an unofficial image or interpret a download page as permission to flash it.

The vendor guide says not to retain settings on downgrades and notes that user-installed packages may need reinstallation after an upgrade. Plan for that behavior. Backups do not prove cross-build compatibility. Do not use an indiscriminate `opkg upgrade` or upstream feed as a maintenance shortcut.

## Logs and routine system tasks

Use [Log](https://docs.gl-inet.com/router/en/4/interface_guide/log/), [Scheduled Tasks](https://docs.gl-inet.com/router/en/4/interface_guide/scheduled_tasks/), [Time Zone](https://docs.gl-inet.com/router/en/4/interface_guide/time_zone/), and other relevant catalog entries. Bound log time windows/lines and redact before sharing. Logs may contain URLs, tokens, public IPs, MACs and client names. Do not create support uploads or send logs to a vendor as a side effect of diagnosis.

For schedules, establish timezone, intended local time, affected service and persistence across reboots. Do not add startup hooks, cron jobs, or background daemons unless the requested behavior requires them and their ownership is clear. Use the narrow supported service reload and verify it; a full reboot is a distinct disruption.
