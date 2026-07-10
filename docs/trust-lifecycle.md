# Public Trust Lifecycle

The public trust lifecycle is a local, dependency-free release check. It evaluates only the canonical public package, synthetic evidence, and an installed copy explicitly named by the caller.

It never calls a network, browser, connector, account, or private service.

## Integrity

`integrity` uses SHA-256 for this fixed public manifest:

- `.codex-plugin/plugin.json`
- `capabilities.example.json`
- `capabilities.example.yaml`
- `scripts/momo-tools`
- `skills/momo-tools/SKILL.md`

Non-strict source-only validation is available for local development:

```bash
plugin/scripts/momo-tools integrity
```

Strict integrity requires an explicit installed copy. Create a temporary public install, smoke-test the installed binary, then run the comparator from the source checkout:

```bash
MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test scripts/install-local.sh
/tmp/momo-tools-public-install-test/bin/momo-tools test
plugin/scripts/momo-tools integrity --installed-root /tmp/momo-tools-public-install-test --strict
```

The report includes the manifest, missing files, mismatched files, and whether an installed copy was checked. Run this strict comparison from a source checkout: an installed binary's own root resolves to that binary's canonical source plugin and is intentionally rejected. In strict mode, an omitted installed root, a supplied root that resolves to the canonical source plugin or repository tree, missing artifacts, or mismatched artifacts fail the command. The source-tree rejection uses the public-safe error `installed_root_is_canonical_source`; an omitted root uses `installed_root_required`.

## Recovery Drill

Run the recovery drill from the source checkout:

```bash
plugin/scripts/momo-tools recovery-drill --strict
```

The drill makes a temporary workspace, copies one public artifact there, simulates corruption, restores the temporary copy, and checks that the canonical source bytes did not change. Its report always includes:

- `temporary_only`
- `source_unchanged`
- `passed`

Strict mode requires all three conditions. This is a drill for the public source package only. It does not touch, repair, back up, or prove protection for a user's real installation.

## Release Health

```bash
MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test scripts/install-local.sh
/tmp/momo-tools-public-install-test/bin/momo-tools test
plugin/scripts/momo-tools slo \
  --as-of 2026-07-10T12:00:00+00:00 \
  --installed-root /tmp/momo-tools-public-install-test \
  --strict
```

`slo` combines validation, routing audit, benchmark, pressure checks, P1 evidence freshness, integrity, and the temporary recovery drill into one JSON report. Run strict `slo` from a source checkout so it compares the source manifest against the independent install. It labels the result as `public_scope` and explicitly records that a real installation is not protected.

Use a fixed `--as-of` only with the synthetic fixture for reproducible public CI. A real release process must provide evidence whose validity window is appropriate for its own release decision.
