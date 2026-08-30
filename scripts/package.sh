#!/usr/bin/env bash
# Builds the distributable layout from the Release build output.
# Usage: scripts/package.sh <version-label> [build-output] [package-dir] [zip-path]
# Produces AstraSkins-<version-label>.zip containing the addons/ tree.
set -euo pipefail

VERSION="${1:?version label required}"
OUT="${2:-src/AstraSkins/bin/Release/net10.0}"
PACKAGE_DIR="${3:-package}"
PKG="$PACKAGE_DIR/addons/counterstrikesharp"
PLUG="$PKG/plugins/AstraSkins"

rm -rf "$PACKAGE_DIR"
mkdir -p "$PLUG" "$PKG/gamedata" "$PKG/configs/plugins/AstraSkins"

# Plugin binaries: only the plugin itself and its own dependencies.
# CounterStrikeSharp.API and everything it pulls in is provided by the runtime.
cp "$OUT/AstraSkins.dll" "$OUT/AstraSkins.deps.json" \
   "$OUT/Microsoft.Data.Sqlite.dll" "$OUT/MySqlConnector.dll" \
   "$OUT"/SQLitePCLRaw.*.dll "$PLUG/"
cp -r "$OUT/data" "$OUT/lang" "$OUT/schema" "$PLUG/"

# Native SQLite for the two platforms CS2 dedicated servers run on.
for rid in win-x64 linux-x64; do
  mkdir -p "$PLUG/runtimes/$rid"
  cp -r "$OUT/runtimes/$rid/." "$PLUG/runtimes/$rid/"
done

cp gamedata/astra_skins.json "$PKG/gamedata/"
cp config.json "$PKG/configs/plugins/AstraSkins/AstraSkins.json"

ZIP_INPUT="${4:-AstraSkins-${VERSION}.zip}"
ZIP="$ZIP_INPUT"
case "$ZIP" in
  /*|[A-Za-z]:/*) ;;
  *) ZIP="$(pwd)/$ZIP" ;;
esac
mkdir -p "$(dirname "$ZIP")"
rm -f "$ZIP"
(cd "$PACKAGE_DIR" && zip -qr "$ZIP" addons)
echo "$ZIP_INPUT"
