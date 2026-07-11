#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$script_dir/.." rev-parse --show-toplevel)"
ref="HEAD"
output_dir="$repo_root/dist"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref)
      ref="${2:?--ref requires a git ref}"
      shift 2
      ;;
    --output-dir)
      output_dir="${2:?--output-dir requires a path}"
      shift 2
      ;;
    -h|--help)
      echo "Usage: scripts/build-release-snapshot.sh [--ref GIT_REF] [--output-dir PATH]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

commit_sha="$(git -C "$repo_root" rev-parse "${ref}^{commit}")"
version="$(git -C "$repo_root" show "$commit_sha:VERSION" | tr -d '\r\n')"
if [[ ! "$version" =~ ^[0-9A-Za-z][0-9A-Za-z._+-]*$ ]]; then
  echo "Invalid release version in $commit_sha:VERSION" >&2
  exit 1
fi

plugin_version="$({
  git -C "$repo_root" show "$commit_sha:plugin/.codex-plugin/plugin.json"
} | python3 -c 'import json, sys; print(json.load(sys.stdin)["version"])')"
json_version="$({
  git -C "$repo_root" show "$commit_sha:plugin/capabilities.example.json"
} | python3 -c 'import json, sys; print(json.load(sys.stdin)[0]["version"])')"
yaml_version="$({
  git -C "$repo_root" show "$commit_sha:plugin/capabilities.example.yaml"
} | python3 -c 'import re, sys; text=sys.stdin.read(); match=re.search(r"(?m)^\s*version:\s*[\"'"'"']?([^\s\"'"'"']+)", text); print(match.group(1) if match else "")')"
release_notes_version="$({
  git -C "$repo_root" show "$commit_sha:RELEASE_NOTES.md"
} | python3 -c 'import re, sys; text=sys.stdin.read(); match=re.search(r"(?m)^## v([^\s]+)", text); print(match.group(1) if match else "")')"
if [[ "$plugin_version" != "$version" || \
      "$json_version" != "$version" || \
      "$yaml_version" != "$version" || \
      "$release_notes_version" != "$version" ]]; then
  echo "Version mismatch: VERSION=$version plugin=$plugin_version json=$json_version yaml=$yaml_version release_notes=$release_notes_version" >&2
  exit 1
fi

tag="v$version"
archive_base="momo-tools-$tag"
archive_name="$archive_base.tar.gz"
archive_path="$output_dir/$archive_name"
checksum_path="$archive_path.sha256"
manifest_path="$output_dir/$archive_base.snapshot.json"
mkdir -p "$output_dir"

temporary_root="${TMPDIR:-/tmp}"
if [[ ! -d "$temporary_root" ]]; then
  temporary_root="/tmp"
fi
temporary_tar="$(mktemp "${temporary_root%/}/momo-tools-release.XXXXXX")"
trap 'rm -f "$temporary_tar"' EXIT

git -C "$repo_root" archive \
  --format=tar \
  --prefix="$archive_base/" \
  "$commit_sha" > "$temporary_tar"
gzip -n -9 -c "$temporary_tar" > "$archive_path"

digest="$(python3 - "$archive_path" <<'PY'
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
digest = hashlib.sha256()
with path.open("rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
print(digest.hexdigest())
PY
)"
printf '%s  %s\n' "$digest" "$archive_name" > "$checksum_path"

python3 - "$manifest_path" "$version" "$tag" "$commit_sha" "$archive_name" "$digest" <<'PY'
import json
import sys
from pathlib import Path

manifest_path, version, tag, commit_sha, archive_name, digest = sys.argv[1:]
report = {
    "schema": "release-snapshot/v1",
    "version": version,
    "tag": tag,
    "commit_sha": commit_sha,
    "archive": archive_name,
    "sha256": digest,
    "source": "git-archive",
    "reproducible": True,
}
Path(manifest_path).write_text(
    json.dumps(report, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

echo "release_snapshot: $archive_path"
echo "release_checksum: $checksum_path"
echo "release_manifest: $manifest_path"
