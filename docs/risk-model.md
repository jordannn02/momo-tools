# Risk Model

Risk tags describe the boundary a capability can cross.

| Risk | Meaning | Typical gate |
|---|---|---|
| `read-only` | Should not mutate state. | Still confirm scope. |
| `local-file` | Reads local project or document files. | Stay inside user-requested files. |
| `write` | Can create, edit, save, send, delete, archive, or persist. | Require explicit intent. |
| `private-data` | Can read account, customer, personal, or internal content. | Bound the query and minimize output. |
| `external-network` | Can browse or call external services. | Use only when current or external info is needed. |
| `credential` | Uses API keys, tokens, passwords, or secrets. | Use secure secret flow; never store secrets in the index. |
| `local-app` | Controls or inspects local apps or browser state. | Avoid unrelated profiles and logged-in content. |

## Action Gates

Risk tags describe the capability. Action gates describe what the prompt is asking the agent to do.

| Action | Trigger examples | Boundary |
|---|---|---|
| `persist` | save, remember, capture, store | Requires a write path and no no-save conflict. |
| `send` | send, reply, message | Requires approval before external communication. |
| `delete` | delete, archive, remove, trash | Requires destructive-action confirmation. |
| `external-call` | latest, browse, website, online | Requires web or connector boundary. |
| `private-read` | inbox, customer, client, account | Requires bounded private-data scope. |
| `credential-use` | token, API key, password, secret | Requires secure secret handling. |

`route` returns both `gates` and `actions`. A capability can be relevant while still blocked by a user instruction such as "do not save" or "no web".

## Prompt Conflict Examples

| User says | Gate behavior |
|---|---|
| "do not save" | `write` gate stays visible; save/capture capabilities should be blocked. |
| "do not browse" | `external-network` gate stays visible; browser/web capabilities need approval fallback. |
| "draft but do not send" | Email may be relevant, but send remains blocked. |
| "read-only" | Write-capable workflows should not use persistence. |

## Design Rule

Risk tags are not punishments. They add friction where friction protects the user.

