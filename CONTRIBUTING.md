# Contributing

Keep changes small, source-grounded, and firmware-specific. Original contributions are licensed under this repository's MIT license.

## What makes a useful change

- A verified procedure records exact model, GL.iNet version, base/SDK, configuration/service ownership, prerequisites, scoped change, recovery, and outcome checks.
- A UI document establishes UI behavior; an SSH mapping needs independent installed-firmware or official-source evidence.
- Use official sources first and link the actual version selector. Label community advice and unverified hypotheses explicitly.
- Keep the entrypoint concise. Put substantial topic-specific guidance in its existing reference; add a new file only when it has a real caller and purpose.
- Preserve authorization boundaries. Avoid universal admin scripts, broad dumps, blanket package upgrades, and default credentials.

## Local checks

Python 3.10+ and the standard library are sufficient for the repository tests:

```sh
python -B -m unittest discover -s tests -v
git diff --check
```

Tests use synthetic router and HTTP responses. Never point CI or unit tests at a live router. For helper changes, add a failing behavior test first, then implement and verify it. Useful boundaries include destination validation, trust settings, sensitive output, network scope, response limits, partial failures, and candidate replacement rules.

For instruction changes, test a realistic user request independently with only the skill and minimum raw observations. Record the result and limitations. Do not brief an evaluator with the desired answer. Live network tests require the router owner's explicit scope and recovery arrangements.

## Refresh documentation deliberately

Use [the refresh workflow](references/documentation.md) to write a new candidate under `.local/`. Review source additions/removals, titles, hashes, version selectors, and the topic references affected. A changed HTML hash may reflect site navigation rather than an operational change. Do not copy manuals or their images into the skill.

## Before release

1. Review every changed instruction, script, dependency, network destination, and sensitive behavior.
2. Run structural validation, the offline suite, link checks, and the target environment's final-payload security review. Re-scan after changes. Keep receipts outside runtime discovery and this repository.
3. Update the factual validation record. Distinguish fixture tests, behavioral evaluations, actual loader checks, and real hardware execution. Do not promote intended compatibility to tested support.
4. Inspect the complete staged diff for secrets, local paths, unrelated edits, generated output, downloaded content, and binary router backups.
5. Commit the complete coherent change. Publishing or installing runtime copies is a separate authorized action.

## Runtime integration

The core intentionally uses portable file reading, shell/OpenSSH, and public documentation retrieval. Runtime-specific UI metadata is optional. Document native discovery, actual tool support, and permission controls for each target runtime. An adapter must preserve permission and data boundaries, receive its own complete-payload review if its bytes differ, and be tested in that runtime before being described as supported.
