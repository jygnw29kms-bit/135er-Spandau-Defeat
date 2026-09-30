#!/usr/bin/env bash
set -euo pipefail

STAGE=/var/www/vhosts/dezender.de/spandau-strike-typo3-staging
DB_NAME=spandau_strike
DB_USER=spandau_t3
DB_PASS_FILE="$STAGE/.db-password"

test -s "$DB_PASS_FILE"
DB_PASS="$(cat "$DB_PASS_FILE")"
MYSQL=(mysql -N -u "$DB_USER" -h localhost "$DB_NAME")
export MYSQL_PWD="$DB_PASS"
NOW="$(date +%s)"

sql() { "${MYSQL[@]}" -e "$1"; }
value() { sql "$1" | head -n1; }

ROOT_PID="$(value "SELECT uid FROM pages WHERE pid=0 AND deleted=0 ORDER BY uid LIMIT 1")"
test -n "$ROOT_PID"

ensure_page() {
  local parent="$1" title="$2" slug="$3" doktype="${4:-1}" fegroup="${5:-}"
  local uid
  uid="$(value "SELECT uid FROM pages WHERE pid=$parent AND slug='$slug' AND deleted=0 ORDER BY uid LIMIT 1")"
  local feSql="''"
  [ -n "$fegroup" ] && feSql="'$fegroup'"
  if [ -z "$uid" ]; then
    sql "INSERT INTO pages (pid,title,slug,doktype,hidden,deleted,tstamp,crdate,sorting,fe_group)
         VALUES ($parent,'$title','$slug',$doktype,0,0,$NOW,$NOW,256,$feSql)"
    uid="$(value "SELECT uid FROM pages WHERE pid=$parent AND slug='$slug' AND deleted=0 ORDER BY uid DESC LIMIT 1")"
  else
    sql "UPDATE pages SET title='$title', doktype=$doktype, fe_group=$feSql, hidden=0, tstamp=$NOW WHERE uid=$uid"
  fi
  printf '%s' "$uid"
}

ensure_content() {
  local pid="$1" ctype="$2" header="$3" body="${4:-}" sorting="${5:-256}" fegroup="${6:-}"
  local uid escBody feSql
  uid="$(value "SELECT uid FROM tt_content WHERE pid=$pid AND CType='$ctype' AND header='$header' AND deleted=0 ORDER BY uid LIMIT 1")"
  escBody="${body//\\/\\\\}"
  escBody="${escBody//\'/\'\'}"
  feSql="''"
  [ -n "$fegroup" ] && feSql="'$fegroup'"
  if [ -z "$uid" ]; then
    sql "INSERT INTO tt_content (pid,CType,colPos,sorting,header,bodytext,fe_group,hidden,deleted,tstamp,crdate)
         VALUES ($pid,'$ctype',0,$sorting,'$header','$escBody',$feSql,0,0,$NOW,$NOW)"
  else
    sql "UPDATE tt_content
         SET bodytext='$escBody', fe_group=$feSql, sorting=$sorting, hidden=0, tstamp=$NOW
         WHERE uid=$uid"
  fi
}

echo "=== COMMUNITY PAGE TREE ==="
STORAGE_PID="$(ensure_page "$ROOT_PID" "Community-Daten" "/community-daten" 254)"
LOGIN_PID="$(ensure_page "$ROOT_PID" "Anmelden" "/anmelden")"
REGISTER_PID="$(ensure_page "$ROOT_PID" "Registrieren" "/registrieren")"

GROUP_UID="$(value "SELECT uid FROM fe_groups WHERE pid=$STORAGE_PID AND title='135er Clan-Mitglied' AND deleted=0 ORDER BY uid LIMIT 1")"
if [ -z "$GROUP_UID" ]; then
  sql "INSERT INTO fe_groups (pid,title,description,hidden,deleted,tstamp,crdate)
       VALUES ($STORAGE_PID,'135er Clan-Mitglied','Freigeschaltete Mitglieder des 135er Spandau Strike Clans',0,0,$NOW,$NOW)"
  GROUP_UID="$(value "SELECT uid FROM fe_groups WHERE pid=$STORAGE_PID AND title='135er Clan-Mitglied' AND deleted=0 ORDER BY uid DESC LIMIT 1")"
fi

INTERN_PID="$(ensure_page "$ROOT_PID" "Clanbereich" "/intern")"
NEWS_PID="$(ensure_page "$INTERN_PID" "Clan-News" "/intern/news")"
ROSTER_PID="$(ensure_page "$INTERN_PID" "Mitglieder & Kader" "/intern/kader")"
DATES_PID="$(ensure_page "$INTERN_PID" "Termine & Matches" "/intern/termine")"
TRAINING_PID="$(ensure_page "$INTERN_PID" "Training" "/intern/training")"
TACTICS_PID="$(ensure_page "$INTERN_PID" "Taktiken & Downloads" "/intern/taktiken-downloads")"
SERVER_PID="$(ensure_page "$INTERN_PID" "Gameserver" "/intern/gameserver")"
STATS_PID="$(ensure_page "$INTERN_PID" "Playerstats" "/intern/playerstats")"
PROFILE_PID="$(ensure_page "$INTERN_PID" "Mein Profil" "/intern/profil")"

echo "=== AUTH CONTENT ==="
ensure_content "$LOGIN_PID" "felogin_login" "Clan-Login" "" 256
ensure_content "$REGISTER_PID" "femanager_registration" "Kiez-Mitglied werden" "" 256

# Public shells: guests see only the login form (-1 = hide at login);
# clan members see the protected content assigned to their FE group.
for pid in "$INTERN_PID" "$NEWS_PID" "$ROSTER_PID" "$DATES_PID" "$TRAINING_PID" "$TACTICS_PID" "$SERVER_PID" "$STATS_PID" "$PROFILE_PID"; do
  ensure_content "$pid" "felogin_login" "Clan-Login" "" 64 "-1"
done

ensure_content "$PROFILE_PID" "femanager_edit" "Mein Profil bearbeiten" "" 256 "$GROUP_UID"
ensure_content "$ROSTER_PID" "femanager_list" "Mitglieder & Kader" "" 256 "$GROUP_UID"

echo "=== MEMBER AREA CONTENT ==="
ensure_content "$INTERN_PID" "text" "Clanbereich" "Willkommen im internen Bereich. Hier findest du Clan-News, Kader, Termine, Training, Taktiken, Downloads, Gameserver, Playerstats und dein Profil." 256 "$GROUP_UID"
ensure_content "$NEWS_PID" "text" "Clan-News" "Hier erscheinen ausschließlich von Clan-Admins gepflegte interne Meldungen. Aktuell sind keine weiteren Meldungen eingetragen." 256 "$GROUP_UID"
ensure_content "$DATES_PID" "text" "Termine & Matches" "Hier werden Clan-Termine, Trainings und Matches gepflegt. Aktuell sind keine Termine eingetragen." 256 "$GROUP_UID"
ensure_content "$TRAINING_PID" "text" "Training" "Trainingspläne, Treffzeiten und Map-Schwerpunkte werden hier zentral gepflegt. Aktuell ist kein Training eingetragen." 256 "$GROUP_UID"
ensure_content "$TACTICS_PID" "text" "Taktiken & Downloads" "Geschützte Clan-Dokumente, Taktiken und Downloads werden hier als TYPO3-Inhalte bzw. Dateien verwaltet. Aktuell sind keine Dateien freigegeben." 256 "$GROUP_UID"
ensure_content "$SERVER_PID" "text" "Gameserver" "Der Bereich ist für die echte Gameserver-Anbindung vorbereitet. Es werden keine erfundenen Serverwerte angezeigt." 256 "$GROUP_UID"
ensure_content "$STATS_PID" "text" "Playerstats" "Der Bereich ist für die echte Playerstats-Anbindung vorbereitet. Es werden keine erfundenen Statistiken angezeigt." 256 "$GROUP_UID"

echo "=== TYPO3 CONSTANTS ==="
CONSTANTS="spandau.community.userStoragePid = $STORAGE_PID
spandau.community.userGroupUid = $GROUP_UID
spandau.community.loginRedirectPid = $INTERN_PID
spandau.community.logoutRedirectPid = $ROOT_PID"

sql "UPDATE sys_template
     SET constants='$(printf '%s' "$CONSTANTS" | sed "s/'/''/g")', tstamp=$NOW
     WHERE pid=$ROOT_PID AND deleted=0 AND title='135er Spandau Strike Root'"

php "$STAGE/vendor/bin/typo3" cache:flush || true

echo "COMMUNITY_READY=yes"
echo "STORAGE_PID=$STORAGE_PID"
echo "GROUP_UID=$GROUP_UID"
echo "LOGIN_PID=$LOGIN_PID"
echo "REGISTER_PID=$REGISTER_PID"
echo "INTERN_PID=$INTERN_PID"
echo "PROFILE_PID=$PROFILE_PID"
