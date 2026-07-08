# Publication Checklist

Use this before making the repository public.

## Required

- [ ] Confirm `README.md` explains the problem, approach, and quickstart.
- [ ] Run `plugin/scripts/momo-tools test`.
- [ ] Run local install smoke test with `MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test`.
- [ ] Confirm examples use synthetic capability names only.
- [ ] Confirm no private paths, customer names, account names, screenshots, or production evidence are included.
- [ ] Confirm the license is intentional.
- [ ] Optional: copy `docs/github-actions-ci.example.yml` to `.github/workflows/ci.yml` after authenticating with workflow scope.
- [ ] Optional: confirm CI passes on GitHub.

## Private Context Scan

```bash
rg -n "YOUR_NAME|/Users/YOUR_NAME|YOUR_COMPANY|YOUR_CUSTOMER|YOUR_HOST|YOUR_DATABASE|YOUR_SECRET_LABEL" .
```

This scan is project-specific. Add your own organization, customer, host, and
account terms before publishing a fork.

## Suggested First GitHub Description

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
