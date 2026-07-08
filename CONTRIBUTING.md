# Contributing

Thanks for helping make MoMo_tools safer and more useful.

Before opening a pull request:

1. Keep examples synthetic. Do not include private capability indexes, customer names, account names, internal hosts, credentials, screenshots, or production evidence.
2. Run the local checks:

```bash
plugin/scripts/momo-tools test
plugin/scripts/momo-tools evidence
plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate
```

3. If you add a capability type, update `capabilities.schema.json`, `docs/risk-model.md`, and at least one routing fixture.
4. If you change routing behavior, add or update a case in `tests/fixtures/routing-benchmark.json`.

MoMo_tools should remain local-first. Public CI must not call private connectors, browsers, email, databases, or production tools.

