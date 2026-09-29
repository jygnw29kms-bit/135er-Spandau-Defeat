#!/usr/bin/env bash
set -euo pipefail

ROOT=/var/www/vhosts/dezender.de
LIVE="$ROOT/httpdocs/135erSpandauStrike"
STAGE="$ROOT/spandau-strike-typo3-staging"
DB_NAME=spandau_strike
DB_USER=spandau_t3
DB_PASS_FILE="$STAGE/.db-password"
ADMIN_PASS_FILE="$STAGE/.admin-password"

test -f "$STAGE/vendor/bin/typo3"
test -f "$STAGE/public/index.php"

rm -rf /tmp/135er-Spandau-Defeat
git clone --depth 1 https://github.com/jygnw29kms-bit/135er-Spandau-Defeat.git /tmp/135er-Spandau-Defeat
rm -rf "$STAGE/packages/spandau_sitepackage"
cp -a /tmp/135er-Spandau-Defeat/typo3/spandau_sitepackage "$STAGE/packages/spandau_sitepackage"

cd "$STAGE"
COMPOSER_ALLOW_SUPERUSER=1 composer update dezender/spandau-sitepackage in2code/femanager --with-all-dependencies --no-interaction

umask 077
if [ ! -s "$DB_PASS_FILE" ]; then
  tr -dc A-Za-z0-9 </dev/urandom | head -c 36 > "$DB_PASS_FILE"
fi
if [ ! -s "$ADMIN_PASS_FILE" ]; then
  tr -dc A-Za-z0-9 </dev/urandom | head -c 36 > "$ADMIN_PASS_FILE"
fi
DB_PASS="$(cat "$DB_PASS_FILE")"
ADMIN_PASS="$(cat "$ADMIN_PASS_FILE")"

plesk bin database --info "$DB_NAME" >/dev/null 2>&1 ||   plesk bin database --create "$DB_NAME" -domain dezender.de -type mysql

if ! plesk bin database --create-dbuser "$DB_USER" -passwd "$DB_PASS"   -domain dezender.de -server localhost:3306 -database "$DB_NAME" >/dev/null 2>&1; then
  plesk bin database --update-dbuser "$DB_USER" -passwd "$DB_PASS"     -server localhost:3306 >/dev/null
fi

if [ ! -f "$STAGE/config/system/settings.php" ]; then
  TYPO3_DB_DRIVER=mysqli   TYPO3_DB_USERNAME="$DB_USER"   TYPO3_DB_PASSWORD="$DB_PASS"   TYPO3_DB_PORT=3306   TYPO3_DB_HOST=localhost   TYPO3_DB_DBNAME="$DB_NAME"   TYPO3_SETUP_ADMIN_EMAIL=admin@dezender.de   TYPO3_SETUP_ADMIN_USERNAME=spandauadmin   TYPO3_SETUP_ADMIN_PASSWORD="$ADMIN_PASS"   TYPO3_SETUP_CREATE_SITE="https://www.dezender.de/135erSpandauStrike/"   TYPO3_PROJECT_NAME="135er - Spandau Strike"   TYPO3_SERVER_TYPE=apache   php "$STAGE/vendor/bin/typo3" setup --force --no-interaction
fi

php "$STAGE/vendor/bin/typo3" extension:setup
php "$STAGE/vendor/bin/typo3" cache:flush || true

ROOT_PID="$(MYSQL_PWD="$DB_PASS" mysql -N -u "$DB_USER" -h localhost "$DB_NAME"   -e "SELECT uid FROM pages WHERE pid=0 AND deleted=0 ORDER BY uid LIMIT 1")"
test -n "$ROOT_PID"

TEMPLATE_COUNT="$(MYSQL_PWD="$DB_PASS" mysql -N -u "$DB_USER" -h localhost "$DB_NAME"   -e "SELECT COUNT(*) FROM sys_template WHERE pid=$ROOT_PID AND deleted=0 AND title=\"135er Spandau Strike Root\"")"

if [ "$TEMPLATE_COUNT" = "0" ]; then
  NOW="$(date +%s)"
  MYSQL_PWD="$DB_PASS" mysql -u "$DB_USER" -h localhost "$DB_NAME" -e   "INSERT INTO sys_template (pid,title,root,clear,include_static_file,tstamp,crdate,sorting,deleted,hidden)
   VALUES ($ROOT_PID,\"135er Spandau Strike Root\",1,3,
   \"EXT:fluid_styled_content/Configuration/TypoScript/,EXT:spandau_sitepackage/Configuration/TypoScript/\",
   $NOW,$NOW,256,0,0)"
fi

php "$STAGE/vendor/bin/typo3" cache:flush || true

TS="$(date +%Y%m%d-%H%M%S)"
PREV="$ROOT/httpdocs/135erSpandauStrike-static-$TS"

if [ -L "$LIVE" ]; then
  rm -f "$LIVE"
elif [ -d "$LIVE" ]; then
  mv "$LIVE" "$PREV"
fi

ln -s ../spandau-strike-typo3-staging/public "$LIVE"

OWNER="$(stat -c %U "$ROOT/httpdocs")"
GROUP="$(stat -c %G "$ROOT/httpdocs")"
chown -R "$OWNER:$GROUP" "$STAGE"
chmod 600 "$DB_PASS_FILE" "$ADMIN_PASS_FILE"

ok=0
for i in 1 2 3 4 5 6; do
  if curl -LfsS "https://www.dezender.de/135erSpandauStrike/" -o /tmp/spandau-live.html     && grep -q "Spandau Strike" /tmp/spandau-live.html; then
    ok=1
    break
  fi
  sleep 3
done

if [ "$ok" != "1" ]; then
  rm -f "$LIVE"
  if [ -d "$PREV" ]; then mv "$PREV" "$LIVE"; fi
  echo "Live verification failed; rollback completed." >&2
  exit 23
fi

echo "TYPO3_LIVE=yes"
php "$STAGE/vendor/bin/typo3" --version | head -1
echo "ROOT_PID=$ROOT_PID"
echo "BACKEND_USER=spandauadmin"
echo "ADMIN_PASSWORD_FILE=$ADMIN_PASS_FILE"
