# Verification Levels

MoMo_tools separates "I can see this capability" from "this capability works".

| Level | Meaning | Promotion requirement |
|---|---|---|
| `visible` | Registered and discoverable. | Metadata is valid. |
| `executed` | Ran once on a bounded task. | Inspectable result or transcript. |
| `verified-working` | Repeatable verification exists. | Evidence, repeatable check, and risk boundary. |

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

## Public Package Rule

The public sample index is mostly `visible` by design. Users should promote
their own capabilities only after local evidence exists.

