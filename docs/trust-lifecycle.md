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

The report includes the manifest, missing files, mismatched files, per-artifact aliases, read/type failures, and whether an installed copy was checked. Run this strict comparison from a source checkout: an installed binary's own root resolves to that binary's canonical source plugin and is intentionally rejected. In strict mode, an omitted installed root, a supplied root that resolves to the canonical source plugin or repository tree, a symlink or hardlink alias for any manifest artifact, a non-regular artifact such as a FIFO or device, missing artifacts, mismatched artifacts, or a source/installed read error fails the command. Artifacts are opened non-blockingly, checked as regular files, identified, and hashed through the same file descriptors. The source-tree rejection uses `installed_root_is_canonical_source`; an omitted root uses `installed_root_required`; the additive report fields `source_aliases`, `source_read_errors`, and `installed_read_errors` preserve machine-readable details for the remaining failures.

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
