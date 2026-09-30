#!/usr/bin/env bash
set -eu

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

echo "=== CREDENTIAL FILES ==="
umask 077
if [ ! -s "$DB_PASS_FILE" ]; then
  php -r 'echo bin2hex(random_bytes(18));' > "$DB_PASS_FILE"
fi
if [ ! -s "$ADMIN_PASS_FILE" ]; then
  printf '%s' "$(php -r 'echo bin2hex(random_bytes(18));')Aa1!" > "$ADMIN_PASS_FILE"
fi
DB_PASS="$(cat "$DB_PASS_FILE")"
ADMIN_PASS="$(cat "$ADMIN_PASS_FILE")"
if [ ! -f "$STAGE/config/system/settings.php" ] && [[ "$ADMIN_PASS" != *"!" ]]; then
  ADMIN_PASS="${ADMIN_PASS}Aa1!"
  printf '%s' "$ADMIN_PASS" > "$ADMIN_PASS_FILE"
fi

echo "=== PLESK DATABASE ==="
plesk bin database --create "$DB_NAME" -domain dezender.de -type mysql >/dev/null 2>&1 || true

if ! plesk bin database --create-dbuser "$DB_USER" -passwd "$DB_PASS"   -domain dezender.de -server localhost:3306 -database "$DB_NAME" >/dev/null 2>&1; then
  plesk bin database --update-dbuser "$DB_USER" -passwd "$DB_PASS"     -server localhost:3306 >/dev/null
fi

echo "=== TYPO3 SETUP ==="
if [ ! -f "$STAGE/config/system/settings.php" ]; then
  TYPO3_DB_DRIVER=mysqli   TYPO3_DB_USERNAME="$DB_USER"   TYPO3_DB_PASSWORD="$DB_PASS"   TYPO3_DB_PORT=3306   TYPO3_DB_HOST=localhost   TYPO3_DB_DBNAME="$DB_NAME"   TYPO3_SETUP_ADMIN_EMAIL=admin@dezender.de   TYPO3_SETUP_ADMIN_USERNAME=spandauadmin   TYPO3_SETUP_ADMIN_PASSWORD="$ADMIN_PASS"   TYPO3_SETUP_CREATE_SITE="https://www.dezender.de/135erSpandauStrike/"   TYPO3_PROJECT_NAME="135er - Spandau Strike"   TYPO3_SERVER_TYPE=apache   php "$STAGE/vendor/bin/typo3" setup --force --no-interaction
fi

echo "=== EXTENSION SETUP ==="
php "$STAGE/vendor/bin/typo3" extension:setup
php "$STAGE/vendor/bin/typo3" cache:flush || true

ROOT_PID="$(MYSQL_PWD="$DB_PASS" mysql -N -u "$DB_USER" -h localhost "$DB_NAME" -e "SELECT uid FROM pages WHERE pid=0 AND deleted=0 ORDER BY uid LIMIT 1")"

if [ -z "$ROOT_PID" ]; then
  NOW="$(date +%s)"
  MYSQL_PWD="$DB_PASS" mysql -u "$DB_USER" -h localhost "$DB_NAME" -e "
    INSERT INTO pages
      (pid, title, slug, doktype, is_siteroot, hidden, deleted, tstamp, crdate, sorting)
    VALUES
      (0, '135er - Spandau Strike', '/', 1, 1, 0, 0, $NOW, $NOW, 256);
  "
  ROOT_PID="$(MYSQL_PWD="$DB_PASS" mysql -N -u "$DB_USER" -h localhost "$DB_NAME" -e "SELECT uid FROM pages WHERE pid=0 AND deleted=0 ORDER BY uid LIMIT 1")"
fi

test -n "$ROOT_PID"

mkdir -p "$STAGE/config/sites/spandau-strike"
cat > "$STAGE/config/sites/spandau-strike/config.yaml" <<EOF
base: 'https://www.dezender.de/135erSpandauStrike/'
baseVariants: {  }
errorHandling: {  }
languages:
  -
    title: Deutsch
    enabled: true
    languageId: 0
    base: /
    locale: de_DE.UTF-8
    navigationTitle: Deutsch
    flag: de
    hreflang: de-DE
rootPageId: $ROOT_PID
routes: {  }
websiteTitle: '135er - Spandau Strike'
EOF

TEMPLATE_COUNT="$(MYSQL_PWD="$DB_PASS" mysql -N -u "$DB_USER" -h localhost "$DB_NAME" -e "SELECT COUNT(*) FROM sys_template WHERE pid=$ROOT_PID AND deleted=0 AND title=\"135er Spandau Strike Root\"")"

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
PUBLISH="$ROOT/httpdocs/135erSpandauStrike.next"

OWNER="$(stat -c %U "$ROOT/httpdocs")"
GROUP="$(stat -c %G "$ROOT/httpdocs")"
chown -R "$OWNER:$GROUP" "$STAGE"
chmod 600 "$DB_PASS_FILE" "$ADMIN_PASS_FILE"

rm -rf "$PUBLISH"
mkdir -p "$PUBLISH"
cp -a "$STAGE/public/." "$PUBLISH/"
chown -R "$OWNER:$GROUP" "$PUBLISH"
find "$PUBLISH" -type d -exec chmod 0755 {} +
find "$PUBLISH" -type f -exec chmod 0644 {} +

cat > "$PUBLISH/index.php" <<'PHP'
<?php
require __DIR__ . '/../../../spandau-strike-typo3-staging/public/index.php';
PHP

if [ -f "$STAGE/public/.htaccess" ]; then
  cp "$STAGE/public/.htaccess" "$PUBLISH/.htaccess"
fi

if [ -L "$LIVE" ]; then
  rm -f "$LIVE"
elif [ -d "$LIVE" ]; then
  mv "$LIVE" "$PREV"
fi

mv "$PUBLISH" "$LIVE"

ok=0
for i in 1 2 3 4 5 6; do
  if curl -LfsS "https://www.dezender.de/135erSpandauStrike/" -o /tmp/spandau-live.html     && grep -q "Spandau Strike" /tmp/spandau-live.html; then
    ok=1
    break
  fi
  sleep 3
done

if [ "$ok" != "1" ]; then
  echo "=== TYPO3 LOGS ===" >&2
  find "$STAGE/var/log" -maxdepth 1 -type f -name "*.log" -print -exec tail -n 120 {} \; 2>/dev/null >&2 || true
  echo "=== PHP / WEB LOGS ===" >&2
  for log in     "$ROOT/logs/proxy_error_log"     "$ROOT/logs/error_log"     "$ROOT/logs/php_error.log"     /var/log/apache2/error.log     /var/log/nginx/error.log
  do
    if [ -f "$log" ]; then
      echo "--- $log ---" >&2
      tail -n 160 "$log" >&2 || true
    fi
  done
  rm -rf "$LIVE"
  if [ -d "$PREV" ]; then mv "$PREV" "$LIVE"; fi
  echo "Live verification failed; rollback completed." >&2
  exit 23
fi

echo "TYPO3_LIVE=yes"
php "$STAGE/vendor/bin/typo3" --version
echo "ROOT_PID=$ROOT_PID"
echo "BACKEND_USER=spandauadmin"
echo "ADMIN_PASSWORD_FILE=$ADMIN_PASS_FILE"
