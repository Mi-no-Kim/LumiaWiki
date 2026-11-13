\getenv db_name POSTGRES_DB
\getenv app_user DB_APP_USERNAME
\getenv app_password DB_APP_PASSWORD
\getenv migrator_user DB_FLYWAY_USERNAME
\getenv migrator_password DB_FLYWAY_PASSWORD

-- These checks contain no password SQL. Unknown logging paths fail before role creation.
DO $bootstrap_preconditions$
BEGIN
  IF current_user <> 'lumiawiki' OR current_database() <> 'lumiawiki'
     OR NOT (SELECT rolsuper FROM pg_roles WHERE rolname = current_user)
     OR current_setting('server_encoding') <> 'UTF8'
     OR current_setting('server_version_num')::INTEGER / 10000 <> 18 THEN
    RAISE EXCEPTION 'Unsupported bootstrap connection';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('lumia_app', 'lumia_migrator')) THEN
    RAISE EXCEPTION 'Bootstrap roles already exist';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'public')
     OR NOT EXISTS (SELECT 1 FROM pg_language WHERE lanname = 'plpgsql') THEN
    RAISE EXCEPTION 'Required bootstrap objects are missing';
  END IF;
  IF current_setting('log_transaction_sample_rate')::NUMERIC <> 0
     OR current_setting('log_destination') <> 'stderr'
     OR current_setting('logging_collector') <> 'off'
     OR current_setting('shared_preload_libraries') <> ''
     OR current_setting('session_preload_libraries') <> ''
     OR current_setting('local_preload_libraries') <> ''
     OR EXISTS (SELECT 1 FROM pg_extension WHERE extname <> 'plpgsql') THEN
    RAISE EXCEPTION 'Unsupported bootstrap logging configuration';
  END IF;
END
$bootstrap_preconditions$;

SET LOCAL log_statement = 'none';
SET LOCAL log_min_duration_statement = -1;
SET LOCAL log_min_duration_sample = -1;
SET LOCAL log_transaction_sample_rate = 0;
SET LOCAL log_min_error_statement = 'panic';
SET LOCAL log_min_messages = 'panic';
SET LOCAL log_parameter_max_length = 0;
SET LOCAL log_parameter_max_length_on_error = 0;
SET LOCAL password_encryption = 'scram-sha-256';

DO $bootstrap_log_check$
BEGIN
  IF current_setting('log_statement') <> 'none'
     OR current_setting('log_min_duration_statement') <> '-1'
     OR current_setting('log_min_duration_sample') <> '-1'
     OR current_setting('log_transaction_sample_rate')::NUMERIC <> 0
     OR current_setting('log_min_error_statement') <> 'panic'
     OR current_setting('log_min_messages') <> 'panic'
     OR current_setting('log_parameter_max_length') <> '0'
     OR current_setting('log_parameter_max_length_on_error') <> '0'
     OR current_setting('password_encryption') <> 'scram-sha-256' THEN
    RAISE EXCEPTION 'Bootstrap logging conditions were not applied';
  END IF;
END
$bootstrap_log_check$;

CREATE ROLE :"migrator_user" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD :'migrator_password';
CREATE ROLE :"app_user" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD :'app_password';

REVOKE CONNECT, TEMPORARY, CREATE ON DATABASE :"db_name" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"db_name" TO :"app_user", :"migrator_user";
REVOKE USAGE, CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO :"app_user";
GRANT USAGE, CREATE ON SCHEMA public TO :"migrator_user";
GRANT USAGE ON LANGUAGE plpgsql TO :"migrator_user";

DO $bootstrap_privilege_check$
DECLARE
  checked_role TEXT;
BEGIN
  FOR checked_role IN SELECT unnest(ARRAY['lumia_app', 'lumia_migrator']) LOOP
    IF NOT EXISTS (
      SELECT 1 FROM pg_roles WHERE rolname = checked_role AND rolcanlogin
        AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole
        AND NOT rolreplication AND NOT rolbypassrls
    ) OR NOT has_database_privilege(checked_role, current_database(), 'CONNECT')
      OR has_database_privilege(checked_role, current_database(), 'CREATE')
      OR has_database_privilege(checked_role, current_database(), 'TEMPORARY') THEN
      RAISE EXCEPTION 'Bootstrap role privileges do not match';
    END IF;
  END LOOP;
  IF EXISTS (
    SELECT 1 FROM pg_auth_members
    WHERE member IN (SELECT oid FROM pg_roles WHERE rolname IN ('lumia_app', 'lumia_migrator'))
       OR roleid IN (SELECT oid FROM pg_roles WHERE rolname IN ('lumia_app', 'lumia_migrator'))
  ) THEN
    RAISE EXCEPTION 'Unexpected bootstrap role membership';
  END IF;
  IF NOT has_schema_privilege('lumia_app', 'public', 'USAGE')
     OR has_schema_privilege('lumia_app', 'public', 'CREATE')
     OR NOT has_schema_privilege('lumia_migrator', 'public', 'USAGE')
     OR NOT has_schema_privilege('lumia_migrator', 'public', 'CREATE')
     OR NOT has_language_privilege('lumia_migrator', 'plpgsql', 'USAGE') THEN
    RAISE EXCEPTION 'Bootstrap schema privileges do not match';
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_database d,
      LATERAL aclexplode(COALESCE(d.datacl, acldefault('d', d.datdba))) a
    WHERE d.datname = current_database() AND a.grantee = 0
      AND a.privilege_type IN ('CONNECT', 'TEMPORARY', 'CREATE')
  ) OR EXISTS (
    SELECT 1 FROM pg_namespace n,
      LATERAL aclexplode(COALESCE(n.nspacl, acldefault('n', n.nspowner))) a
    WHERE n.nspname = 'public' AND a.grantee = 0
      AND a.privilege_type IN ('USAGE', 'CREATE')
  ) THEN
    RAISE EXCEPTION 'Unexpected PUBLIC bootstrap privileges';
  END IF;
END
$bootstrap_privilege_check$;
