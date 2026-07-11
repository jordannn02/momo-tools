---
name: momo-tools
description: Route an AI agent task through a local capability index, risk gates, action gates, and verification levels before choosing tools. Use when the user asks which tool/skill/plugin/connector/script to use, wants a capability dashboard, or needs a safe workflow for work that could touch files, private data, credentials, external services, browser state, automation, or persistence.
---

# MoMo_tools

MoMo_tools is a local-first capability router. It helps an agent choose the smallest safe capability set instead of exposing every available tool.

## Use When

- The user asks which tool, skill, plugin, connector, or script should be used.
- A task could involve writes, saves, private data, credentials, external network calls, browser/local app state, scheduled automation, or destructive operations.
- The user asks for a dashboard or audit of available capabilities.
- A workflow should distinguish installed/configured tools from verified tools.

## Core Rule

Do not treat a capability as safe or working just because it is registered.

Respect `verification_level`:

- `visible`: discoverable only.
- `executed`: ran once on a bounded task with evidence.
- `verified-working`: repeatable evidence and risk boundary documented.

## Suggested Commands

```bash
./plugin/scripts/momo-tools validate
./plugin/scripts/momo-tools dashboard
./plugin/scripts/momo-tools route --prompt "Summarize this PDF, do not save anything"
./plugin/scripts/momo-tools benchmark
./plugin/scripts/momo-tools evidence
./plugin/scripts/momo-tools pressure
./plugin/scripts/momo-tools doctor --as-of 2026-07-10T12:00:00+00:00
./plugin/scripts/momo-tools repair-plan --dry-run --as-of 2026-07-10T12:00:00+00:00
./plugin/scripts/momo-tools test
```

## Safety

Routing is advisory. The agent must still obey user constraints, approval gates, and host application safety rules.

MoMo_tools validation, benchmark, evidence, pressure, doctor, and repair-plan checks should not call real connectors, access browser profiles, read secrets, or mutate production systems.

Run strict `doctor` from a source checkout with an explicit independent `--installed-root`. Non-strict doctor is diagnostic. `repair-plan` requires `--dry-run`, has no apply mode, and must leave `applied=false` with `write_operations_executed=0`.
