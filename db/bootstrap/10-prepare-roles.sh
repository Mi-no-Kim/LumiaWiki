#!/usr/bin/env bash
# A subshell keeps the entrypoint's shell options and environment intact when sourced.
(
  set +x
  set -euo pipefail

  input_failed() {
    printf '%s\n' 'stage=input_check result=failed'
    exit 1
  }

  for key in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD \
    DB_APP_USERNAME DB_APP_PASSWORD DB_FLYWAY_USERNAME DB_FLYWAY_PASSWORD; do
    value=${!key-}
    [[ -n "$value" ]] || input_failed
    case "${value^^}" in
      CHANGE_ME|\<*\>) input_failed ;;
    esac
  done
  [[ "$POSTGRES_DB" == lumiawiki && "$POSTGRES_USER" == lumiawiki \
    && "$DB_APP_USERNAME" == lumia_app \
    && "$DB_FLYWAY_USERNAME" == lumia_migrator ]] || input_failed

  # Use the entrypoint's local socket, not inherited libpq connection overrides.
  unset PGOPTIONS PGSERVICE PGSERVICEFILE PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD PSQLRC
  status=0
  psql -X --no-password --quiet --set=ON_ERROR_STOP=1 \
    --set=ECHO=none --set=ECHO_HIDDEN=off --single-transaction \
    --host=/var/run/postgresql --port=5432 \
    --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" \
    --file=/opt/lumia-bootstrap/prepare-roles.sql >/dev/null 2>&1 || status=$?

  case "$status" in
    0)
      printf '%s\n' 'stage=role_prepare result=ok psql_exit=0'
      ;;
    1|2|3)
      printf 'stage=role_prepare result=failed psql_exit=%s\n' "$status"
      exit "$status"
      ;;
    *)
      printf '%s\n' 'stage=role_prepare result=unknown'
      exit 1
      ;;
  esac
)
