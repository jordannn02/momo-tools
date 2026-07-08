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
```

