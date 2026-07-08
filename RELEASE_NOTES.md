# Release Notes

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
