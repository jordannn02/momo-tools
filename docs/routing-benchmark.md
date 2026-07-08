# Routing Benchmark

`tests/fixtures/routing-benchmark.json` is a starter benchmark for routing behavior. It uses the same shape as the smaller audit fixture:

```json
{
  "id": "repo_release_blockers",
  "prompt": "Review this repository for release-blocking bugs, regression risk, and missing tests.",
  "expected": ["repo-review"],
  "forbidden": [],
  "must_gate": ["local-file"]
}
```

Run:

```bash
plugin/scripts/momo-tools benchmark
```

The current benchmark intentionally covers a compact set of cases:

- easy routing
- ambiguous prompts
- no-save and no-web conflicts
- private data gates
- write-capable workflows
- local app and frontend workflows
- data analysis workflows

For a production index, grow this to 50-100 cases and keep separate files for team-specific prompts. Benchmark cases should stay synthetic unless the repository is private.

