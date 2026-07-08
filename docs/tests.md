# Tests

MoMo_tools public v0.1 ships with lightweight local tests.

## Existing Coverage

| Command | What it checks |
|---|---|
| `validate` | Required fields, duplicate names, verification level values. |
| `dashboard` | Count by verification level and risk. |
| `audit` | Fixture prompts route to expected capabilities and gates. |
| `pressure` | Conflict prompts keep risk gates visible and block unsafe save behavior. |
| `test` | Runs validation, audit, and a pressure check together. |

## Proposed Next Tests

| Test | Type | Why |
|---|---|---|
| YAML parser compatibility | automated | Many users prefer YAML indexes. |
| Package install smoke test | automated | Confirm local installer works on fresh machine. |
| Redaction scanner | automated | Prevent publishing local paths or secrets. |
| Codex plugin install test | guarded manual | Plugin install flow may vary by host. |

## Gaps

| Gap | Risk |
|---|---|
| Router scoring is simple keyword matching. | It can miss semantic matches. |
| No dependency-managed package yet. | Users run from source or local installer. |
| No CI config yet. | Public repo should add CI before release. |

