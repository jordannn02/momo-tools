# Publication Checklist

Use this before publishing or tagging a release.

## Required

- [ ] Confirm `README.md` explains the problem, approach, quickstart, and safety boundary.
- [ ] Run `plugin/scripts/momo-tools test`.
- [ ] Run `plugin/scripts/momo-tools evidence`.
- [ ] Run `plugin/scripts/momo-tools freshness --as-of 2026-07-10T12:00:00+00:00 --strict` against the synthetic evidence fixture.
- [ ] Run `python -m unittest discover -s tests -p 'test_*.py' -v`.
- [ ] Run local install smoke test with `MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test`.
- [ ] Run `/tmp/momo-tools-public-install-test/bin/momo-tools test` as the installed-binary smoke test.
- [ ] From the source checkout, run `plugin/scripts/momo-tools integrity --installed-root /tmp/momo-tools-public-install-test --strict`.
- [ ] Run `plugin/scripts/momo-tools recovery-drill --strict` and confirm `temporary_only`, `source_unchanged`, and `passed` are all `true`.
- [ ] From the source checkout, run `plugin/scripts/momo-tools slo --as-of 2026-07-10T12:00:00+00:00 --installed-root /tmp/momo-tools-public-install-test --strict`.
- [ ] Run `plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate`.
- [ ] Compare that temporary install with `integrity --installed-root /tmp/momo-tools-public-install-test --strict`.
- [ ] Confirm release notes do not claim that integrity or recovery protects a user's real installation.
- [ ] Confirm examples use synthetic capability names only.
- [ ] Confirm no private paths, customer names, account names, screenshots, or production evidence are included.
- [ ] Confirm `capabilities.schema.json` still matches required fields in the CLI.
- [ ] Confirm license is intentional.
- [ ] Confirm `.github/workflows/ci.yml` passes on GitHub.

## Private Context Scan

```bash
rg -n "YOUR_NAME|YOUR_HOME_PATH|YOUR_COMPANY|YOUR_CUSTOMER|YOUR_HOST|YOUR_DATABASE|YOUR_SECRET_LABEL" .
```

Add your own organization, customer, host, and account terms before publishing a fork.

## Suggested GitHub Description

Local-first capability router and safety gate for AI agent tools.

## Suggested Topics

- ai-agents
- codex
- agent-skills
- tool-routing
- mcp
- local-first
- safety
- developer-tools
