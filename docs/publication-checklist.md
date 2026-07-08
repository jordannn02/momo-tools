# Publication Checklist

Use this before publishing or tagging a release.

## Required

- [ ] Confirm `README.md` explains the problem, approach, quickstart, and safety boundary.
- [ ] Run `plugin/scripts/momo-tools test`.
- [ ] Run `plugin/scripts/momo-tools evidence`.
- [ ] Run `plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate`.
- [ ] Run local install smoke test with `MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test`.
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
