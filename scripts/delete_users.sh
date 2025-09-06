#!/usr/bin/env bash

ROOT="$(cd "$(dirname "$0")/.."; pwd)"

# load NUM_USERS from .env
if [ -f "$ROOT/.env" ]; then
  set -a; source "$ROOT/.env"; set +a
fi
: "${NUM_USERS:?NUM_USERS not set in .env}"

# ensure the nextcloud container is running
if ! docker ps --format '{{.Names}}' | grep -qx nextcloud; then
  echo "Nextcloud container not running. Start stack first (docker compose up -d)."
  exit 1
fi

echo "Deleting $NUM_USERS locust users ..."
for i in $(seq 0 $((NUM_USERS - 1))); do
  USER="locust_user$i"
  echo "Deleting $USER ..."
  docker exec -i -u www-data nextcloud php occ user:delete "$USER" \
    || echo "User $USER may not exist"
done

echo "Done."