---
name: momo-tools
description: Route an AI agent task through a local capability index, risk gates, and verification levels before choosing tools. Use when the user asks what tool/skill/plugin/connector/script to use, wants a capability dashboard, or needs a safe workflow for a task that could touch files, private data, credentials, external services, browser state, or automation.
---

# MoMo_tools

MoMo_tools is a local-first capability router. It helps the agent choose the
smallest safe capability set instead of exposing every available tool.

## Use When

- The user asks which tool, skill, plugin, connector, or script should be used.
- A task could involve writes, saves, private data, credentials, external
  network calls, browser/local app state, scheduled automation, or destructive
  operations.
- The user asks for a dashboard or audit of available capabilities.
- A workflow should distinguish installed/configured tools from verified tools.

## Core Rule

Do not treat a capability as safe or working just because it is registered.
Respect `verification_level`:

- `visible`: discoverable only.
- `executed`: ran once on a bounded task with evidence.
- `verified-working`: repeatable evidence and risk boundary are documented.

## Suggested Commands

```bash
./plugin/scripts/momo-tools validate
./plugin/scripts/momo-tools dashboard
./plugin/scripts/momo-tools route --prompt "Summarize this PDF, do not save anything"
./plugin/scripts/momo-tools audit
./plugin/scripts/momo-tools pressure
```

## Safety

Routing is advisory. The agent must still obey user constraints, approval gates,
and the host application's safety rules. MoMo_tools should not call real
connectors, access browser profiles, read secrets, or mutate production systems
as part of validation or pressure tests.

