#!/usr/bin/env bash
set -euo pipefail

echo "starting stack..."
docker compose up -d

NEXTC=$(docker compose ps -q nextcloud)

echo "waiting for /status.php (installed:true)..."
until curl -fsS http://localhost:8080/status.php | grep -q '"installed":true'; do
  sleep 3
done


echo "configuring Nextcloud..."
docker exec --user www-data "$NEXTC" php occ config:system:set skeletondirectory --value=""
docker exec --user www-data "$NEXTC" php occ app:disable firstrunwizard    || true
docker exec --user www-data "$NEXTC" php occ app:disable dashboard   || true
docker exec --user www-data "$NEXTC" php occ app:disable photos    || true
docker exec --user www-data "$NEXTC" php occ app:disable activity   || true


echo "Done. Access Nextcloud at http://localhost:8080"
