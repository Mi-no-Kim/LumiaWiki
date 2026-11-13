package io.github.minokim.lumiawiki;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Duration;
import java.util.HashMap;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.test.system.CapturedOutput;
import org.springframework.boot.test.system.OutputCaptureExtension;
import org.springframework.core.env.MapPropertySource;
import org.springframework.core.env.StandardEnvironment;
import org.testcontainers.containers.Container;
import org.testcontainers.images.builder.Transferable;
import org.testcontainers.postgresql.PostgreSQLContainer;

@Tag("integration")
@ExtendWith(OutputCaptureExtension.class)
class BootstrapInitializationTests {
  private static final String APP_PASSWORD = " app-'\"$\\한글\n끝 ";
  private static final String MIGRATOR_PASSWORD = " migration-'\"$\\비밀\n끝 ";
  private static final String ADMIN_PASSWORD = "synthetic-bootstrap-only";
  private static final String SQL_PATH = "/opt/lumia-bootstrap/prepare-roles.sql";
  private static final String SCRIPT_PATH = "/opt/lumia-bootstrap/run-test.sh";

  private static String source(String name) throws Exception {
    Path path = Path.of("..", "db", "bootstrap").resolve(name).toAbsolutePath().normalize();
    // An absent implementation is a no-op fixture; the required role/exit assertions still fail.
    return Files.exists(path) ? Files.readString(path, StandardCharsets.UTF_8) : "";
  }

  private static PostgreSQLContainer database(boolean initialize, String sqlSuffix)
      throws Exception {
    var database =
        new PostgreSQLContainer("postgres:18.6")
            .withDatabaseName("lumiawiki")
            .withUsername("lumiawiki")
            .withPassword(ADMIN_PASSWORD)
            .withEnv("POSTGRES_HOST_AUTH_METHOD", "scram-sha-256")
            .withEnv("DB_APP_USERNAME", "lumia_app")
            .withEnv("DB_APP_PASSWORD", APP_PASSWORD)
            .withEnv("DB_FLYWAY_USERNAME", "lumia_migrator")
            .withEnv("DB_FLYWAY_PASSWORD", MIGRATOR_PASSWORD)
            .withCopyToContainer(
                Transferable.of(source("sql/prepare-roles.sql") + sqlSuffix, 0444), SQL_PATH)
            .withCopyToContainer(Transferable.of(source("10-prepare-roles.sh"), 0444), SCRIPT_PATH)
            .withReuse(false)
            .withStartupTimeout(Duration.ofSeconds(60));
    if (initialize) {
      database.withCopyToContainer(
          Transferable.of(source("10-prepare-roles.sh"), 0444),
          "/docker-entrypoint-initdb.d/10-prepare-roles.sh");
    }
    return database;
  }

  private static Connection admin(PostgreSQLContainer database) throws SQLException {
    return DriverManager.getConnection(database.getJdbcUrl(), "lumiawiki", ADMIN_PASSWORD);
  }

  private static String scalar(Connection connection, String sql) throws SQLException {
    try (var statement = connection.createStatement();
        var result = statement.executeQuery(sql)) {
      assertTrue(result.next());
      return result.getString(1);
    }
  }

  private static void noSecrets(String text) {
    assertFalse(text.contains(APP_PASSWORD), "app password was exposed");
    assertFalse(text.contains(MIGRATOR_PASSWORD), "Flyway password was exposed");
    assertFalse(text.contains(ADMIN_PASSWORD), "bootstrap password was exposed");
    assertFalse(text.contains("app-'"), "quoted app password was exposed");
    assertFalse(text.contains("migration-'"), "quoted Flyway password was exposed");
  }

  private static void assertDenied(Connection connection, String sql) {
    var failure =
        assertThrows(
            SQLException.class,
            () -> {
              try (var statement = connection.createStatement()) {
                statement.execute(sql);
              }
            });
    assertEquals("42501", failure.getSQLState());
  }

  @Test
  void initializationSeparatesRolesAndSpringConnections(CapturedOutput output) throws Exception {
    try (var database = database(true, "")) {
      database.start();
      try (var connection = admin(database)) {
        assertEquals(
            "2",
            scalar(
                connection,
                "select count(*) from pg_roles where rolname in ('lumia_app','lumia_migrator')"
                    + " and rolcanlogin and not rolsuper and not rolcreatedb and not rolcreaterole"
                    + " and not rolreplication and not rolbypassrls"));
        assertEquals(
            "f",
            scalar(
                connection,
                "select has_database_privilege('lumia_app','lumiawiki','TEMPORARY')"
                    + " or has_schema_privilege('lumia_app','public','CREATE')"));
      }

      var app = new SpringApplication(LumiawikiApiApplication.class);
      var isolatedEnvironment = new StandardEnvironment();
      isolatedEnvironment
          .getPropertySources()
          .remove(StandardEnvironment.SYSTEM_ENVIRONMENT_PROPERTY_SOURCE_NAME);
      isolatedEnvironment
          .getPropertySources()
          .remove(StandardEnvironment.SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME);
      app.setEnvironment(isolatedEnvironment);
      app.setWebApplicationType(WebApplicationType.NONE);
      app.setAdditionalProfiles("local");
      app.addInitializers(context -> {
        var properties = new HashMap<String, Object>();
        properties.put("DB_HOST", database.getHost());
        properties.put("DB_PORT", database.getMappedPort(5432).toString());
        properties.put("DB_NAME", "lumiawiki");
        properties.put("DB_APP_USERNAME", "lumia_app");
        properties.put("DB_APP_PASSWORD", APP_PASSWORD);
        properties.put("DB_FLYWAY_USERNAME", "lumia_migrator");
        properties.put("DB_FLYWAY_PASSWORD", MIGRATOR_PASSWORD);
        properties.put("spring.flyway.locations", "classpath:db/bootstrap-migration");
        properties.put("spring.main.banner-mode", "off");
        context
            .getEnvironment()
            .getPropertySources()
            .addFirst(new MapPropertySource("isolated-bootstrap", properties));
      });
      try (var context = app.run();
          var appConnection = context.getBean(DataSource.class).getConnection();
          var migrationConnection =
              context.getBean(Flyway.class).getConfiguration().getDataSource().getConnection()) {
        assertEquals("lumia_app", scalar(appConnection, "select current_user"));
        assertEquals("lumia_migrator", scalar(migrationConnection, "select current_user"));
        var badPassword =
            assertThrows(
                SQLException.class,
                () ->
                    DriverManager.getConnection(
                        database.getJdbcUrl(), "lumia_app", "wrong-test-password"));
        assertEquals("28P01", badPassword.getSQLState());
        try (var statement = appConnection.createStatement()) {
          statement.executeUpdate("insert into bootstrap_test_probe values (1, 'isolated')");
        }
        assertEquals(
            "isolated",
            scalar(appConnection, "select marker from bootstrap_test_probe where id=1"));
        assertDenied(appConnection, "create table public.bootstrap_forbidden (id integer)");
        assertDenied(appConnection, "truncate table bootstrap_test_probe");
        assertDenied(appConnection, "alter role lumia_migrator superuser");
      }
      try (var connection = admin(database)) {
        assertEquals(
            "lumia_migrator",
            scalar(
                connection,
                "select tableowner from pg_tables where schemaname='public'"
                    + " and tablename='flyway_schema_history'"));
      }
      Container.ExecResult repeated = database.execInContainer("bash", SCRIPT_PATH);
      assertEquals(3, repeated.getExitCode());
      assertEquals("stage=role_prepare result=failed psql_exit=3\n", repeated.getStdout());
      assertEquals("", repeated.getStderr());
      noSecrets(database.getLogs());
      noSecrets(output.getAll());
    }
  }

  @Test
  void lateSqlFailureRollsBackRolesAndPrivilegesWithoutSecretOutput() throws Exception {
    try (var database = database(false, "\nSELECT 1 / 0;\n")) {
      database.start();
      Container.ExecResult result = database.execInContainer("bash", SCRIPT_PATH);
      assertEquals(3, result.getExitCode());
      assertEquals("stage=role_prepare result=failed psql_exit=3\n", result.getStdout());
      assertEquals("", result.getStderr());
      try (var connection = admin(database)) {
        assertEquals(
            "0",
            scalar(
                connection,
                "select count(*) from pg_roles where rolname in ('lumia_app','lumia_migrator')"));
        assertEquals(
            "t",
            scalar(
                connection,
                "select exists (select 1 from pg_database d, lateral"
                    + " aclexplode(coalesce(d.datacl,acldefault('d',d.datdba))) a"
                    + " where d.datname='lumiawiki' and a.grantee=0"
                    + " and a.privilege_type='CONNECT')"));
      }
      noSecrets(database.getLogs());
    }
  }

  @Test
  void nonstandardLoggingStopsBeforePasswordSql() throws Exception {
    try (var database =
        database(false, "").withCommand("postgres", "-c", "log_transaction_sample_rate=1")) {
      database.start();
      Container.ExecResult result = database.execInContainer("bash", SCRIPT_PATH);
      assertEquals(3, result.getExitCode());
      assertEquals("stage=role_prepare result=failed psql_exit=3\n", result.getStdout());
      assertEquals("", result.getStderr());
      try (var connection = admin(database)) {
        assertEquals(
            "0",
            scalar(
                connection,
                "select count(*) from pg_roles where rolname in ('lumia_app','lumia_migrator')"));
      }
      noSecrets(database.getLogs());
    }
  }

  @Test
  void missingInputFailsBeforeDatabaseWrites() throws Exception {
    try (var database = database(false, "").withEnv("DB_APP_PASSWORD", "")) {
      database.start();
      Container.ExecResult result =
          database.execInContainer("bash", "-c", ". /opt/lumia-bootstrap/run-test.sh");
      assertEquals(1, result.getExitCode());
      assertEquals("stage=input_check result=failed\n", result.getStdout());
      assertEquals("", result.getStderr());
      try (var connection = admin(database)) {
        assertEquals(
            "0",
            scalar(
                connection,
                "select count(*) from pg_roles where rolname in ('lumia_app','lumia_migrator')"));
      }
      noSecrets(database.getLogs());
    }
  }
}
