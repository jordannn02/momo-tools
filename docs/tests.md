# Tests

MoMo_tools uses dependency-free smoke tests so the public repository can run in GitHub Actions without private tools.

| Command | What it checks |
|---|---|
| `validate` | Required fields, duplicate names, list fields, and verification level values. |
| `dashboard` | Verification level counts, risk counts, and validation health. |
| `audit` | Core routing fixture in `tests/fixtures/route-cases.json`. |
| `benchmark` | Broader starter routing fixture in `tests/fixtures/routing-benchmark.json`. |
| `evidence` | JSONL verification evidence shape in `evidence/example-verification.jsonl`. |
| `pressure` | Conflict prompts keep risk gates visible and block unsafe persistence. |
| `test` | Validation, audit, benchmark, and pressure in one command. |

Run everything locally:

```bash
plugin/scripts/momo-tools test
plugin/scripts/momo-tools evidence
plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate
```

CI also checks Python syntax, JSON syntax, local install smoke behavior, and a private-context leak scan.

## Known Limits

| Gap | Risk |
|---|---|
| Router scoring is simple keyword matching. | It can miss semantic matches. Add benchmark cases for failures. |
| JSON Schema is provided but not used as a runtime dependency. | The CLI remains dependency-free; use schema-aware IDE or pre-commit tools for deeper validation. |
| Public evidence is synthetic. | It proves format and routing behavior, not private runtime access. |
| No package manager metadata yet. | Users run from source or local installer. |

