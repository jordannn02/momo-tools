# MoMo_tools

[![CI](https://github.com/jordannn02/momo-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/jordannn02/momo-tools/actions/workflows/ci.yml)

**A local-first capability router for AI coding agents.**

MoMo_tools helps agents choose a smaller, safer capability set before they touch tools. It turns skills, plugins, MCP servers, scripts, apps, and connectors into a reviewable capability index with risk gates and verification evidence.

![MoMo_tools workflow](assets/momo-tools-flow.png)

## Why This Exists

Modern coding agents often see too many tools at once. That creates three failure modes:

- noisy tool selection when a smaller local capability would work;
- installed tools competing for context even when they are irrelevant;
- "installed" being mistaken for "safe and verified".

MoMo_tools adds a thin governance layer:

| Layer | What it answers |
|---|---|
| Capability index | What exists, where it lives, and what it is for. |
| Risk gates | Whether the task crosses write, private data, credential, browser, or network boundaries. |
| Action gates | Whether the prompt implies persist, send, delete, external-call, private-read, or credential-use actions. |
| Verification levels | Whether the capability is merely visible, executed once, or verified-working. |
| Routing checks | Which capability set is sufficient for the prompt. |
| Pressure tests | Whether conflicts like "remember this" plus "do not save" stay safe. |

MoMo_tools does not execute your private tools. It routes and audits metadata so the agent can ask for the right capability with the right boundary.

## Quickstart

Run from the repository:

```bash
chmod +x plugin/scripts/momo-tools scripts/install-local.sh
plugin/scripts/momo-tools validate
plugin/scripts/momo-tools dashboard
plugin/scripts/momo-tools route --prompt "Read this PDF, summarize it, do not save anything"
plugin/scripts/momo-tools audit
plugin/scripts/momo-tools benchmark
plugin/scripts/momo-tools evidence
plugin/scripts/momo-tools pressure
plugin/scripts/momo-tools test
```

Or install a local copy:

```bash
scripts/install-local.sh
~/.momo-tools/bin/momo-tools dashboard
```

The installer copies the public package into `~/.momo-tools` by default. It does not modify Codex, Claude, Cursor, browser profiles, credentials, shell startup files, or private indexes.

## Visual Demo

MoMo_tools also ships a static Evidence Dashboard that turns development-time fixture screenshots into a public-safe review layer:

```bash
python3 -m http.server 4173 --directory demo
```

Then open `http://127.0.0.1:4173`.

The demo is intentionally static: no private connectors, no production data, no account screenshots, no writes, and no network calls.

## Use Your Own Workflow

Start from the sample index:

```bash
cp plugin/capabilities.example.json capabilities.local.json
```

Then replace the examples with your own capabilities:

```json
{
  "name": "repo-review",
  "type": "skill",
  "trigger": ["review code", "security audit", "regression risk"],
  "scope": "local repo",
  "path_or_tool": "skills/repo-review/SKILL.md",
  "risk": ["read-only", "local-file"],
  "source": "local",
  "owner": "you",
  "version": "0.1.0",
  "last_verified": "2026-07-08",
  "verification_level": "visible",
  "known_caveats": ["No runtime execution proof yet."],
  "canonical_for": ["code review"],
  "workflow_shape": "inspect -> findings -> tests"
}
```

Use the local index with:

```bash
plugin/scripts/momo-tools --index capabilities.local.json dashboard
plugin/scripts/momo-tools --index capabilities.local.json route --prompt "Review this repo for release risk"
```

Simple YAML indexes are also supported:

```bash
plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate
```

See [docs/schemas.md](docs/schemas.md) for the JSON schema and YAML boundary.

## Commands

| Command | Purpose |
|---|---|
| `validate` | Checks required fields, duplicate names, list fields, and verification levels. |
| `dashboard` | Summarizes verification levels, risk tags, and validation health. |
| `list` | Prints capability names, types, levels, and risks. |
| `route --prompt ...` | Scores capabilities for one prompt and returns gates, actions, and matches. |
| `audit` | Runs the core routing fixture. |
| `benchmark` | Runs the broader starter routing benchmark. |
| `evidence` | Validates synthetic JSONL verification evidence. |
| `pressure` | Runs conflict prompts such as no-save plus remember-this. |
| `test` | Runs validation, audit, benchmark, and pressure checks together. |

## Verification Levels

| Level | Meaning |
|---|---|
| `visible` | Registered and discoverable. This does not prove login, runtime access, or success. |
| `executed` | Ran once on a bounded task and produced inspectable evidence. |
| `verified-working` | Has repeatable evidence plus an explicit risk boundary. |

Promotion should be earned. A capability should not become `verified-working` just because it is installed.

See [docs/evidence.md](docs/evidence.md) for the JSONL evidence format.

## Public Safety Boundary

This public version includes only synthetic examples:

- no private capability index;
- no real connector calls;
- no browser profile access;
- no email, Drive, Notion, database, or production writes;
- no local secrets or environment-specific paths;
- no automatic memory capture or automation runs.

If you fork this project, keep your private capability index out of the public repo.

## Project Shape

```text
.github/workflows/ci.yml
capabilities.schema.json
plugin/
  .codex-plugin/plugin.json
  capabilities.example.json
  capabilities.example.yaml
  scripts/momo-tools
  skills/momo-tools/SKILL.md
docs/
  architecture.md
  evidence.md
  risk-model.md
  routing-benchmark.md
  schemas.md
  tests.md
  verification-levels.md
  workflows.md
demo/
  index.html
  app.js
  styles.css
  assets/evidence/
examples/
  personal-workflow.capabilities.yaml
  team-dev.capabilities.yaml
  docs-research.capabilities.yaml
tests/fixtures/
  route-cases.json
  routing-benchmark.json
evidence/
  example-verification.jsonl
```

## Second Brain Loop

MoMo_tools is the routing and safety layer. A second-brain system can be the long-term learning layer.

```text
user task
  -> momo-tools route / gates / verification
  -> bounded tool use by the agent
  -> evidence record
  -> optional second-brain capture after user-safe delivery
  -> future routing preference
```

See [docs/second-brain-integration.md](docs/second-brain-integration.md) for a minimal integration sketch.

## Roadmap

- Grow the routing benchmark from the starter fixture to 50-100 synthetic cases.
- Add optional JSON Schema validation in pre-commit examples.
- Add richer action-level gates for send, persist, delete, external-call, private-read, and credential-use.
- Add more evidence fixtures for `executed` and `verified-working` promotion.
- Provide a private-index template that is safe to keep outside public Git.

## Design Principle

MoMo_tools is not a bigger toolbox. It is a decision layer that makes tool use smaller, safer, and more auditable.
