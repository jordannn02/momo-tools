#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
install_root="${MOMO_TOOLS_HOME:-$HOME/.momo-tools}"

mkdir -p "$install_root"
rm -rf "$install_root/plugin"
cp -R "$repo_root/plugin" "$install_root/plugin"
rm -rf "$install_root/tests" "$install_root/docs" "$install_root/examples"
cp -R "$repo_root/tests" "$install_root/tests"
cp -R "$repo_root/docs" "$install_root/docs"
cp -R "$repo_root/examples" "$install_root/examples"
cp "$repo_root/README.md" "$install_root/README.md"
cp "$repo_root/SECURITY.md" "$install_root/SECURITY.md"
cp "$repo_root/LICENSE" "$install_root/LICENSE"
mkdir -p "$install_root/bin"
ln -sf "$install_root/plugin/scripts/momo-tools" "$install_root/bin/momo-tools"
chmod +x "$install_root/plugin/scripts/momo-tools"

cat <<MSG
MoMo_tools installed locally.

CLI:
  $install_root/bin/momo-tools

Try:
  $install_root/bin/momo-tools dashboard
  $install_root/bin/momo-tools route --prompt "Read this PDF and do not save anything"

This installer does not modify agent config, shell startup files, credentials,
browser profiles, or plugin caches.
MSG
