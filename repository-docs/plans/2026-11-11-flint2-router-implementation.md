# Flint 2 Router Skill Implementation Plan

> For Claude: use the established executing-plans workflow when continuing this plan in a separate session. The owner has already authorized implementation in the current session.

**Goal:** Deliver a tested, documented, MIT-licensed skill repository ready for public GitHub publication.

**Architecture:** A short `SKILL.md` routes to focused references and a provenance-bearing official source catalog. Two standard-library Python CLIs support public-source discovery and a bounded read-only SSH inventory; the agent performs firmware-specific configuration with recovery and verification.

**Tech Stack:** Agent Skills Markdown, Python 3.10+, OpenSSH, JSON, YAML metadata, SVG, GitHub Actions.

## Task 1: Record the design and baseline behavior

- Create this plan and the approved design under `repository-docs/plans/`.
- Initialize the separate repository on `main` and commit the approved design.
- Run an independent offline baseline for VPN policy, management-disrupting networking, and SQM/acceleration tasks before writing the skill.
- Record observed outcomes honestly; a baseline that passes is not a failure.

## Task 2: Test helper behavior at public boundaries

Create `tests/test_inspect_router.py`, `tests/test_refresh_docs.py`, and synthetic fixtures where useful. The agreed test seams are the CLIs' arguments/results and the SSH/HTTP transport boundaries; tests must not contact a router or public service.

- Verify malformed destinations and option injection are rejected before subprocess creation.
- Verify the SSH invocation preserves host-key checking, has bounded timeouts, and sends only a fixed read-only script.
- Verify output is an explicit allowlist, secrets in extra fields are omitted, unsupported hardware fails closed, and command failures remain failures.
- Verify documentation discovery includes sitemap and linked version variants, deduplicates fragments, rejects off-scope redirects, respects robots rules, bounds responses and page counts, and never publishes incomplete results as a successful snapshot.
- Run `python -B -m unittest discover -s tests -v` and observe the expected failures because helpers do not yet exist.

## Task 3: Author the skill and helpers

Create `SKILL.md`, `agents/openai.yaml`, `references/{documentation,access-and-discovery,networking,vpn,dns-and-applications,security-and-maintenance,recovery}.md`, `references/official-docs.json`, and `scripts/{inspect_router,refresh_docs}.py`.

- Use only the preserved successful crawl metadata for the initial source inventory.
- Keep original operational guidance separate from vendor facts and examples.
- Implement fixed read-only inspection using `subprocess.run` with an argument list, normal OpenSSH trust checks, explicit host/port/key inputs, no passwords in arguments, and bounded output.
- Implement a same-origin documentation crawl using standard-library HTTP, XML, and HTML parsers. Fetch robots and sitemap, follow only authorized documentation links, and save a candidate snapshot only when complete.
- Review source and run the static admission scan before executing candidate helpers. After changes, renew evidence before using the changed payload.
- Run unit tests and structural validation after source review and admission.

## Task 4: Prepare public packaging and README

Create `README.md`, `LICENSE`, `NOTICE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.gitignore`, `.gitattributes`, `.github/workflows/validate.yml`, `assets/banner.svg`, and `tests/test_package.py`.

- Use a distinctive dark/navy and mint original banner with accessible text, readable mobile composition, compact capability sections, install instructions, and realistic prompts.
- Describe Codex, Claude Code, Antigravity, and Hermes separately and distinguish intended portability from actual runtime tests.
- Keep secrets, router exports, local reports, caches, and bytecode ignored; install nothing into active runtime skill directories.
- Validate local Markdown links, parse SVG/XML and JSON, and visually inspect the banner/README layout using existing local rendering tools.

## Task 5: Forward-test, scan, and finish

- Run independent forward tests with realistic raw scenarios and the skill, without disclosing baseline conclusions or intended answers.
- Fix demonstrated gaps; re-run affected checks and re-scan the complete changed package.
- Record reproducible validation results and limitations in `repository-docs/validation.md`.
- Run `python -B -m unittest discover -s tests -v`, the bundled skill-creator validator, `git diff --check`, and the final static gate verification.
- Inspect `git diff --cached` and commit explicit task-owned paths. Verify a clean working tree and report the local repository, README, tests, security result, and commit.

Publishing, installing runtime copies, and live router access are separate tasks.
