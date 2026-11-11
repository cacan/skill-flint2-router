# Access and discovery

Read for SSH setup, firmware identification, and deciding which configuration surface owns a setting.

## Establish the route

Use the address, port, and identity selected for this router. `192.168.8.1` is a factory default, not a discovery result. Do not scan the user's network or try default credentials. Ask for the missing address if it is not already recorded. Prefer an existing LAN or private VPN management path; enabling WAN SSH is a separate exposure change.

The [official SSH guide](https://docs.gl-inet.com/router/en/4/tutorials/ssh_log_in_to_the_router/) describes root login using the router's admin password. Use interactive OpenSSH when password authentication is needed; do not place passwords in commands, environment variables, source files, or conversation output. Do not install key-authentication software or alter authentication settings merely to use this helper.

On first connection, establish the host fingerprint through a trusted channel before accepting it. On a mismatch, verify the device and the cause first; never disable host-key checking or clear the whole `known_hosts` file. A reset or upgrade may explain a changed key but does not prove its identity. Preserve any existing SSH route/jump-host configuration explicitly selected by the user.

## Optional inventory helper

Run from the skill directory. The hostname below is an example and must be replaced with the intended router.

```sh
python scripts/inspect_router.py --host router.example --dry-run
python scripts/inspect_router.py --host router.example
```

Use `--port` or `--identity` for an existing selected route. This helper requires an already trusted host key and non-interactive key authentication; a password-only router can be inspected through an ordinary interactive SSH session instead. No password fallback is attempted.

The helper runs one fixed read-only script, reads `ubus call system board` and the first line of `/etc/glversion`, and checks a short command allowlist. It returns model, board name, kernel, GL.iNet version, selected release fields, and available tools. It excludes the hostname, serial, topology, and configuration. Output is a small identification inventory, not proof of compatibility or a complete diagnosis. Firmware layouts without these fields fail closed; investigate interactively rather than overriding identity checks.

## Interpret firmware precisely

- Verify `GL-MT6000` and the board identity together. Record the product variant if the same board identifier is reused; do not infer a newer product's features from that identifier.
- Read the GL.iNet version and OpenWrt release/target separately. A `4.x` interface does not identify the kernel, SDK, firewall engine, or drivers.
- GL.iNet's [firmware status page](https://www.gl-inet.com/pages/firmware-versions) has listed both MTK and op24 variants for this model. Check the installed build directly and current model-specific downloads before consequential decisions. That status page can lag newer releases.
- If the router runs upstream OpenWrt without GL.iNet services, stop using GL-specific recipes. Explain the scope change; do not flash firmware to make it fit this skill.

## Gather only what the task needs

These are read-only discovery candidates after access is authorized. Review the selected output locally before sharing any of it.

```sh
# Identification and available RPC object names; listing does not invoke methods.
ubus call system board
ubus list

# Section types and non-secret link/address fields, rather than a full export.
uci -q show network | sed -n '/=interface$/p; /=device$/p; /\.proto=/p; /\.device=/p; /\.ifname=/p; /\.ports=/p; /\.ipaddr=/p; /\.netmask=/p'

# Wi-Fi section types and bridge association; omit keys, SSIDs, RADIUS and PSKs.
uci -q show wireless | sed -n '/=wifi-iface$/p; /=wifi-device$/p; /\.network=/p; /\.mode=/p'
```

These filtered commands still reveal private network structure. Keep it local unless a sanitized subset is needed. Prefer `uci -q get <verified.package.section.option>` once the section is known. Discover dynamic section names through safe fields; do not assume `radio0`, `wan`, `lan2`, or anonymous section indices mean the same thing on every build.

For a known RPC object, `ubus -v list <observed-object>` can describe its interface. A method name such as `get` does not guarantee no side effects: use documented or source-verified read methods only. GL.iNet JSON-RPC, OpenWrt ubus, and UCI are separate interfaces.

Inspect the relevant installed init/config scripts when needed to establish which files a service reads or regenerates. Do not execute sourced vendor scripts merely to inspect them. Prefer supported GL.iNet ownership of a feature; avoid competing direct daemon invocations that its service manager may undo.

## Stop conditions

Stop the dependent operation when identity is uncertain, the firmware differs from the chosen guide, a service mapping is unknown, or access errors repeat. A missing helper dependency justifies an interactive or documented UI route, not an unrequested installation. Continue useful read-only investigation and report the exact missing evidence.
