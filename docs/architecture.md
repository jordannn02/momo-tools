# Architecture

MoMo_tools is a local-first routing layer for AI agent capabilities.

It does not own your tools. It keeps a reviewable map of them and helps the
agent choose a small, safe set for a task.

## Components

| Component | Purpose |
|---|---|
| Capability index | JSON list of skills, plugins, scripts, connectors, or workflows. |
| Risk model | Tags such as `write`, `private-data`, `external-network`, `credential`, `local-app`, and `local-file`. |
| Verification levels | Distinguishes discoverable tools from tools with execution evidence. |
| Router | Scores a prompt against triggers and canonical use cases. |
| Gates | Flags risks and prompt conflicts before execution. |
| Audit cases | Known task prompts that should route to expected capabilities. |
| Pressure tests | High-conflict prompts such as "remember this" plus "do not save". |
| Doctor | Aggregates explicit public validation, routing, freshness, and package-integrity checks without executing capabilities or recovery. |
| Repair planner | Converts doctor findings into deterministic advisory or blocked dry-run actions with no apply mode. |

## Runtime Flow

1. User gives a task.
2. MoMo_tools loads the capability index.
3. The router scores relevant capabilities by trigger and canonical use case.
4. Risk hints from the prompt become gates.
5. Prompt negations such as "do not save" block conflicting capabilities.
6. The agent reviews the route result and decides what it may safely use.

MoMo_tools does not automatically execute matched capabilities. Routing is an
advisory control layer.

## Trust Boundaries

| Boundary | Rule |
|---|---|
| Local index | Safe to validate and route. |
| Local files | Requires task relevance and user intent. |
| Private data | Must be explicit and bounded. |
| External network | Must be needed for current facts or user request. |
| Credentials | Must use a secure secret flow outside the index. |
| Browser/local app state | Never inspect unrelated profiles or logged-in state. |
| Writes/destructive actions | Require explicit permission and postcheck. |

## Known Assumptions

- The sample index is synthetic.
- Verification levels are self-declared metadata unless supported by evidence.
- The router is intentionally simple and inspectable.
- Host agent safety policies still apply.

## Related Documents

- `risk-model.md`
- `verification-levels.md`
- `workflows.md`
- `tests.md`
