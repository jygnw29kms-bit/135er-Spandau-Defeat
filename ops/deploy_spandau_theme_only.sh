#!/usr/bin/env bash
set -euo pipefail

ROOT=/var/www/vhosts/dezender.de
STAGE="$ROOT/spandau-strike-typo3-staging"
LIVE="$ROOT/httpdocs/135erSpandauStrike"

test -x "$STAGE/vendor/bin/typo3"
test -d "$STAGE/packages"

rm -rf /tmp/135er-Spandau-Defeat-theme
git clone --depth 1 https://github.com/jygnw29kms-bit/135er-Spandau-Defeat.git /tmp/135er-Spandau-Defeat-theme

SRC=/tmp/135er-Spandau-Defeat-theme/typo3/spandau_sitepackage
DST="$STAGE/packages/spandau_sitepackage"
test -f "$SRC/Resources/Private/Templates/Page.html"

OWNER="$(stat -c %U "$ROOT/httpdocs")"
GROUP="$(stat -c %G "$ROOT/httpdocs")"

rm -rf "$DST.new"
cp -a "$SRC" "$DST.new"
chown -R "$OWNER:$GROUP" "$DST.new"

if [ -d "$DST" ]; then
  rm -rf "$DST.prev"
  mv "$DST" "$DST.prev"
fi
mv "$DST.new" "$DST"

php "$STAGE/vendor/bin/typo3" cache:flush

curl -LfsS --retry 4 --retry-delay 2 "https://www.dezender.de/135erSpandauStrike/" -o /tmp/spandau-theme-live.html

if ! grep -q "Rathaus Spandau // aktueller Stand" /tmp/spandau-theme-live.html; then
  rm -rf "$DST"
  if [ -d "$DST.prev" ]; then mv "$DST.prev" "$DST"; fi
  php "$STAGE/vendor/bin/typo3" cache:flush || true
  echo "Current Rathaus marker missing; rollback completed." >&2
  exit 31
fi

grep -q "WORLD_MASTER v51" /tmp/spandau-theme-live.html
grep -q "FIRST_PLAY v72" /tmp/spandau-theme-live.html

echo "SPANDAU_RATHAUS_CURRENT_LIVE=yes"
