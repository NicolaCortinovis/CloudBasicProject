#!/usr/bin/env bash


# project root (where docker-compose.yml and .env live)
ROOT="$(cd "$(dirname "$0")/.."; pwd)"

# load OC_PASS and NUM_USERS from .env
if [ -f "$ROOT/.env" ]; then
  set -a; source "$ROOT/.env"; set +a
fi
: "${OC_PASS:?OC_PASS is not set (put it in .env next to docker-compose.yml)}"
: "${NUM_USERS:?NUM_USERS not set in .env}"

# ensure the nextcloud container is running
if ! docker ps --format '{{.Names}}' | grep -qx nextcloud; then
  echo "Nextcloud container not running. Start stack first (docker compose up -d)."
  exit 1
fi

echo "Creating $NUM_USERS locust users ..."
for i in $(seq 0 $((NUM_USERS - 1))); do
  USER="locust_user$i"
  echo "Creating $USER ..."
  docker exec -i -u www-data -e OC_PASS="$OC_PASS" nextcloud \
    php occ user:add --password-from-env --display-name="$USER" "$USER" \
    || echo "User $USER may already exist"
done

echo "Done."
