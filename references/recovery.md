# Backup, recovery, and access-changing operations

Read before changing the management subnet, bridge/port membership, firewall access, Wi-Fi used for administration, VPN carrying this session, network mode, firmware, or other access-critical state.

## Prepare a concrete recovery path

Record the current route, a private backup location, the proposed diff, the expected interruption, the new address/port/SSID, client reconnection steps, and the exact way to restore the affected state. Keep the current session open where possible, but assume it can disappear.

A usable recovery path is either an independently reachable administration route that the proposed diff leaves intact, or a verified rollback facility that continues after SSH disconnects. Physical operator recovery may be appropriate when the operator is present, has the exact model procedure and client settings ready, and explicitly accepts the interruption. A second terminal using the same affected network is not an independent path.

If the user explicitly declines a separate archival backup, respect that choice and explain which recovery state remains available. Do not create the declined copy anyway. An existing verified recovery artifact or independent route may suffice; missing topology or an unproven recovery mechanism still needs resolution before a disruptive write.

For automated rollback, use only a mechanism available on the installed firmware and test its non-destructive trigger first. Establish that it survives session loss, can restore the required files and owning service, and can be cancelled deliberately after verification. Do not assume LuCI/rpcd rollback exists or works for direct UCI commits. A background `sleep` in the SSH shell is not proof of survival. Avoid installing a scheduler or adding persistent recovery hooks merely to complete a one-off change.

If no adequate path is available, prepare the reviewed change and resolve that specific gap before the disruptive write. Continue independent inspection; do not hide the limitation behind an optimistic command batch.

## Backups are sensitive and firmware-specific

Determine which configuration files and service state the task affects. A narrowly scoped backup may suffice for a small change; an upgrade or migration can require a broader supported backup. Confirm the installed backup utility's actual behavior before using it. When supported, `sysupgrade -b <private-path>` creates a backup rather than flashing firmware; this is not a promise it contains every GL.iNet or application setting.

Use restrictive permissions, a unique timestamped name, and a location outside any Git checkout, web root, public share, or synchronized public directory. Router `/tmp` is volatile: transfer a critical backup securely before a reboot or power-risking operation, and verify its size and archive readability without extracting or printing its secret contents. Avoid shell text redirection of binary backup streams on older Windows PowerShell; use a suitable binary-safe transfer tool. OpenSSH `scp` may default to SFTP, which some builds do not provide; verify support rather than silently installing a server or globally changing SSH settings.

Backups can contain VPN keys, Wi-Fi credentials, admin material, and account data. Do not put them in chat, CI artifacts, issues, or this repository. Do not retain them longer than the user's chosen policy. Cleanup is a separate deliberate file operation, not an implicit deletion of the user's only recovery copy.

## Apply and verify

1. Check existing staged UCI edits and preserve unrelated work. Capture the current values of every changed setting privately.
2. Prepare and verify recovery before replacing the access-critical state. Choose a bounded rollback window long enough for the client to reconnect and run the relevant checks.
3. Stage the minimal change. Inspect the exact diff and use the supported commit/apply path for that service. Avoid bundling password, subnet, Wi-Fi, and firewall changes into one opaque operation.
4. Reconnect through a new session, renew or update client addressing as planned, and verify persistent plus effective state. Test the affected client's outcome and an unaffected control where appropriate.
5. Cancel an armed rollback only after all required checks succeed; verify cancellation. If a timer expires, read back the resulting state before claiming restoration.

`uci revert` discards staged edits; it does not restore values already committed. Restoring an entire package can overwrite concurrent work, so coordinate and restore the narrowest correct state. A reboot can hide transient state without fixing persistent configuration.

## Lost access

First use the established alternate route or rollback. Then check expected address changes, DHCP leases on the selected upstream router, the client's current subnet, link state, the chosen management port, and known firewall/VPN restrictions. Do not guess addresses by broad scanning or delete SSH trust entries to suppress an identity mismatch.

If access cannot be recovered, use the exact model's official [repair/reset guide](https://docs.gl-inet.com/router/en/4/faq/repair_network_or_reset_firmware/) or [bricked-router recovery guide](https://docs.gl-inet.com/router/en/4/faq/debrick/), fetched and checked when needed. Button durations and U-Boot recovery details vary; never improvise from another GL.iNet model. Factory reset and flashing are consequential actions requiring explicit scope and awareness of lost settings. They are not routine responses to a connection timeout.
