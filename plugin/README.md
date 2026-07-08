# MoMo_tools Plugin Package

This folder contains the public plugin package:

- `.codex-plugin/plugin.json`: plugin metadata
- `skills/momo-tools/SKILL.md`: agent-facing operating instructions
- `scripts/momo-tools`: local CLI
- `capabilities.example.json`: canonical example index used by the CLI
- `capabilities.example.yaml`: human-readable equivalent

The public package is intentionally synthetic. Replace the example index with
your own `capabilities.local.json` and keep private paths, account names,
customer data, credentials, and production details out of public repos.

