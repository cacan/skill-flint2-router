# Validation record

Release preparation date: 2026-11-11. This record distinguishes authored capability, offline checks, and real-device execution. It is not a hardware certification.

## Evidence available at authoring

The initial research retrieved 87 successful official documents on 2026-11-11: 82 Interface Guide URLs including its index and version variants, plus the Flint 2 guide, SSH guide, and three release guides. The catalog contains metadata and hashes, not article bodies. Additional recovery and download-center links were checked separately. Retrieval dates are not release dates.

An independent baseline exercise, without the skill, addressed selected-client WireGuard routing, access-changing LAN/port configuration, and SQM/acceleration on a metered link. The agent recognized the main VPN, recovery, and SQM constraints. It also proposed a whole policy-package export and cited an unverified version-suffixed dashboard URL. These observations motivated targeted reads and catalog-backed source selection; no claim is made that the baseline failed every scenario.

The helper suite was run before implementation: all 13 initial tests failed because the helpers did not yet exist. This established the missing behavior at the transport/output boundaries before code was added.

## Verification status

| Requirement | State | Evidence |
| --- | --- | --- |
| Separate repository and approved design | Recorded | Approved design and implementation plan committed before the skill was written |
| Documentation coverage | Checked | 87 unique successful retrievals; original research cache read back before metadata import |
| Helper and package tests | Pass | 24 unittest checks on Windows / Python 3.14; controlled local subprocesses and synthetic HTTP responses |
| Skill structure and local links | Pass | Bundled skill-creator validator; package tests resolve local links and anchors and parse Python, JSON and SVG |
| Independent forward testing | Pass within offline scope | Four scenario responses inspected: selected-client VPN, LAN/port changes, metered SQM, and read-only DNS diagnosis with hostile retrieved text |
| Static security review | Complete with reviewed findings | NVIDIA SkillSpector 2.12.0 through the admission gate, with LLM analysis disabled; LOW / SAFE, three individually reviewed MEDIUM findings |
| README/banner appearance | Checked | Local browser preview at desktop and 390px mobile width; banner loaded and no document-width overflow observed |
| Documentation helper live retrieval | Checked | Live metadata refresh returned 87 URLs matching the maintained catalog; final HTTP200 transport check fetched the interface index successfully |
| Live router mutations | Unverified | No live router was connected or changed during authoring |
| Runtime loader checks | Unverified | No skill was installed into Codex, Claude Code, Antigravity, or Hermes |
| Hosted CI | Unverified | Workflow prepared; GitHub execution requires publication |

## Reproduce offline checks

```sh
python -B -m unittest discover -s tests -v
git diff --check
```

The suite does not require router access, network requests, credentials, or third-party Python packages. One remote-script exit-status fixture uses an existing local POSIX shell and is skipped if none exists. No checks were skipped in the recorded Windows run. The inventory helper's real OpenSSH/router interaction requires separate scoped verification. Before using a changed package, review its final source and security evidence again.

## Behavioral and source-review results

The forward evaluator used the skill and relevant references with raw observations, without being given the intended answers or baseline conclusions. It selected the actual v4.9+ dashboard URL, distinguished tunnel and enhanced kill switches, avoided guessed policy mutation commands and whole profile exports, required topology/recovery evidence before access-changing writes, respected the metered-link restriction, and treated a retrieved backup-upload instruction as untrusted data. Every router operation remained explicitly proposed. The exercise is evidence about those responses, not a guarantee of future model behavior or live routing correctness.

The evaluator identified ambiguity around an operator declining archival backups. The recovery reference now respects that explicit choice while requiring an adequate remaining recovery path for disruptive writes.

Independent source review identified four concrete helper issues: unbounded SSH capture, redirect provenance/robots handling, partial HTTP response acceptance, and a pipeline masking `ubus` failure. Regression checks reproduced these gaps before corrections. The final helpers cap stdout/stderr while draining, reject redirects for explicit canonical-source review, require HTTP200, and preserve the router command's exit status. The source review found the requested public-package components present and authorization/support claims appropriately bounded.

## Static admission scope

The complete package was staged outside active skill discovery and scanned with the existing gate using `--no-llm --fail-on-incomplete`. No hosted semantic analysis or telemetry configuration was enabled. Static dependency checks can still contact vulnerability services; this is not described as an offline scan.

The remaining findings are declared-capability metadata (`LP3`) and two explicit subprocess sites (`AST4`): the fixed, validated SSH transport and the controlled local POSIX regression fixture. Source review explains their necessary scope, input handling, time/output limits, runtime permissions, and user authorization. Runtime-specific tool preapproval was not added to silence a metadata finding. There are no HIGH/CRITICAL findings in the admitted package. Local receipts bind the exact payload, report bytes, scanner version, reviewer and timestamp; they stay outside this repository and are not security signatures.

The README's CI actions are pinned to commits obtained from the official action release tags on 2026-11-11. The hosted Linux/Windows matrix has not run in GitHub during local preparation. Prepared CI is distinct from executed CI.
