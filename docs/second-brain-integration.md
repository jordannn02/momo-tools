# Second Brain Integration

MoMo_tools and a second-brain system solve different parts of the agent workflow.

| Layer | Responsibility |
|---|---|
| MoMo_tools | Route a task to the smallest sufficient capability set, surface risk gates, and require verification evidence. |
| Second brain | Remember what route worked, what failed, what evidence mattered, and what should change next time. |

## Minimal Loop

```text
user task
  -> momo-tools route
  -> agent runs bounded capability
  -> evidence JSONL record
  -> capture event in second brain
  -> future routing preference
```

## Capture Event Shape

This repository does not ship a second-brain CLI. It only shows the safe handoff shape:

```json
{
  "task_id": "example-2026-07-08-route-review",
  "prompt_class": "repo-review",
  "route": {
    "capabilities": ["repo-review"],
    "gates": ["local-file"],
    "actions": []
  },
  "outcome": "passed",
  "evidence_ref": "evidence/example-verification.jsonl#repo-review",
  "next_time": "Use repo-review before broad web research for local release-risk questions."
}
```

Keep this boundary:

- capture after the user has received the useful result;
- write only when the user allows persistence or the workflow policy permits it;
- never publish private vault paths, customer names, hostnames, credentials, screenshots, or production transcripts;
- keep evidence and memory distinct: evidence proves what happened, memory changes future behavior.

## What To Build Next

For a real second-brain project, add:

- `capture-event.schema.json`
- `memory-edge.schema.json`
- `route-suggest` examples
- dry-run consolidation before writing
- golden fixture vaults for snapshot tests

