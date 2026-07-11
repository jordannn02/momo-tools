# MoMo_tools Plugin Package

This folder contains the public plugin package:

- `.codex-plugin/plugin.json`: plugin metadata
- `skills/momo-tools/SKILL.md`: agent-facing operating instructions
- `scripts/momo-tools`: local CLI
- `capabilities.example.json`: canonical example index used by CLI
- `capabilities.example.yaml`: simple YAML equivalent

The public package is intentionally synthetic. Replace the example index with your own `capabilities.local.json` or simple YAML file, and keep private paths, account names, customer data, credentials, and production details out of public repositories.

Core checks:

```bash
plugin/scripts/momo-tools validate
plugin/scripts/momo-tools benchmark
plugin/scripts/momo-tools evidence
plugin/scripts/momo-tools test
MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test scripts/install-local.sh
plugin/scripts/momo-tools doctor --as-of 2026-07-10T12:00:00+00:00 --installed-root /tmp/momo-tools-public-install-test --strict
plugin/scripts/momo-tools repair-plan --dry-run --as-of 2026-07-10T12:00:00+00:00 --installed-root /tmp/momo-tools-public-install-test --strict
scripts/build-release-snapshot.sh --ref HEAD --output-dir dist/release
```

`doctor` reads only explicit public fixtures and an optional installed-copy path. It never discovers a private index, scans a home/cache directory, runs a capability, or invokes the recovery drill. `repair-plan` has no apply mode and emits advisory or blocked actions only.
