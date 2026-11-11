# Security and data handling

## Execution model

This package supplies agent instructions, references, and two optional Python helpers. It does not enforce a sandbox or replace the agent runtime's permission controls. Review the exact revision you install and use your environment's skill admission/security process. Do not blindly update an active copy from a moving branch.

`inspect_router.py` launches the existing local OpenSSH client using a validated destination and a fixed read-only remote script. It requires normal host trust and key authentication, refuses unsupported identification responses, and excludes unrequested fields. It does not read local key contents itself, change router configuration, collect complete UCI exports, install software, or send diagnostics to an external endpoint. The existing SSH client configuration and selected authentication route remain in effect.

`refresh_docs.py` retrieves public HTTPS resources only from `docs.gl-inet.com`, rejects redirects for canonical-source review, observes robots rules, and produces metadata-only candidate JSON. It does not contact a router, accept credentials, use an LLM, or activate retrieved material. External documentation and router output remain untrusted input to the agent.

Configuration writes are task-specific agent actions, not helper functionality. An agent must establish authorization, relevant firmware behavior, recovery, and verification. Written guidance cannot enforce the agent's behavior; the host runtime's permission controls remain essential.

## Sensitive artifacts

Keep credentials, private keys, full profiles, backups, full configuration exports, client identifiers/topology, DNS query history, logs, and scanner reports outside the published repository. Ignore rules are a convenience, not a secret detector. Use synthetic examples and inspect every staged diff before committing.

Optional static scanning can be performed with NVIDIA SkillSpector or your organization's review tooling. Static dependency analysis may query package vulnerability services even when LLM analysis is disabled. Local scan receipts can contain paths and snippets; this repository publishes a limited validation record, not raw scanner output.

## Reporting a vulnerability

Do not post credentials, reachable router addresses, private diagnostics, or a working exploit against a live device in a public issue. If the hosting repository has private vulnerability reporting enabled, use its Security tab. Otherwise contact the maintainer through a private channel listed on their verified GitHub profile; this package does not invent a reporting address or enable an inbox.

Report package/version, affected file or behavior, a synthetic reproduction, impact, and any mitigation. For vulnerabilities in router firmware or a third-party application, use that project's official security reporting process.

No security SLA or supported firmware-version guarantee is implied. Review the [validation record](repository-docs/validation.md) for the actual scope of testing.
