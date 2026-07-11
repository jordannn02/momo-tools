# Release Notes

## v0.2.1-public - 2026-07-11

- add public-safe `doctor` diagnostics over explicit public index, routing fixtures, evidence, and optional installed-copy inputs;
- add deterministic `repair-plan --dry-run` output with no apply mode, one action per finding, unknown findings blocked by default, and strict CI semantics;
- keep both commands read-only: no capability execution, private index discovery, home/cache scan, recovery drill, network call, or write operation;
- make strict doctor require an explicitly named independent installed copy while non-strict doctor remains diagnostic;
- reject symlinked installed/plugin roots, nested directory symlinks, and symlinks to independent equal-byte artifacts; anchor traversal to open directory descriptors, re-check every component after hashing, and verify identity, size, mtime, and ctime stability;
- treat failed `verified-working` evidence and malformed, empty, blank-assertion, or assertionless index or route fixtures as non-healthy fail-closed findings without tracebacks;
- require repair advice to recompute the trusted canonical artifact hash and verify the explicit installed root plus exact target state through descriptor-anchored existing or missing-path checks;
- execute and assert doctor/repair safety contracts in source-install and extracted-release CI paths.

## v0.2.0-public - 2026-07-11

- add strict public trust-lifecycle checks for evidence freshness, package integrity, recovery drills, and aggregate SLO health;
- require an independent installed copy and reject both whole-root and per-artifact symlink or hardlink aliases using open-file identity;
- return machine-readable integrity failures for missing, mismatched, aliased, non-regular, and unreadable artifacts without blocking or leaking tracebacks;
- make the tracked-file private-context scan self-nonmatching, non-echoing, and fail closed when the scan command errors;
- add regression coverage for CI scan behavior, canonical-root rejection, per-artifact aliases, corruption, and read failures.
- add a single release version source, deterministic committed-ref snapshot builder, SHA-256/JSON provenance outputs, and CI reproducibility comparison.

## v0.1.0-public

First public-ready MoMo_tools package.

Includes:

- local-first capability index schema;
- sample JSON and simple YAML capability indexes;
- `momo-tools` CLI commands: `validate`, `dashboard`, `list`, `route`, `audit`, `benchmark`, `evidence`, `pressure`, `test`;
- risk gates for write, private data, external network, credentials, local apps, and local files;
- action gates for persist, send, delete, external-call, private-read, and credential-use;
- verification levels: `visible`, `executed`, `verified-working`;
- route fixture tests, starter routing benchmark, pressure tests, and evidence JSONL validation;
- static Evidence Dashboard demo with synthetic visual proof assets;
- local installer that copies the public package to `~/.momo-tools`;
- GitHub Actions CI validation, install smoke test, YAML check, evidence check, and private-context leak scan;
- documentation for architecture, schemas, risk model, verification levels, evidence, workflows, tests, and second-brain integration.

Not included:

- private capability indexes;
- real connector calls;
- browser profile access;
- production or account writes;
- user-specific workspace evidence;
- background automation.
- live dashboard backend or production telemetry.
