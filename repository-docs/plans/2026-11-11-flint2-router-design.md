# Flint 2 Router Skill Design

Approved by the repository owner on 2026-11-11, including the MIT license.

## Goal

Publish a portable agent skill for configuring and troubleshooting the GL.iNet Flint 2 (GL-MT6000) running GL.iNet 4.x firmware. Support controlled SSH execution and current official documentation without embedding a copy of the vendor manual.

## Architecture

Keep a concise root `SKILL.md`, optional runtime-specific discovery metadata, focused operational references, a machine-readable official documentation inventory, and two dependency-free Python helpers. The helpers discover public documentation and collect a small read-only router inventory; configuration changes remain task-specific rather than an unverified generic mutation engine.

Route tasks by subject and firmware. Distinguish GL.iNet firmware from upstream OpenWrt, and identify the actual SDK/build, installed tools, configuration sections, firewall backend, network topology, and GL.iNet service ownership before proposing writes. An interface guide demonstrates UI behavior; it does not establish an undocumented SSH or RPC interface.

## Operating contract

Inspect, look up the relevant versioned documentation, prepare a scoped change and recovery plan, execute authorized changes, and verify effective behavior. Additional confirmation is needed only for consequential unresolved decisions, such as downtime, new WAN exposure, or replacement of existing configuration. Diagnosis alone does not authorize repair. Never collect or publish credentials, raw configuration bundles, or private router diagnostics.

Before a change that could disconnect management access, establish a working backup and a tested recovery mechanism independent of that SSH session. A backup alone is not rollback. Verify access from a new session and test the actual requested outcome. Never interpret a disconnection or successful commit as proof of completion.

## Documentation and maintenance

The initial crawl fetched 82 Interface Guide URLs, including the index and version variants, plus the model guide, SSH guide, and three release guides: 87 successful documents. Publish URLs, titles, retrieval metadata, and hashes, not downloaded manuals. Version mentions in a document are search hints, not compatibility guarantees. Re-fetch only task-relevant sources during use; use a separate candidate inventory when refreshing the catalog.

Provide focused references for access/discovery, networking, VPN, DNS/applications, security/maintenance, and recovery. Cover the rest of the interface through the catalog, hardware checks, and on-demand official guides. Mark unavailable or unverified SSH mappings honestly and use the documented admin UI where appropriate.

## Public repository

Use an original accessible SVG banner and a concise, polished GitHub README. Include installation and examples, the MIT license for original work, third-party attribution, contributor/security guidance, local tests, and CI. Keep downloaded pages, backups, diagnostics, scanner reports, and credentials outside the published package. Do not create a GitHub remote or publish without a separate instruction.

## Runtime compatibility

Design the core for any agent runtime that provides local file reading, a shell/OpenSSH client, and a public documentation retrieval tool. Describe each target runtime's native skill discovery separately. Optional UI metadata does not supply tools or credentials to another runtime. No runtime is installed or configured by this authoring task; actual loader and live-router support require separate verification in the target environment.

## Validation

Use offline behavioral scenarios before and after authoring, fixtures for helper boundaries, subprocess argument and redaction checks, crawler scope/redirect/size/error checks, local link and skill structure validation, and visual inspection of the README banner. Scan and source-review the full final package with NVIDIA SkillSpector through the existing admission gate. Store exact-payload receipts locally outside the repository. No live router mutations are part of this authoring task.
