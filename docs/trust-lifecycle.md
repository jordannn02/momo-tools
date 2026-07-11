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

The report includes the manifest, missing files, mismatched files, per-artifact aliases, read/type failures, and whether an installed copy was checked. Run this strict comparison from a source checkout: an installed binary's own root resolves to that binary's canonical source plugin and is intentionally rejected. In strict mode, an omitted installed root, a supplied root that resolves to the canonical source plugin or repository tree, any symlink (including one targeting an independent equal-byte file), a hardlink alias, a non-regular artifact such as a FIFO or device, missing artifacts, mismatched artifacts, or a source/installed read error fails the command. Inspection runs `lstat` first, opens with `O_NOFOLLOW`, `O_NONBLOCK`, and `O_CLOEXEC` when available, requires a regular file, compares the pre-open and descriptor identity, hashes through that descriptor, then verifies device, inode, size, and modification time remained stable. The source-tree rejection uses `installed_root_is_canonical_source`; an omitted root uses `installed_root_required`; the additive report fields `source_aliases`, `source_read_errors`, and `installed_read_errors` preserve machine-readable details for the remaining failures.

## Doctor

`doctor` aggregates only public inputs named by the CLI: the public index, routing cases, benchmark cases, synthetic evidence, and an optional installed-copy root.

```bash
plugin/scripts/momo-tools doctor \
  --as-of 2026-07-10T12:00:00+00:00 \
  --installed-root /tmp/momo-tools-public-install-test \
  --strict
```

The JSON report has stable `ok`, `degraded`, and `failed` health states. Expired or invalid verification evidence degrades health; validation, routing, probe, or integrity failures fail health. Non-strict mode remains diagnostic and exits zero after producing a report. Strict mode requires an independent installed copy and exits nonzero unless health is `ok`.

`doctor` is read-only. Its report explicitly records `capability_execution=false`, `external_calls=false`, `network_calls=false`, `browser_calls=false`, `connector_calls=false`, and `write_scope=none`. It does not invoke the recovery drill, discover a private index, scan a home/cache directory, or execute a registered capability.

## Repair Plan

```bash
plugin/scripts/momo-tools repair-plan \
  --dry-run \
  --as-of 2026-07-10T12:00:00+00:00 \
  --installed-root /tmp/momo-tools-public-install-test \
  --strict
```

`repair-plan` requires `--dry-run` and has no apply mode. Every validated doctor finding maps to one deterministic action. Unknown, unsafe, aliased, unstable, missing-proof, probe, or inconsistent-report findings are blocked by default. Expired evidence can only recommend rerunning a bounded verification; it cannot extend validity or promote a verification level. Installed mismatch advice requires an allowlisted public relative path, canonical SHA-256, and an explicitly named installed root. Every action remains `auto_applicable=false`, requires separate explicit authorization, and the report always records `applied=false` and `write_operations_executed=0`.

Diagnostic repair-plan mode exits zero after printing the plan. `--strict` exits nonzero when doctor health is not `ok` or any plan action is blocked, making it suitable for CI without adding write authority.

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

`slo` combines validation, routing audit, benchmark, pressure checks, P1 evidence freshness, integrity, and the temporary recovery drill into one JSON report. Run strict `slo` from a source checkout so it compares the source manifest against the independent install. It labels the result as `public_scope` and explicitly records that a real installation is not protected. `doctor` is intentionally separate because it does not execute the recovery drill.

Use a fixed `--as-of` only with the synthetic fixture for reproducible public CI. A real release process must provide evidence whose validity window is appropriate for its own release decision.
