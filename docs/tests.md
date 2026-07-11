# Tests

MoMo_tools uses dependency-free smoke tests so the public repository can run in GitHub Actions without private tools.

| Command | What it checks |
|---|---|
| `validate` | Required fields, duplicate names, list fields, and verification level values. |
| `dashboard` | Verification level counts, risk counts, and validation health. |
| `audit` | Core routing fixture in `tests/fixtures/route-cases.json`. |
| `benchmark` | Broader starter routing fixture in `tests/fixtures/routing-benchmark.json`. |
| `evidence` | JSONL verification evidence shape in `evidence/example-verification.jsonl`. |
| `freshness --strict` | Requires valid, timezone-aware, unexpired `verified-working` evidence at `--as-of`. |
| `pressure` | Conflict prompts keep risk gates visible and block unsafe persistence. |
| source `integrity --installed-root PATH --strict` | SHA-256 comparison of a fixed public manifest against an independent installed copy; strict mode rejects omitted/canonical roots, per-artifact aliases, non-regular files, and artifact read failures. |
| source `recovery-drill --strict` | Temporary-only corruption and restore proof with canonical source bytes unchanged. |
| source `slo --installed-root PATH --strict` | One public release-health result covering P1 freshness and P2 integrity/recovery alongside routing checks; strict mode rejects an omitted root or the canonical source tree. |
| source `doctor --installed-root PATH --strict` | Public-only aggregate diagnostics; confirms read-only/no-execution/no-external/no-write boundaries and skips recovery. |
| source `repair-plan --dry-run --installed-root PATH --strict` | Deterministic advisory/blocked plan with no apply mode and zero write operations. |
| `scripts/build-release-snapshot.sh --ref REF` | Builds a committed Git ref reproducibly and emits archive, checksum, and exact-commit manifest evidence. |
| `test` | Validation, audit, benchmark, and pressure in one command. |

Run everything locally:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
plugin/scripts/momo-tools test
plugin/scripts/momo-tools freshness --as-of 2026-07-10T12:00:00+00:00 --strict
MOMO_TOOLS_HOME=/tmp/momo-tools-public-install-test scripts/install-local.sh
/tmp/momo-tools-public-install-test/bin/momo-tools test
plugin/scripts/momo-tools integrity --installed-root /tmp/momo-tools-public-install-test --strict
plugin/scripts/momo-tools recovery-drill --strict
plugin/scripts/momo-tools slo --as-of 2026-07-10T12:00:00+00:00 --installed-root /tmp/momo-tools-public-install-test --strict
plugin/scripts/momo-tools doctor --as-of 2026-07-10T12:00:00+00:00 --installed-root /tmp/momo-tools-public-install-test --strict
plugin/scripts/momo-tools repair-plan --dry-run --as-of 2026-07-10T12:00:00+00:00 --installed-root /tmp/momo-tools-public-install-test --strict
scripts/build-release-snapshot.sh --ref HEAD --output-dir /tmp/momo-tools-public-release
plugin/scripts/momo-tools --index plugin/capabilities.example.yaml validate
```

CI smoke-tests a temporary installed binary, runs the strict trust comparison, doctor, and dry-run repair contracts, and builds the exact commit twice to prove byte-reproducible release outputs. The extracted snapshot repeats those checks. Contract tests cover no-follow artifact inspection, root/nested/final symlink rejection, non-blocking FIFO handling, post-hash pathname and metadata stability, failed-evidence handling, malformed/empty fixture rejection, canonical repair proof, deterministic finding/action mapping, version consistency, release snapshot provenance, and a tracked-file private-context scan that neither echoes matched content nor treats a `git grep` error as clean.

## Known Limits

| Gap | Risk |
|---|---|
| Router scoring is simple keyword matching. | It can miss semantic matches. Add benchmark cases for failures. |
| JSON Schema is provided but not used as a runtime dependency. | The CLI remains dependency-free; use schema-aware IDE or pre-commit tools for deeper validation. |
| Public evidence is synthetic. | It proves format and routing behavior, not private runtime access. |
| Integrity only compares the supplied public copy. | It does not protect, repair, or monitor a user's real installation. |
| Recovery drill uses a temporary workspace. | It proves the exercise, not recovery of a user's files. |
| Doctor reads only explicit public inputs. | It does not inspect a private registry, home directory, cache, connector, or real production environment. |
| Repair plan has no apply mode. | It can recommend a separately authorized action but cannot repair files itself. |
| No package manager metadata yet. | Users run from source or local installer. |
