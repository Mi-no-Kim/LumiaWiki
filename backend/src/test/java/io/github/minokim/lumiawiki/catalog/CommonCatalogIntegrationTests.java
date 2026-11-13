package io.github.minokim.lumiawiki.catalog;

import static org.junit.jupiter.api.Assertions.*;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.FlywayException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.core.env.MapPropertySource;
import org.springframework.core.env.StandardEnvironment;
import org.testcontainers.images.builder.Transferable;
import org.testcontainers.postgresql.PostgreSQLContainer;

/** Real product DDL and JPA against a new, disposable database; no host DB settings are read. */
@Tag("integration")
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CommonCatalogIntegrationTests {
  private static final String APP_PASSWORD = "synthetic-catalog-app";
  private static final String MIGRATOR_PASSWORD = "synthetic-catalog-migrator";
  private PostgreSQLContainer database;
  private ConfigurableApplicationContext context;
  private CommonCatalogService service;
  private final AtomicBoolean rejectReferences = new AtomicBoolean();

  @Configuration(proxyBeanMethods = false)
  @EnableAutoConfiguration
  @Import({CommonCatalogService.class, CommonCatalogStore.class})
  static class CatalogTestApplication {
    @Bean
    CatalogReferenceCheck downstreamCheck(AtomicBoolean rejectReferences) {
      return () -> {
        if (rejectReferences.get()) throw ApiFailure.invalidInput("syntheticReference");
      };
    }
  }

  @BeforeAll
  void startIsolatedProduct() throws Exception {
    Path bootstrap = Path.of("..", "db", "bootstrap").toAbsolutePath().normalize();
    database =
        new PostgreSQLContainer("postgres:18.6")
            .withDatabaseName("lumiawiki")
            .withUsername("lumiawiki")
            .withPassword("synthetic-catalog-admin")
            .withEnv("POSTGRES_HOST_AUTH_METHOD", "scram-sha-256")
            .withEnv("DB_APP_USERNAME", "lumia_app")
            .withEnv("DB_APP_PASSWORD", APP_PASSWORD)
            .withEnv("DB_FLYWAY_USERNAME", "lumia_migrator")
            .withEnv("DB_FLYWAY_PASSWORD", MIGRATOR_PASSWORD)
            .withCopyToContainer(
                Transferable.of(Files.readString(bootstrap.resolve("10-prepare-roles.sh")), 0444),
                "/docker-entrypoint-initdb.d/10-prepare-roles.sh")
            .withCopyToContainer(
                Transferable.of(Files.readString(bootstrap.resolve("sql/prepare-roles.sql")), 0444),
                "/opt/lumia-bootstrap/prepare-roles.sql")
            .withReuse(false)
            .withStartupTimeout(Duration.ofSeconds(60));
    database.start();
    var app = new SpringApplication(CatalogTestApplication.class);
    var environment = new StandardEnvironment();
    environment
        .getPropertySources()
        .remove(StandardEnvironment.SYSTEM_ENVIRONMENT_PROPERTY_SOURCE_NAME);
    environment
        .getPropertySources()
        .remove(StandardEnvironment.SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME);
    app.setEnvironment(environment);
    app.setWebApplicationType(WebApplicationType.NONE);
    app.setAdditionalProfiles("local");
    app.addInitializers(c -> {
      c.getBeanFactory().registerSingleton("rejectReferences", rejectReferences);
      var properties = new HashMap<String, Object>();
      properties.put("DB_HOST", database.getHost());
      properties.put("DB_PORT", database.getMappedPort(5432).toString());
      properties.put("DB_NAME", "lumiawiki");
      properties.put("DB_APP_USERNAME", "lumia_app");
      properties.put("DB_APP_PASSWORD", APP_PASSWORD);
      properties.put("DB_FLYWAY_USERNAME", "lumia_migrator");
      properties.put("DB_FLYWAY_PASSWORD", MIGRATOR_PASSWORD);
      properties.put("spring.flyway.locations", "classpath:db/migration");
      properties.put("spring.main.banner-mode", "off");
      c.getEnvironment()
          .getPropertySources()
          .addFirst(new MapPropertySource("isolated-catalog", properties));
    });
    context =
        app.run(); // Flyway installation followed by Hibernate validate, never schema creation.
    service = context.getBean(CommonCatalogService.class);
  }

  @AfterAll
  void closeIsolatedProduct() {
    if (context != null) context.close();
    if (database != null) database.close();
  }

  private Connection appConnection() throws SQLException {
    return context.getBean(DataSource.class).getConnection();
  }

  private Connection migrationConnection() throws SQLException {
    return DriverManager.getConnection(database.getJdbcUrl(), "lumia_migrator", MIGRATOR_PASSWORD);
  }

  private static String scalar(Connection connection, String sql) throws SQLException {
    try (var statement = connection.createStatement();
        var result = statement.executeQuery(sql)) {
      assertTrue(result.next());
      return result.getString(1);
    }
  }

  private static void execute(Connection connection, String sql) throws SQLException {
    try (var statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }

  private static void rejected(Connection connection, String state, String sql) {
    var failure = assertThrows(SQLException.class, () -> execute(connection, sql));
    assertEquals(state, failure.getSQLState());
  }

  @Test
  void installsEightOwnedTablesAndRevalidatesWithoutPendingMigrations() throws Exception {
    try (var connection = migrationConnection()) {
      assertEquals(
          "9",
          scalar(
              connection,
              "select count(*) from pg_tables where schemaname='public' and tableowner='lumia_migrator'"));
      assertEquals(
          "8",
          scalar(
              connection,
              "select count(*) from information_schema.columns where table_schema='public' and column_name='id' and identity_generation='ALWAYS'"));
      assertEquals(
          "8",
          scalar(
              connection,
              "select count(*) from pg_trigger where not tgisinternal and tgname like 'trg_%_reject_pk_update'"));
      assertEquals(
          "6",
          scalar(
              connection,
              "select count(*) from pg_constraint where contype='f' and connamespace='public'::regnamespace and not condeferrable and confdeltype='r'"));
      assertEquals(
          "f",
          scalar(
              connection,
              "select has_function_privilege('lumia_app','public.reject_common_pk_update()','EXECUTE')"));
    }
    Flyway flyway = context.getBean(Flyway.class);
    flyway.validate();
    assertEquals(0, flyway.info().pending().length);
    assertEquals(0, flyway.migrate().migrationsExecuted);
  }

  @Test
  void savesReadsAndCorrectsSnapshotsWithRealTransactionRollback() {
    Season season = service.createSeason(11, "synthetic season", null, null, null);
    GamePatch before = service.createPatch(season.getId(), 0, 0, null, null);
    GamePatch start =
        service.createPatch(
            season.getId(), 0, 1, null, Instant.parse("2020-01-01T00:00:00.987654Z"));
    GamePatch after = service.createPatch(season.getId(), 0, 2, null, null);
    GamePatch empty = service.createPatch(season.getId(), 0, 3, null, null);
    assertEquals(
        Instant.parse("2020-01-01T00:00:00Z"),
        service.get(GamePatch.class, start.getId()).getAppliedAt());
    assertFalse(service.readMap(before.getId()).known());
    Region region = service.createRegion("synthetic internal name");
    var members = List.of(new CatalogViews.MapRegion(region.getId(), "synthetic public name", 10));
    RegionMapVersion map = service.saveMap(null, start.getId(), members);
    assertEquals(members, service.readMap(after.getId()).regions());
    service.renameRegion(region.getId(), "renamed internal name");
    assertEquals(members, service.readMap(start.getId()).regions());
    service.saveMap(null, empty.getId(), List.of());
    assertTrue(service.readMap(empty.getId()).known());
    assertTrue(service.readMap(empty.getId()).regions().isEmpty());
    rejectReferences.set(true);
    try {
      assertThrows(ApiFailure.class, () -> service.saveMap(map.getId(), start.getId(), List.of()));
    } finally {
      rejectReferences.set(false);
    }
    assertEquals(
        members,
        service.readMap(start.getId()).regions(),
        "failed correction must restore deleted members");
    service.saveMap(map.getId(), start.getId(), List.of());
    assertTrue(service.readMap(after.getId()).regions().isEmpty());
    service.updateSeason(season.getId(), 12, "synthetic season", null, null, null);
    assertEquals(210001L, service.get(GamePatch.class, start.getId()).getSortOrder());

    ItemCategory root = service.createCategory("synthetic root", null);
    ItemCategory child = service.createCategory("synthetic child", root.getId());
    assertThrows(
        ApiFailure.class,
        () -> service.updateCategory(root.getId(), "synthetic root", child.getId()));
    assertNull(service.get(ItemCategory.class, root.getId()).getParent());
    service.createWeaponType("synthetic weapon", child.getId());
    assertEquals(
        "API_INPUT_INVALID",
        assertThrows(
                ApiFailure.class,
                () -> service.createWeaponType("another synthetic weapon", child.getId()))
            .code());
    assertEquals(
        1,
        service.list(WeaponType.class).stream()
            .filter(w -> w.getName().equals("synthetic weapon"))
            .count());
    ItemGrade grade = service.createGrade("synthetic grade", 10);
    service.updateGrade(grade.getId(), "corrected synthetic grade", 20);
    assertEquals(
        "corrected synthetic grade", service.get(ItemGrade.class, grade.getId()).getName());
  }

  @Test
  void guardsDirectWritesAndAllowsOnlyApprovedApplicationPrivileges() throws Exception {
    try (var connection = appConnection();
        var migrator = migrationConnection()) {
      long id =
          Long.parseLong(
              scalar(
                  connection,
                  "insert into public.region(display_name) values ('synthetic guard region') returning id"));
      execute(connection, "update public.region set display_name=display_name where id=" + id);
      rejected(connection, "428C9", "update public.region set id=id where id=" + id);
      rejected(connection, "LW001", "update public.region set id=DEFAULT where id=" + id);
      assertEquals(
          "synthetic guard region",
          scalar(connection, "select display_name from public.region where id=" + id));
      rejected(
          connection,
          "428C9",
          "insert into public.region(id,display_name) values (1000001,'explicit identity')");
      rejected(
          connection,
          "23505",
          "insert into public.region(display_name) values ('synthetic guard region')");
      rejected(connection, "23514", "insert into public.region(display_name) values ('   ')");
      rejected(
          connection,
          "23503",
          "insert into public.weapon_type(name,category_id) values ('missing category',9999999)");
      rejected(connection, "42501", "delete from public.region where id=" + id);
      rejected(connection, "42501", "truncate public.region");
      rejected(connection, "42501", "create table public.forbidden_catalog_table(id bigint)");
      rejected(
          connection,
          "42501",
          "alter table public.region disable trigger trg_region_reject_pk_update");
      rejected(connection, "42501", "alter role lumia_migrator superuser");
      execute(connection, "delete from public.region_map_member where false");
      long categoryId =
          Long.parseLong(
              scalar(
                  connection,
                  "insert into public.item_category(name) values ('synthetic FK root') returning id"));
      execute(
          connection,
          "insert into public.weapon_type(name,category_id) values ('synthetic FK weapon',"
              + categoryId
              + ")");
      rejected(migrator, "23001", "delete from public.item_category where id=" + categoryId);
      rejected(
          connection,
          "23505",
          "insert into public.item_category(name) values ('synthetic FK root')");
    }
  }

  @Test
  void conflictingBasisWritesWaitWhilePlainReadsContinue() throws Exception {
    try (var reader = appConnection();
        var writer = appConnection()) {
      reader.setAutoCommit(false);
      execute(reader, "lock table public.game_patch in share mode");
      execute(writer, "set lock_timeout='250ms'");
      assertNotNull(scalar(writer, "select count(*) from public.game_patch"));
      writer.setAutoCommit(false);
      rejected(writer, "55P03", "lock table public.game_patch in share row exclusive mode");
      writer.rollback();
      reader.commit();
      execute(writer, "lock table public.game_patch in share row exclusive mode");
      writer.commit();
    }
  }

  @Test
  void failedInitialMigrationRollsBackTheEntireProductStructure(@TempDir Path migrations)
      throws Exception {
    String failedUrl = database.getJdbcUrl().replace("/lumiawiki", "/catalog_rollback");
    try (var admin =
        DriverManager.getConnection(
            database.getJdbcUrl(), "lumiawiki", "synthetic-catalog-admin")) {
      execute(admin, "create database catalog_rollback");
    }
    try (var admin =
        DriverManager.getConnection(failedUrl, "lumiawiki", "synthetic-catalog-admin")) {
      execute(admin, "revoke all on schema public from public");
      execute(admin, "grant usage, create on schema public to lumia_migrator");
      execute(admin, "grant usage on schema public to lumia_app");
    }
    // Force a failure after the exact product SQL, in this disposable database only.
    String product =
        Files.readString(Path.of("..", "db", "migration", "V1__create_common_model.sql"));
    Files.writeString(migrations.resolve("V1__forced_failure.sql"), product + "\nSELECT 1 / 0;\n");
    Flyway failed =
        Flyway.configure()
            .dataSource(failedUrl, "lumia_migrator", MIGRATOR_PASSWORD)
            .locations("filesystem:" + migrations)
            .load();
    assertThrows(FlywayException.class, failed::migrate);
    try (var connection =
        DriverManager.getConnection(failedUrl, "lumia_migrator", MIGRATOR_PASSWORD)) {
      assertEquals(
          "1", scalar(connection, "select count(*) from pg_tables where schemaname='public'"));
      assertEquals("0", scalar(connection, "select count(*) from public.flyway_schema_history"));
      assertNull(scalar(connection, "select to_regprocedure('public.reject_common_pk_update()')"));
      assertEquals(
          "0",
          scalar(
              connection,
              "select count(*) from information_schema.role_table_grants where table_schema='public' and grantee='lumia_app'"));
    }
  }
}
