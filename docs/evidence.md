# Verification Evidence

MoMo_tools separates metadata from proof. A capability can be visible in an index without being safe or working in the user's environment.

Evidence records live in JSONL so they can be appended, reviewed, and redacted without rewriting the whole file.

```json
{"capability":"momo-tools","level":"verified-working","status":"passed","checked_at":"2026-07-08","command":"plugin/scripts/momo-tools test","evidence_ref":"tests/fixtures/route-cases.json","risk_boundary":["read-only"],"summary":"Synthetic routing tests pass."}
```

Required fields:

| Field | Meaning |
|---|---|
| `capability` | Capability name from the index. |
| `level` | `visible`, `executed`, or `verified-working`. |
| `status` | Short status such as `passed`, `failed`, or `metadata-only`. |
| `checked_at` | Date or timestamp of the check. |
| `command` | Bounded command or manual check used as evidence. |
| `evidence_ref` | File, fixture id, transcript id, or report anchor. |
| `risk_boundary` | Explicit limits proven by this evidence. |

Run:

```bash
plugin/scripts/momo-tools evidence
```

Visual fixture screenshots are available in the static demo:

```bash
python3 -m http.server 4173 --directory demo
```

Then open `http://127.0.0.1:4173`.

The public example evidence is synthetic. Do not publish private transcripts, customer data, local account names, hostnames, credentials, screenshots, or production evidence.
