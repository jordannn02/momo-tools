# Schemas

`capabilities.schema.json` describes the public capability index shape. It is meant for IDE validation, pre-commit checks, and CI syntax checks.

The CLI still performs the authoritative dependency-free validation:

```bash
plugin/scripts/momo-tools validate
plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate
```

Supported index formats:

| Format | Support |
|---|---|
| JSON | Full public example support. |
| YAML | Dependency-free support for the simple list-of-capability-records shape used by this repository. |

The YAML loader is intentionally small. If your index needs anchors, nested maps, multiline strings, or advanced YAML features, convert it to JSON before using this public CLI.

