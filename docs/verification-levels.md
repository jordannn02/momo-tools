# Verification Levels

MoMo_tools separates "I can see this capability" from "this capability works".

| Level | Meaning | Promotion requirement |
|---|---|---|
| `visible` | Registered and discoverable. | Metadata is valid. |
| `executed` | Ran once on a bounded task. | Inspectable result or transcript. |
| `verified-working` | Repeatable verification exists and remains current. | Evidence, repeatable check, risk boundary, and timezone-aware `checked_at` / `valid_until` where `valid_until > checked_at`. |

## Why This Matters

Installed tools often fail for ordinary reasons:

- missing login;
- stale path;
- changed plugin manifest;
- unavailable runtime;
- insufficient permission;
- unsafe or unclear side effects.

`visible` is useful because it allows routing. It is not proof.

## Suggested Evidence Fields

For `executed`:

- timestamp;
- runner;
- command or tool;
- task summary;
- outcome;
- evidence path or reference;
- risk boundary.

For `verified-working`, also include:

- repeatable check;
- postcheck;
- caveats.
- timezone-aware `checked_at` and `valid_until` timestamps.

## Freshness

`plugin/scripts/momo-tools freshness` evaluates evidence at the current time or
at a supplied timezone-aware `--as-of` timestamp. A current record retains the
effective level `verified-working`. Expired evidence and invalid freshness
timestamps, including date-only and timezone-naive timestamps, are degraded
while retaining their raw declared level in the report. Use `--strict` to make
expired or invalid freshness evidence fail the command; non-strict summaries
remain inspectable for audit and cleanup.

## Public Package Rule

The public sample index is mostly `visible` by design. Users should promote
their own capabilities only after local evidence exists.
