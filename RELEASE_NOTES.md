# Release Notes

## v0.1.0-public

First public-ready MoMo_tools package.

Includes:

- local-first capability index schema;
- sample JSON/YAML capability indexes;
- `momo-tools` CLI with `validate`, `dashboard`, `list`, `route`, `audit`, `pressure`, and `test`;
- risk gates for write, private data, external network, credentials, local apps, and local files;
- verification levels: `visible`, `executed`, `verified-working`;
- route fixture tests and pressure tests;
- local installer that copies the public package to `~/.momo-tools`;
- GitHub Actions CI for validation, install smoke test, and private-context leak scan;
- documentation for architecture, risk model, verification levels, workflows, and tests.

Not included:

- private capability indexes;
- real connector calls;
- browser profile access;
- production or account writes;
- user-specific workspace evidence;
- background automation.

