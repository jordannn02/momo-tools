# Verification Evidence

MoMo_tools separates metadata from proof. A capability can be visible in an index without being safe or working in the user's environment.

Evidence records live in JSONL so they can be appended, reviewed, and redacted without rewriting the whole file.

```json
{"capability":"momo-tools","level":"verified-working","status":"passed","checked_at":"2026-07-08T09:00:00+00:00","valid_until":"2026-08-08T09:00:00+00:00","command":"plugin/scripts/momo-tools test","evidence_ref":"tests/fixtures/route-cases.json","risk_boundary":["read-only","synthetic examples only"],"summary":"Synthetic routing tests passed."}
```

Required fields:

| Field | Meaning |
|---|---|
| `capability` | Capability name from the index. |
| `level` | `visible`, `executed`, or `verified-working`. |
| `status` | Short status such as `passed`, `failed`, or `metadata-only`. |
| `checked_at` | Timezone-aware ISO 8601 timestamp of the check. Required for `verified-working`. |
| `valid_until` | Timezone-aware ISO 8601 expiry timestamp. Required for `verified-working` and must be later than `checked_at`. |
| `command` | Bounded command or manual check used as evidence. |
| `evidence_ref` | File, fixture id, transcript id, or report anchor. |
| `risk_boundary` | Explicit limits proven by this evidence. |

Run:

```bash
plugin/scripts/momo-tools evidence

# Evaluate evidence as of a reproducible point in time. This reports expired or invalid records but exits successfully unless --strict is supplied.
plugin/scripts/momo-tools freshness --as-of 2026-07-10T12:00:00+00:00
plugin/scripts/momo-tools evidence --as-of 2026-07-10T12:00:00+00:00 --strict
```

For a `verified-working` record, freshness keeps its effective level at
`verified-working` only while `valid_until` is after both `checked_at` and the
evaluation time. Expired, missing, malformed, or timezone-naive freshness
timestamps are reported as `expired` or `invalid` with an effective level of
`degraded`; the raw `level` remains visible for audit. `--strict` fails for
expired or invalid freshness evidence. Other validation errors retain their
normal failure behavior.

Visual fixture screenshots are available in the static demo:

```bash
python3 -m http.server 4173 --directory demo
```

Then open `http://127.0.0.1:4173`.

The public example evidence is synthetic. Do not publish private transcripts, customer data, local account names, hostnames, credentials, screenshots, or production evidence.
