# Risk Model

Risk tags tell the agent what kind of boundary a capability can cross.

| Risk | Meaning | Typical gate |
|---|---|---|
| `read-only` | Should not mutate state. | Still confirm scope. |
| `local-file` | Reads local project or document files. | Stay inside user-requested files. |
| `write` | Can create, edit, save, send, delete, archive, or persist. | Require explicit intent. |
| `private-data` | Can read account, customer, personal, or internal content. | Bound the query and minimize output. |
| `external-network` | Can browse or call external services. | Use only when current/external info is needed. |
| `credential` | Uses API keys, tokens, passwords, or secrets. | Use secure secret flow; never store in index. |
| `local-app` | Controls or inspects local apps or browser state. | Avoid unrelated profiles and logged-in content. |

## Prompt Conflict Examples

| User says | Gate behavior |
|---|---|
| "do not save" | `write` gate stays visible; save/capture capabilities should be blocked. |
| "do not browse" | `external-network` gate stays visible; browser/web capabilities need approval or fallback. |
| "draft but do not send" | email may be relevant, but send remains blocked. |
| "read-only" | write-capable workflows should not be used for persistence. |

## Design Rule

Risk tags are not punishments. They are friction where friction protects the
user.

