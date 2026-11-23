package io.github.minokim.lumiawiki.catalog;

import static org.junit.jupiter.api.Assertions.*;

import io.github.minokim.lumiawiki.catalog.ItemCatalogService.Material;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.MaxStackChange;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.PatchItem;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.Recipe;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.RecipeChange;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.SkillInput;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.StatInput;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.StatValue;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.VersionInput;
import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
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
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;
import org.testcontainers.images.builder.Transferable;
import org.testcontainers.postgresql.PostgreSQLContainer;
import tools.jackson.databind.json.JsonMapper;

/** Real product DDL and JPA against a new, disposable database; no host DB settings are read. */
@Tag("integration")
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CommonCatalogIntegrationTests {
  private static final String APP_PASSWORD = "synthetic-catalog-app";
  private static final String MIGRATOR_PASSWORD = "synthetic-catalog-migrator";
  private PostgreSQLContainer database;
  private ConfigurableApplicationContext context;
  private CommonCatalogService service;
  private ItemCatalogService items;
  private final AtomicBoolean rejectReferences = new AtomicBoolean();

  @Configuration(proxyBeanMethods = false)
  @EnableAutoConfiguration
  @Import({
    CommonCatalogService.class,
    CommonCatalogStore.class,
    ItemCatalogService.class,
    ItemSkillReferenceCheck.class,
    ItemAcquisitionReferenceCheck.class
  })
  static class CatalogTestApplication {
    @Bean
    CatalogReferenceCheck downstreamCheck(AtomicBoolean rejectReferences) {
      return () -> {
        if (rejectReferences.get()) throw ApiFailure.invalidInput("syntheticReference");
      };
    }

    @Bean
    HuntingAcquisitionCheck syntheticHuntingDetails() {
      return (versionId, regionId) -> regionId == null;
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
    context = startProduct("lumiawiki");
    service = context.getBean(CommonCatalogService.class);
    items = context.getBean(ItemCatalogService.class);
  }

  private ConfigurableApplicationContext startProduct(String databaseName) {
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
      properties.put("DB_NAME", databaseName);
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
    return app.run(); // Flyway installation followed by Hibernate validate.
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

  private String createIsolatedDatabase(String name) throws SQLException {
    String url = database.getJdbcUrl().replace("/lumiawiki", "/" + name);
    try (var admin =
        DriverManager.getConnection(
            database.getJdbcUrl(), "lumiawiki", "synthetic-catalog-admin")) {
      execute(admin, "create database " + name);
    }
    try (var admin = DriverManager.getConnection(url, "lumiawiki", "synthetic-catalog-admin")) {
      execute(admin, "revoke all on schema public from public");
      execute(admin, "grant usage, create on schema public to lumia_migrator");
      execute(admin, "grant usage on schema public to lumia_app");
    }
    return url;
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

  private static VersionInput itemInput(
      long category, long grade, String name, List<SkillInput> skills) {
    return new VersionInput(category, grade, name, null, null, null, null, skills);
  }

  @Test
  void itemStorageInstallsThroughV5AndRevalidatesWithoutPendingMigrations() throws Exception {
    try (var connection = migrationConnection()) {
      assertEquals(
          "0",
          scalar(
              connection,
              "select count(*) from information_schema.columns where table_schema='public' and table_name='item_version' and column_name='equipment_slot'"));
      assertEquals(
          "17",
          scalar(
              connection,
              "select count(*) from pg_tables where schemaname='public' and tableowner='lumia_migrator'"));
      assertEquals(
          "16",
          scalar(
              connection,
              "select count(*) from information_schema.columns where table_schema='public' and column_name='id' and identity_generation='ALWAYS'"));
      assertEquals(
          "16",
          scalar(
              connection,
              "select count(*) from pg_trigger where not tgisinternal and tgname like 'trg_%_reject_pk_update'"));
      assertEquals(
          "25",
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
    assertEquals("5", flyway.info().current().getVersion().getVersion());
    flyway.validate();
    assertEquals(0, flyway.info().pending().length);
    assertEquals(0, flyway.migrate().migrationsExecuted);
  }

  @Test
  void itemRelationsEnforceAgreedConstraintsAndPreserveUnclassifiedCounts() throws Exception {
    long season = service.createSeason(32, "synthetic relation season", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long later = service.createPatch(season, 0, 2, null, null).getId();
    long grade = service.createGrade("synthetic relation grade", 711).getId();
    long category = service.createCategory("synthetic relation category", null).getId();
    long forest = service.createRegion("synthetic forest").getId();
    long shore = service.createRegion("synthetic shore").getId();
    service.saveMap(
        null,
        patch,
        List.of(
            new CatalogViews.MapRegion(forest, "숲", 10),
            new CatalogViews.MapRegion(shore, "해안", 20)));
    var first = items.createItem(null, patch, itemInput(category, grade, "first", null));
    var second = items.createItem(null, patch, itemInput(category, grade, "second", null));
    var crafted = items.createItem(null, patch, itemInput(category, grade, "crafted", null));

    try (var app = appConnection()) {
      String recipe =
          """
          update public.item_version set material_a_item_id=%d,material_a_version_id=%d,
             material_b_item_id=%d,material_b_version_id=%d,craft_output_count=3 where id=%d
          """;
      rejected(
          app,
          "23514",
          "update public.item_version set craft_output_count=3 where id=" + crafted.id());
      rejected(
          app,
          "23514",
          recipe.formatted(first.itemId(), first.id(), first.itemId(), first.id(), crafted.id()));
      rejected(
          app,
          "23503",
          recipe.formatted(
              first.itemId(), second.id(), second.itemId(), second.id(), crafted.id()));
      execute(
          app,
          recipe.formatted(first.itemId(), first.id(), second.itemId(), second.id(), crafted.id()));
      rejected(
          app, "23514", "update public.item_version set delivery_price=2 where id=" + crafted.id());
      execute(
          app,
          "update public.item_version set deliverable=false,delivery_acquire_count=0 where id="
              + crafted.id());

      String acquisition =
          """
          insert into public.item_acquisition(item_id,item_version_id,game_patch_id,method,region_id,spawn_count)
          values (%d,%d,%d,'%s',%s,%s)
          """;
      execute(
          app,
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "CHEST", forest, "null"));
      execute(app, acquisition.formatted(crafted.itemId(), crafted.id(), patch, "CHEST", shore, 0));
      execute(
          app,
          acquisition.formatted(
              crafted.itemId(), crafted.id(), patch, "GATHERING", forest, "null"));
      execute(
          app,
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "GATHERING", shore, "null"));
      execute(
          app,
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "HUNTING", "null", "null"));
      rejected(
          app,
          "23P01",
          acquisition.formatted(
              crafted.itemId(), crafted.id(), patch, "GATHERING", forest, "null"));
      rejected(
          app,
          "23P01",
          acquisition.formatted(
              crafted.itemId(), crafted.id(), patch, "GATHERING", "null", "null"));
      rejected(
          app,
          "23P01",
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "HUNTING", "null", "null"));
      rejected(
          app,
          "23P01",
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "HUNTING", shore, "null"));
      rejected(
          app,
          "23514",
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "CHEST", "null", "null"));
      rejected(
          app,
          "23514",
          acquisition.formatted(crafted.itemId(), crafted.id(), patch, "HUNTING", shore, 0));
      rejected(
          app,
          "23503",
          acquisition.formatted(crafted.itemId(), first.id(), patch, "CHEST", shore, "null"));
      rejected(
          app,
          "23503",
          acquisition.formatted(second.itemId(), second.id(), later, "CHEST", shore, "null"));
      assertEquals(
          "1:1",
          scalar(
              app,
              """
              select count(*) filter (where spawn_count is null)::text || ':' ||
                     count(*) filter (where spawn_count = 0)::text
              from public.item_acquisition where method='CHEST' and item_version_id=
              """
                  + crafted.id()));
      execute(app, "delete from public.item_acquisition where item_version_id=" + crafted.id());
    }
  }

  @Test
  void itemRelationsRoundTripDeliveryAndEditIndividualAcquisitions() {
    long season =
        service.createSeason(33, "synthetic acquisition season", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long inheritedPatch = service.createPatch(season, 0, 2, null, null).getId();
    long later = service.createPatch(season, 0, 3, null, null).getId();
    long boundary = service.createPatch(season, 0, 4, null, null).getId();
    long grade = service.createGrade("synthetic acquisition grade", 712).getId();
    long category = service.createCategory("synthetic acquisition category", null).getId();
    long forest = service.createRegion("synthetic gathering forest").getId();
    long shore = service.createRegion("synthetic gathering shore").getId();
    long absent = service.createRegion("synthetic absent region").getId();
    var map =
        List.of(
            new CatalogViews.MapRegion(forest, "숲", 10),
            new CatalogViews.MapRegion(shore, "해안", 20));
    service.saveMap(null, patch, map);
    var version =
        items.createItem(
            null,
            patch,
            new VersionInput(
                category,
                grade,
                "synthetic source",
                null,
                null,
                null,
                null,
                null,
                null,
                new ItemCatalogService.Delivery(0, false, null)));
    // Keep the region references within this fixture's maps in the shared test database.
    items.recordItemExistence(version.itemId(), boundary, true);
    assertEquals(
        new ItemCatalogService.Delivery(0, false, null),
        items.getItemVersion(version.id()).delivery());

    var chest =
        items.createAcquisition(
            version.id(),
            new ItemCatalogService.AcquisitionInput(AcquisitionMethod.CHEST, forest, null));
    var hunting =
        items.createAcquisition(
            version.id(),
            new ItemCatalogService.AcquisitionInput(AcquisitionMethod.HUNTING, null, null));
    var gathering =
        items.createAcquisition(
            version.id(),
            new ItemCatalogService.AcquisitionInput(AcquisitionMethod.GATHERING, shore, null));
    assertEquals(List.of("HUNTING_DETAIL_MISMATCH"), hunting.warnings());
    assertNull(chest.spawnCount());
    assertEquals(
        "regionId",
        assertThrows(
                ApiFailure.class,
                () ->
                    items.createAcquisition(
                        version.id(),
                        new ItemCatalogService.AcquisitionInput(
                            AcquisitionMethod.GATHERING, null, null)))
            .fields()
            .getFirst()
            .field());
    assertEquals(
        "regionId",
        assertThrows(
                ApiFailure.class,
                () ->
                    items.createAcquisition(
                        version.id(),
                        new ItemCatalogService.AcquisitionInput(
                            AcquisitionMethod.CHEST, absent, 0)))
            .fields()
            .getFirst()
            .field());
    assertEquals(
        0,
        items
            .updateAcquisition(
                version.id(),
                chest.id(),
                new ItemCatalogService.AcquisitionInput(AcquisitionMethod.CHEST, forest, 0))
            .spawnCount());
    items.deleteAcquisition(version.id(), gathering.id());
    assertEquals(
        List.of(chest.id(), hunting.id()),
        items.getItemVersion(version.id()).acquisitions().stream()
            .map(ItemCatalogService.Acquisition::id)
            .toList());
    var inherited =
        items.createItemVersion(
            version.itemId(),
            inheritedPatch,
            itemInput(category, grade, "synthetic inherited source", null));
    assertEquals(version.delivery(), inherited.delivery());
    assertEquals(2, inherited.acquisitions().size());
    assertNotEquals(chest.id(), inherited.acquisitions().getFirst().id());
    assertEquals(0, inherited.acquisitions().getFirst().spawnCount());
    assertTrue(
        inherited.acquisitions().stream()
            .allMatch(row ->
                inherited.itemId().equals(row.itemId())
                    && inherited.id().equals(row.itemVersionId())
                    && row.gamePatchId().equals(inheritedPatch)));
    assertThrows(ApiFailure.class, () -> service.saveMap(null, later, List.of(map.getLast())));
    var deleted = items.recordItemExistence(version.itemId(), later, true);
    assertTrue(items.getItemVersion(deleted.id()).acquisitions().isEmpty());
    assertEquals(2, items.getItemVersion(version.id()).acquisitions().size());
    service.saveMap(null, later, List.of(map.getLast()));
  }

  @Test
  void itemRelationsRejectConcurrentGlobalAndRegionalRowsInEitherOrder() throws Exception {
    long season = service.createSeason(36, "synthetic acquisition race", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long boundary = service.createPatch(season, 0, 2, null, null).getId();
    long grade = service.createGrade("synthetic acquisition race grade", 715).getId();
    long category = service.createCategory("synthetic acquisition race category", null).getId();
    long forest = service.createRegion("synthetic race forest").getId();
    service.saveMap(null, patch, List.of(new CatalogViews.MapRegion(forest, "숲", 10)));
    var owner =
        items.createItem(
            null, patch, itemInput(category, grade, "synthetic acquisition race item", null));
    items.recordItemExistence(owner.itemId(), boundary, true);
    String insert =
        """
        insert into public.item_acquisition(item_id,item_version_id,game_patch_id,method,region_id)
        values (%d,%d,%d,'GATHERING',%s)
        """;
    for (boolean globalFirst : List.of(true, false)) {
      String leading = globalFirst ? "null" : Long.toString(forest);
      var request =
          new ItemCatalogService.AcquisitionInput(
              AcquisitionMethod.GATHERING, globalFirst ? forest : null, null);
      try (var first = appConnection();
          var worker = Executors.newSingleThreadExecutor()) {
        first.setAutoCommit(false);
        String firstPid = scalar(first, "select pg_backend_pid()");
        execute(first, insert.formatted(owner.itemId(), owner.id(), patch, leading));
        var waiter =
            worker.submit(() ->
                assertThrows(ApiFailure.class, () -> items.createAcquisition(owner.id(), request)));
        boolean blocked;
        try {
          blocked =
              waitForDatabaseLock(
                  """
                  select exists (select 1 from pg_stat_activity
                    where %s = any(pg_blocking_pids(pid))
                      and lower(query) like '%%insert into%%item_acquisition%%')::text
                  """
                      .formatted(firstPid));
        } finally {
          first.commit();
        }
        try {
          assertTrue(blocked);
          var failure = waiter.get(10, TimeUnit.SECONDS);
          var spring =
              assertThrows(ApiFailure.class, () -> items.createAcquisition(owner.id(), request));
          assertEquals(spring.fields(), failure.fields());
          assertEquals(spring.operation(), failure.operation());
          assertEquals(1, items.getItemVersion(owner.id()).acquisitions().size());
        } finally {
          execute(first, "delete from public.item_acquisition where item_version_id=" + owner.id());
          first.commit();
        }
      }
    }
  }

  @Test
  void itemRelationsRevalidateMapMembershipInEitherWriteOrder() throws Exception {
    long season = service.createSeason(37, "synthetic map race", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long later = service.createPatch(season, 0, 2, null, null).getId();
    long boundary = service.createPatch(season, 0, 3, null, null).getId();
    long grade = service.createGrade("synthetic map race grade", 716).getId();
    long category = service.createCategory("synthetic map race category", null).getId();
    long forest = service.createRegion("synthetic map race forest").getId();
    long shore = service.createRegion("synthetic map race shore").getId();
    var shoreOnly = List.of(new CatalogViews.MapRegion(shore, "해안", 10));
    service.saveMap(
        null, patch, List.of(new CatalogViews.MapRegion(forest, "숲", 20), shoreOnly.getFirst()));
    var owner =
        items.createItem(null, patch, itemInput(category, grade, "synthetic map item", null));
    items.recordItemExistence(owner.itemId(), boundary, true);
    var chest = new ItemCatalogService.AcquisitionInput(AcquisitionMethod.CHEST, forest, null);
    String pendingMapLock =
        """
        select exists(select 1 from pg_locks
          where relation = 'public.region_map_version'::regclass and not granted and mode = '%s')::text
        """;
    runConcurrentWrites(
        () -> items.createAcquisition(owner.id(), chest),
        () -> assertThrows(ApiFailure.class, () -> service.saveMap(null, later, shoreOnly)),
        waiting ->
            assertTrue(waitForDatabaseLock(pendingMapLock.formatted("ShareRowExclusiveLock"))));
    var saved = items.getItemVersion(owner.id()).acquisitions().getFirst();
    items.deleteAcquisition(owner.id(), saved.id());
    runConcurrentWrites(
        () -> service.saveMap(null, later, shoreOnly),
        () -> {
          var failure =
              assertThrows(ApiFailure.class, () -> items.createAcquisition(owner.id(), chest));
          assertEquals("regionId", failure.fields().getFirst().field());
        },
        waiting -> assertTrue(waitForDatabaseLock(pendingMapLock.formatted("ShareLock"))));
    assertTrue(items.getItemVersion(owner.id()).acquisitions().isEmpty());
  }

  @Test
  void itemRelationsSaveMaterialsFirstAndPropagateTheFinalRecipeAcrossPatches() {
    long season = service.createSeason(34, "synthetic crafting season", null, null, null).getId();
    long first = service.createPatch(season, 0, 1, null, null).getId();
    long second = service.createPatch(season, 0, 2, null, null).getId();
    long third = service.createPatch(season, 0, 3, null, null).getId();
    long grade = service.createGrade("synthetic crafting grade", 713).getId();
    long category = service.createCategory("synthetic crafting category", null).getId();
    var initial =
        items.savePatchItems(
            first,
            List.of(
                new PatchItem(
                    "sword",
                    null,
                    null,
                    withRecipe(category, grade, "검", new Material("blade"), new Material("hilt"))),
                new PatchItem("blade", null, null, itemInput(category, grade, "칼날", null)),
                new PatchItem("hilt", null, false, itemInput(category, grade, "손잡이", null))));
    var sword = initial.get(0);
    var blade = initial.get(1);
    var hilt = initial.get(2);
    assertEquals(
        new Recipe(
            new Material(blade.itemId(), blade.id()), new Material(hilt.itemId(), hilt.id()), 3),
        items.getItemVersion(sword.id()).recipe());
    assertFalse(hilt.searchable());
    assertNull(hilt.recipe());
    var kit =
        items.createItem(
            null,
            first,
            withRecipe(
                category,
                grade,
                "장비 세트",
                new Material(sword.itemId(), sword.id()),
                new Material(hilt.itemId(), hilt.id())));

    var next =
        items.savePatchItems(
            second,
            List.of(
                new PatchItem(
                    null,
                    sword.itemId(),
                    null,
                    withRecipe(
                        category,
                        grade,
                        "개량 검",
                        new Material("steel"),
                        new Material(hilt.itemId(), hilt.id()))),
                new PatchItem(
                    null, blade.itemId(), null, itemInput(category, grade, "기존 칼날 수정", null)),
                new PatchItem("steel", null, null, itemInput(category, grade, "강철판", null))));
    var swordSecond = next.getFirst();
    var steel = next.getLast();
    var kitSecond = effectiveVersion(kit.itemId(), second);
    assertEquals(second, kitSecond.fromGamePatchId());
    assertEquals(swordSecond.id(), kitSecond.recipe().materialA().itemVersionId());
    assertEquals(steel.id(), swordSecond.recipe().materialA().itemVersionId());
    assertEquals("개량 검", swordSecond.name());
    assertEquals(blade.id(), items.getItemVersion(sword.id()).recipe().materialA().itemVersionId());
    assertEquals(sword.id(), items.getItemVersion(kit.id()).recipe().materialA().itemVersionId());

    var directlyChanged =
        items.createItemVersion(sword.itemId(), third, itemInput(category, grade, "이름 바꾼 검", null));
    var kitBeforeMaterialChange = effectiveVersion(kit.itemId(), third);
    var hiltThird =
        items.createItemVersion(hilt.itemId(), third, itemInput(category, grade, "새 손잡이", null));
    var swordThird = effectiveVersion(sword.itemId(), third);
    var kitThird = effectiveVersion(kit.itemId(), third);
    assertEquals(directlyChanged.id(), swordThird.id());
    assertEquals(kitBeforeMaterialChange.id(), kitThird.id());
    assertEquals(third, swordThird.fromGamePatchId());
    assertEquals(hiltThird.id(), swordThird.recipe().materialB().itemVersionId());
    assertEquals(swordThird.id(), kitThird.recipe().materialA().itemVersionId());
    assertEquals("이름 바꾼 검", swordThird.name());
    assertEquals(
        hilt.id(), items.getItemVersion(swordSecond.id()).recipe().materialB().itemVersionId());
  }

  @Test
  void itemRelationsRejectACycleAcrossConcurrentRecipeCorrections() throws Exception {
    long season = service.createSeason(38, "synthetic recipe race", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long category = service.createCategory("synthetic recipe race category", null).getId();
    long grade = service.createGrade("synthetic recipe race grade", 717).getId();
    var fillerF = items.createItem(null, patch, itemInput(category, grade, "F", null));
    var fillerG = items.createItem(null, patch, itemInput(category, grade, "G", null));
    var a = items.createItem(null, patch, itemInput(category, grade, "A", null));
    var c = items.createItem(null, patch, itemInput(category, grade, "C", null));
    var b =
        items.createItem(
            null,
            patch,
            withRecipe(
                category,
                grade,
                "B",
                new Material(c.itemId(), c.id()),
                new Material(fillerF.itemId(), fillerF.id())));
    var d =
        items.createItem(
            null,
            patch,
            withRecipe(
                category,
                grade,
                "D",
                new Material(a.itemId(), a.id()),
                new Material(fillerG.itemId(), fillerG.id())));
    var aCorrection =
        withRecipe(
            category,
            grade,
            "A corrected",
            new Material(b.itemId(), b.id()),
            new Material(fillerF.itemId(), fillerF.id()));
    var cCorrection =
        withRecipe(
            category,
            grade,
            "C corrected",
            new Material(d.itemId(), d.id()),
            new Material(fillerG.itemId(), fillerG.id()));

    var jdbc = new JdbcTemplate(context.getBean(DataSource.class));
    runConcurrentWrites(
        () -> items.updateItemVersion(a.id(), aCorrection),
        () -> {
          var failure =
              assertThrows(ApiFailure.class, () -> items.updateItemVersion(c.id(), cCorrection));
          assertEquals("recipe", failure.fields().getFirst().field());
        },
        waiting -> {
          int holdingPid = jdbc.queryForObject("select pg_backend_pid()", Integer.class);
          assertTrue(
              waitForDatabaseLock(
                  """
                  select exists (select 1 from pg_stat_activity
                    where %d = any(pg_blocking_pids(pid)))::text
                  """
                      .formatted(holdingPid)));
        });
    var corrected = items.getItemVersion(a.id());
    assertEquals("A corrected", corrected.name());
    assertEquals(b.id(), corrected.recipe().materialA().itemVersionId());
    var rejected = items.getItemVersion(c.id());
    assertEquals("C", rejected.name());
    assertNull(rejected.recipe());
  }

  @Test
  void itemRelationsRollBackNewMaterialsIfUpperVersionFails() throws Exception {
    long season = service.createSeason(35, "synthetic crafting rollback", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long grade = service.createGrade("synthetic crafting rollback grade", 714).getId();
    long category = service.createCategory("synthetic crafting rollback category", null).getId();
    try (var migrator = migrationConnection();
        var app = appConnection()) {
      String itemCount = "select count(*) from public.item";
      String before = scalar(app, itemCount);
      execute(
          migrator,
          "alter table public.item_version add constraint ck_test_upper_save_failure check (name <> 'synthetic failing upper')");
      try {
        var failure =
            assertThrows(
                RuntimeException.class,
                () ->
                    items.savePatchItems(
                        patch,
                        List.of(
                            new PatchItem(
                                "upper",
                                null,
                                null,
                                withRecipe(
                                    category,
                                    grade,
                                    "synthetic failing upper",
                                    new Material("lowerA"),
                                    new Material("lowerB"))),
                            new PatchItem(
                                "lowerA",
                                null,
                                null,
                                itemInput(category, grade, "synthetic rolled back A", null)),
                            new PatchItem(
                                "lowerB",
                                null,
                                null,
                                itemInput(category, grade, "synthetic rolled back B", null)))));
        assertTrue(
            java.util.stream.Stream.iterate(
                    (Throwable) failure, java.util.Objects::nonNull, Throwable::getCause)
                .anyMatch(cause ->
                    cause instanceof SQLException sql
                        && "23514".equals(sql.getSQLState())
                        && sql.getMessage().contains("ck_test_upper_save_failure")));
        assertEquals(before, scalar(app, itemCount));
        assertEquals(
            "0",
            scalar(
                app, "select count(*) from public.item_version where from_game_patch_id=" + patch));
      } finally {
        execute(
            migrator, "alter table public.item_version drop constraint ck_test_upper_save_failure");
      }
    }
  }

  private ItemCatalogService.Version effectiveVersion(long itemId, long patchId) {
    long patchOrder = service.get(GamePatch.class, patchId).getSortOrder();
    long version =
        context
            .getBean(CommonCatalogStore.class)
            .findEffectiveItemVersionId(itemId, patchOrder)
            .orElseThrow();
    return items.getItemVersion(version);
  }

  private static VersionInput withRecipe(
      long category, long grade, String name, Material a, Material b) {
    return new VersionInput(
        category,
        grade,
        name,
        null,
        null,
        null,
        null,
        null,
        new RecipeChange(new Recipe(a, b, 3)),
        null);
  }

  @Test
  void itemRelationsCompareInlineAndSeparateRecipesOnTheSameData() throws Exception {
    try (var admin =
        DriverManager.getConnection(
            database.getJdbcUrl(), "lumiawiki", "synthetic-catalog-admin")) {
      execute(
          admin,
          """
          create temporary table compare_inline as
          select id, 'synthetic item ' || id as name,
                 case when id % 4 = 0 then id % 100 end as material_a_item_id,
                 case when id % 4 = 0 then id % 100 + 10000 end as material_a_version_id,
                 case when id % 4 = 0 then id % 100 + 100 end as material_b_item_id,
                 case when id % 4 = 0 then id % 100 + 10100 end as material_b_version_id,
                 case when id % 4 = 0 then 3 end as output_count
          from generate_series(1, 20000) as input(id)
          """);
      execute(admin, "create temporary table compare_base as select id,name from compare_inline");
      execute(
          admin,
          """
          create temporary table compare_recipe as
          select id,material_a_item_id,material_a_version_id,material_b_item_id,material_b_version_id,output_count
          from compare_inline where output_count is not null
          """);
      for (String table : List.of("compare_inline", "compare_base", "compare_recipe")) {
        execute(admin, "alter table " + table + " add primary key (id)");
      }
      for (String table : List.of("compare_inline", "compare_recipe")) {
        execute(admin, "create index on " + table + "(material_a_item_id)");
        execute(admin, "create index on " + table + "(material_b_item_id)");
      }
      for (String table : List.of("compare_inline", "compare_base", "compare_recipe")) {
        execute(admin, "analyze " + table);
      }
      String inlineRead =
          """
          select id, name, material_a_version_id, material_b_version_id, output_count
          from compare_inline where id in (4,5) order by id
          """;
      String separateRead =
          """
          select id, name, material_a_version_id, material_b_version_id, output_count
          from compare_base left join compare_recipe using(id) where id in (4,5) order by id
          """;
      assertEquals(
          scalar(admin, "select json_agg(t)::text from (" + inlineRead + ") t"),
          scalar(admin, "select json_agg(t)::text from (" + separateRead + ") t"));
      String usages =
          "select array_agg(id order by id)::text from %s where material_a_item_id=4 or material_b_item_id=4";
      assertEquals(
          scalar(admin, usages.formatted("compare_inline")),
          scalar(admin, usages.formatted("compare_recipe")));
      String update =
          """
          with updated as (update %s set material_a_version_id=%d where material_a_item_id=4 returning id)
          select count(*)::text from updated
          """;
      assertEquals("200", scalar(admin, update.formatted("compare_inline", 30004)));
      assertEquals("200", scalar(admin, update.formatted("compare_recipe", 30004)));
      System.out.println(
          "recipe comparison bytes (inline vs base+recipe): "
              + scalar(
                  admin,
                  """
                  select pg_total_relation_size('compare_inline')::text || ':' ||
                          (pg_total_relation_size('compare_base') + pg_total_relation_size('compare_recipe'))::text
                  """));
      JsonMapper plans = JsonMapper.builder().build();
      compareRecipeCost(admin, plans, "version lookup", inlineRead, separateRead);
      compareRecipeCost(
          admin,
          plans,
          "material usage",
          usages.formatted("compare_inline"),
          usages.formatted("compare_recipe"));
      compareRecipeCost(
          admin,
          plans,
          "material version change",
          update.formatted("compare_inline", 40004),
          update.formatted("compare_recipe", 40004));
    }
  }

  private record RecipeCost(double milliseconds, long localBlocks, long dirtiedBlocks) {}

  private static void compareRecipeCost(
      Connection connection, JsonMapper plans, String operation, String inline, String separate)
      throws SQLException {
    var inlineSamples = new ArrayList<RecipeCost>();
    var separateSamples = new ArrayList<RecipeCost>();
    connection.setAutoCommit(false);
    try {
      measureRecipeCost(connection, plans, inline);
      measureRecipeCost(connection, plans, separate);
      for (int sample = 0; sample < 7; sample++) {
        // Alternate the execution order so both layouts run first in the paired samples.
        if (sample % 2 == 0) {
          inlineSamples.add(measureRecipeCost(connection, plans, inline));
          separateSamples.add(measureRecipeCost(connection, plans, separate));
        } else {
          separateSamples.add(measureRecipeCost(connection, plans, separate));
          inlineSamples.add(measureRecipeCost(connection, plans, inline));
        }
      }
    } finally {
      connection.rollback();
      connection.setAutoCommit(true);
    }
    var byTime = Comparator.comparingDouble(RecipeCost::milliseconds);
    inlineSamples.sort(byTime);
    separateSamples.sort(byTime);
    RecipeCost inlineMedian = inlineSamples.get(inlineSamples.size() / 2);
    RecipeCost separateMedian = separateSamples.get(separateSamples.size() / 2);
    System.out.printf(
        Locale.ROOT,
        "recipe cost %s: inline %.3f ms, %d local blocks, %d dirtied; separate %.3f ms, %d local blocks, %d dirtied%n",
        operation,
        inlineMedian.milliseconds(),
        inlineMedian.localBlocks(),
        inlineMedian.dirtiedBlocks(),
        separateMedian.milliseconds(),
        separateMedian.localBlocks(),
        separateMedian.dirtiedBlocks());
  }

  private static RecipeCost measureRecipeCost(Connection connection, JsonMapper plans, String sql)
      throws SQLException {
    try {
      var result =
          plans
              .readTree(
                  scalar(connection, "explain (analyze, buffers, timing off, format json) " + sql))
              .get(0);
      var root = result.path("Plan");
      return new RecipeCost(
          result.path("Execution Time").asDouble(),
          root.path("Local Hit Blocks").asLong() + root.path("Local Read Blocks").asLong(),
          root.path("Local Dirtied Blocks").asLong());
    } finally {
      connection.rollback();
    }
  }

  @Test
  void itemStorageReadsEquipmentSlotsFromTheCurrentCategoryTree() {
    long season = service.createSeason(31, "synthetic equipment season", null, null, null).getId();
    long first = service.createPatch(season, 0, 1, null, null).getId();
    long later = service.createPatch(season, 0, 2, null, null).getId();
    long grade = service.createGrade("synthetic equipment grade", 710).getId();
    long allItems = service.createCategory("아이템", null).getId();
    long equipment = service.createCategory("장비", allItems).getId();
    long materials = service.createCategory("재료", null).getId();
    long nonEquipment = service.createCategory("무기", materials).getId();
    var slots =
        Map.of(
            "무기", EquipmentSlot.WEAPON,
            "옷", EquipmentSlot.CHEST,
            "머리", EquipmentSlot.HEAD,
            "장식", EquipmentSlot.ACCESSORY,
            "팔", EquipmentSlot.ACCESSORY,
            "다리", EquipmentSlot.LEG);
    for (var entry : slots.entrySet()) {
      long branch = service.createCategory(entry.getKey(), equipment).getId();
      long leaf = service.createCategory("synthetic leaf", branch).getId();
      var original = items.createItem(null, first, itemInput(leaf, grade, "equipment", null));
      assertEquals(entry.getValue(), items.getItemVersion(original.id()).equipmentSlot());

      var changed =
          items.createItemVersion(
              original.itemId(), later, itemInput(nonEquipment, grade, "material", null));
      assertNull(items.getItemVersion(changed.id()).equipmentSlot());
      assertEquals(leaf, items.getItemVersion(original.id()).categoryId());
      assertEquals(entry.getValue(), items.getItemVersion(original.id()).equipmentSlot());

      service.updateCategory(leaf, entry.getKey() + " synthetic leaf", materials);
      assertEquals(leaf, items.getItemVersion(original.id()).categoryId());
      assertNull(items.getItemVersion(original.id()).equipmentSlot());
    }
  }

  @Test
  void itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange() {
    long season = service.createSeason(39, "synthetic equipment rename", null, null, null).getId();
    long first = service.createPatch(season, 0, 1, null, null).getId();
    long later = service.createPatch(season, 0, 2, null, null).getId();
    long grade = service.createGrade("synthetic equipment rename grade", 719).getId();
    long catalog = service.createCategory("synthetic equipment rename tree", null).getId();
    long equipment = service.createCategory("장비", catalog).getId();
    long clothing = service.createCategory("옷", equipment).getId();
    long armor = service.createCategory("synthetic armor", clothing).getId();
    var original = items.createItem(null, first, itemInput(armor, grade, "original armor", null));
    var changed =
        items.createItemVersion(
            original.itemId(), later, itemInput(armor, grade, "current armor", null));
    assertEquals(EquipmentSlot.CHEST, original.equipmentSlot());

    service.updateCategory(clothing, "상의", equipment);
    assertEquals(EquipmentSlot.CHEST, items.getItemVersion(original.id()).equipmentSlot());
    service.updateCategory(equipment, "개편 장비", catalog);
    assertEquals(EquipmentSlot.CHEST, items.getItemVersion(original.id()).equipmentSlot());
    assertEquals(EquipmentSlot.CHEST, items.getItemVersion(changed.id()).equipmentSlot());
    assertEquals(armor, items.getItemVersion(changed.id()).categoryId());

    long head = service.createCategory("머리", equipment).getId();
    assertEquals(
        EquipmentSlot.HEAD,
        items.createItem(null, later, itemInput(head, grade, "head item", null)).equipmentSlot());
  }

  @Test
  @org.junit.jupiter.api.Timeout(20)
  void itemStorageReadsOneCategoryHierarchyWhenAncestorsMoveConcurrently() {
    long season =
        service.createSeason(40, "synthetic equipment ancestry move", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long grade = service.createGrade("synthetic equipment ancestry grade", 718).getId();
    long catalog = service.createCategory("synthetic equipment ancestry tree", null).getId();
    long equipment = service.createCategory("장비", catalog).getId();
    long clothing = service.createCategory("옷", equipment).getId();
    long outer = service.createCategory("synthetic outer category", clothing).getId();
    long inner = service.createCategory("synthetic inner category", outer).getId();
    var version = items.createItem(null, patch, itemInput(inner, grade, "ancestry item", null));
    var transaction = new TransactionTemplate(context.getBean(PlatformTransactionManager.class));
    var catalogStore = context.getBean(CommonCatalogStore.class);

    try (var editor = Executors.newSingleThreadExecutor()) {
      transaction.executeWithoutResult(ignored -> {
        var cached = catalogStore.find(ItemCategory.class, inner).orElseThrow();
        assertEquals(outer, cached.getParent().getId());
        var moving =
            editor.submit(() ->
                transaction.executeWithoutResult(write -> {
                  service.updateCategory(inner, "synthetic inner category", clothing);
                  service.updateCategory(outer, "synthetic outer category", inner);
                }));
        assertDoesNotThrow(() -> moving.get(5, TimeUnit.SECONDS));
        // The reader still holds the old inner -> outer entity. The DB read sees the whole new
        // path.
        assertEquals(outer, cached.getParent().getId());
        assertEquals(EquipmentSlot.CHEST, items.getItemVersion(version.id()).equipmentSlot());
      });
    }
  }

  @Test
  void itemStorageSavesCorrectsAndRevalidatesSkillLinksAcrossPatches() {
    long season = service.createSeason(21, "synthetic item season", null, null, null).getId();
    long first = service.createPatch(season, 0, 1, null, null).getId();
    long basis = service.createPatch(season, 0, 3, null, null).getId();
    long future = service.createPatch(season, 0, 4, null, null).getId();
    long restore = service.createPatch(season, 0, 6, null, null).getId();
    long category = service.createCategory("synthetic item category", null).getId();
    long grade = service.createGrade("synthetic skill test grade", 701).getId();
    long skillA = items.createSkillDefinition();
    long skillB = items.createSkillDefinition();
    long a1 = items.createSkillVersion(skillA, first, "first", " original A ").id();
    long a2 = items.createSkillVersion(skillA, future, "future", "later A").id();
    long b1 = items.createSkillVersion(skillB, basis, "same patch", "original B").id();
    var links = List.of(new SkillInput(skillA, a1, "display A"), new SkillInput(skillB, b1, null));
    var version =
        items.createItem(null, basis, itemInput(category, grade, " synthetic item ", links));

    var loaded = items.getItemVersion(version.id());
    assertEquals(" synthetic item ", loaded.name());
    assertTrue(loaded.searchable());
    assertFalse(loaded.deleted());
    assertEquals("[]", loaded.statJson());
    assertEquals(
        List.of(a1, b1),
        loaded.skills().stream().map(ItemCatalogService.SkillLink::skillVersionId).toList());
    assertEquals(
        List.of(first, basis),
        loaded.skills().stream().map(ItemCatalogService.SkillLink::skillFromGamePatchId).toList());
    assertTrue(loaded.skills().stream().allMatch(link -> link.itemVersionPatchId() == basis));
    assertEquals(" original A ", loaded.skills().getFirst().originalDescription());
    assertEquals("display A", loaded.skills().getFirst().displayDescription());
    assertEquals("", loaded.skills().getLast().displayDescription());

    var futureLink = List.of(new SkillInput(skillA, a2, ""));
    var failure =
        assertThrows(
            ApiFailure.class,
            () ->
                items.updateItemVersion(
                    version.id(), itemInput(category, grade, "item", futureLink)));
    assertEquals("SKILL_VERSION_AFTER_ITEM_PATCH", failure.fields().getFirst().code());
    assertThrows(ApiFailure.class, () -> service.updatePatch(first, season, 0, 5, null, null));
    assertEquals(1, service.get(GamePatch.class, first).getMinorNo());

    var deleted = items.recordItemExistence(version.itemId(), future, true);
    var restored = items.recordItemExistence(version.itemId(), restore, false);
    assertTrue(deleted.deleted());
    assertFalse(restored.deleted());
    assertEquals(links.size(), restored.skills().size());
    assertNotEquals(loaded.skills().getFirst().id(), restored.skills().getFirst().id());
    assertEquals(restore, restored.skills().getFirst().itemVersionPatchId());
    assertEquals(loaded.name(), restored.name());

    var withoutB = itemInput(category, grade, "corrected item", List.of(links.getFirst()));
    var transaction = new TransactionTemplate(context.getBean(PlatformTransactionManager.class));
    assertThrows(
        ApiFailure.class,
        () ->
            transaction.executeWithoutResult(status -> {
              items.updateItemVersion(version.id(), withoutB);
              items.createSkillVersion(skillA, restore, "missing explanation", null);
            }));
    assertEquals(loaded, items.getItemVersion(version.id()));

    var corrected = items.updateItemVersion(version.id(), withoutB);
    assertEquals(loaded.skills().getFirst(), corrected.skills().getFirst());
    assertEquals(1, items.getItemVersion(version.id()).skills().size());
    assertEquals(2, items.getItemVersion(restored.id()).skills().size());
    assertEquals(
        1,
        items
            .updateItemVersion(version.id(), itemInput(category, grade, "corrected name", null))
            .skills()
            .size());
    assertTrue(
        items
            .updateItemVersion(
                version.id(), itemInput(category, grade, "corrected name", List.of()))
            .skills()
            .isEmpty());
    items.setItemSearchable(version.itemId(), false);
    assertFalse(items.getItemVersion(version.id()).searchable());
    assertFalse(items.getItemVersion(restored.id()).searchable());
  }

  @Test
  void itemStorageGuardsCombinationsDefaultsTextAndApplicationPrivileges() throws Exception {
    long season =
        service.createSeason(22, "synthetic item constraint season", null, null, null).getId();
    long first = service.createPatch(season, 0, 1, null, null).getId();
    long basis = service.createPatch(season, 0, 3, null, null).getId();
    long category = service.createCategory("synthetic item constraint category", null).getId();
    long skillA = items.createSkillDefinition();
    long skillB = items.createSkillDefinition();
    long a1 = items.createSkillVersion(skillA, first, "first", "original").id();
    long b1 = items.createSkillVersion(skillB, first, "second", "original").id();
    long unusedSkill = items.createSkillDefinition();

    try (var app = appConnection();
        var migrator = migrationConnection()) {
      long item =
          Long.parseLong(scalar(app, "insert into public.item default values returning id"));
      String versionInsert =
          """
          insert into public.item_version(item_id,from_game_patch_id,category_id,name)
          values (%d,%d,%d,%%s)
          """
              .formatted(item, basis, category);
      rejected(app, "23502", versionInsert.formatted("null"));
      for (String blank : List.of("''", "chr(9) || chr(10) || chr(12288)")) {
        rejected(app, "23514", versionInsert.formatted(blank));
        rejected(
            app,
            "23514",
            "insert into public.stat_type(name,sort_order) values (" + blank + ",29)");
        rejected(
            app,
            "23514",
            """
            insert into public.item_skill_definition_version
                (item_skill_definition_id,from_game_patch_id,internal_name,description)
            values (%d,%d,'nonblank',%s)
            """
                .formatted(skillB, basis, blank));
      }
      long version =
          Long.parseLong(scalar(app, versionInsert.formatted("'name'") + " returning id"));
      assertEquals(
          "true", scalar(app, "select searchable::text from public.item where id=" + item));
      assertEquals(
          "false:[]",
          scalar(
              app,
              "select is_deleted::text || ':' || stat_json::text from public.item_version where id="
                  + version));
      rejected(app, "23502", "update public.item set searchable=null where id=" + item);
      rejected(app, "23502", "update public.item_version set is_deleted=null where id=" + version);
      rejected(app, "23502", "update public.item_version set stat_json=null where id=" + version);
      for (String json : List.of("null", "{}", "1")) {
        rejected(
            app,
            "23514",
            "update public.item_version set stat_json='%s'::jsonb where id=%d"
                .formatted(json, version));
      }

      long statType = items.createStatType("synthetic stat", 29L).getId();
      rejected(
          app,
          "23505",
          "insert into public.stat_type(name,sort_order) values ('synthetic stat',30)");
      rejected(
          app, "23505", "insert into public.stat_type(name,sort_order) values ('other stat',29)");
      String linkInsert =
          """
          insert into public.item_version_skill_link
              (item_version_id,item_version_patch_id,item_skill_definition_id,item_skill_definition_version_id)
          values (%d,%%d,%%d,%%d)
          """
              .formatted(version);
      rejected(app, "23503", linkInsert.formatted(basis, skillB, a1));
      rejected(app, "23503", linkInsert.formatted(first, skillB, b1));
      execute(app, linkInsert.formatted(basis, skillA, a1));
      rejected(app, "23505", linkInsert.formatted(basis, skillA, a1));
      execute(app, "delete from public.item_version_skill_link where item_version_id=" + version);
      assertTrue(items.getItemVersion(version).skills().isEmpty());
      rejected(app, "42501", "delete from public.item_version where id=" + version);
      rejected(
          app,
          "42501",
          "update public.item_skill_definition set id=default where id=" + unusedSkill);
      rejected(
          migrator,
          "LW001",
          "update public.item_skill_definition set id=default where id=" + unusedSkill);
      rejected(app, "23514", "update public.item_version set max_stack_size=0 where id=" + version);
      rejected(
          app,
          "23503",
          "update public.item_version set grade_id=9223372036854775807 where id=" + version);
      String statInsert =
          """
          insert into public.item_stat(item_version_id,stat_type_id,value) values (%d,%d,%%s)
          """
              .formatted(version, statType);
      for (String value : List.of("'NaN'", "'Infinity'", "'-Infinity'")) {
        rejected(app, "23514", statInsert.formatted(value));
      }
      long stat = Long.parseLong(scalar(app, statInsert.formatted("-0.0001") + " returning id"));
      rejected(app, "23505", statInsert.formatted("1080"));
      rejected(app, "LW001", "update public.item_stat set id=default where id=" + stat);
      execute(app, "delete from public.item_stat where id=" + stat);
    }
  }

  @Test
  void itemStorageSavesExactStatsAndRollsBackWhenCacheWriteFails() throws Exception {
    long season = service.createSeason(23, "synthetic stats season", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long laterPatch = service.createPatch(season, 0, 3, null, null).getId();
    long category = service.createCategory("synthetic stats category", null).getId();
    long grade = service.createGrade("synthetic stats grade", 702).getId();
    long statA = items.createStatType("synthetic first stat", 51L).getId();
    long statB = items.createStatType("synthetic second stat", 60L).getId();
    var original =
        List.of(
            new StatInput(statB, new BigDecimal("1080.0019")),
            new StatInput(statA, new BigDecimal("-0.02")));
    var created =
        items.createItem(
            null,
            patch,
            new VersionInput(
                category, grade, "synthetic stats item", null, null, null, original, List.of()));
    assertNull(created.maxStackSize());
    var version =
        items.updateItemVersion(
            created.id(),
            new VersionInput(
                category, grade, created.name(), null, null, new MaxStackChange(7), null, null));
    var expected =
        List.of(
            new StatValue(Long.toString(statA), "-0.02"),
            new StatValue(Long.toString(statB), "1080.0019"));
    assertEquals(expected, items.getItemVersion(version.id()).stats());
    assertEquals(7, items.getItemVersion(version.id()).maxStackSize());
    var later = items.recordItemExistence(version.itemId(), laterPatch, true);
    assertEquals(expected, later.stats());
    assertEquals(grade, later.gradeId());
    assertEquals(7, later.maxStackSize());
    var replacement =
        new VersionInput(
            category,
            grade,
            version.name(),
            null,
            null,
            null,
            List.of(new StatInput(statA, new BigDecimal("0.2"))),
            null);

    assertCacheWriteRejected(version, () -> items.updateItemVersion(version.id(), replacement));
    assertEquals(expected, items.getItemVersion(version.id()).stats());
    try (var app = appConnection()) {
      assertEquals(
          "-0.02",
          scalar(
              app,
              """
              select value::text from public.item_stat where item_version_id=%d and stat_type_id=%d
              """
                  .formatted(version.id(), statA)));
      assertEquals(
          "1080.0019",
          scalar(
              app,
              """
              select value::text from public.item_stat where item_version_id=%d and stat_type_id=%d
              """
                  .formatted(version.id(), statB)));
    }
    var cleared =
        items.updateItemVersion(
            version.id(),
            new VersionInput(
                category,
                grade,
                version.name(),
                null,
                null,
                new MaxStackChange(null),
                List.of(),
                null));
    assertNull(cleared.maxStackSize());
    assertEquals("[]", cleared.statJson());
    assertEquals(expected, items.getItemVersion(later.id()).stats());
    try (var app = appConnection()) {
      assertEquals(
          "0",
          scalar(
              app, "select count(*) from public.item_stat where item_version_id=" + version.id()));
    }
  }

  private void assertCacheWriteRejected(ItemCatalogService.Version target, Runnable write)
      throws SQLException {
    String configuredCheck =
        """
        alter table public.item_version add constraint item_storage_test_keep_cache
        check (id <> %d or stat_json = '%s'::jsonb)
        """
            .formatted(target.id(), target.statJson());
    try (var migrator = migrationConnection()) {
      execute(migrator, configuredCheck);
      try {
        var failure = assertThrows(RuntimeException.class, write::run);
        assertTrue(causeHasSqlState(failure, "23514"));
      } finally {
        execute(
            migrator,
            "alter table public.item_version drop constraint item_storage_test_keep_cache");
      }
    }
  }

  private static boolean causeHasSqlState(Throwable failure, String expected) {
    for (Throwable cause = failure; cause != null; cause = cause.getCause()) {
      if (cause instanceof SQLException sql && expected.equals(sql.getSQLState())) return true;
    }
    return false;
  }

  @Test
  void itemStorageCoordinatesStatWritesAndOrderChangesInBothDirections() throws Exception {
    long season = service.createSeason(24, "synthetic stat order season", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long category = service.createCategory("synthetic stat order category", null).getId();
    long grade = service.createGrade("synthetic stat order grade", 703).getId();
    long typeA = items.createStatType("synthetic ordered stat A", 71L).getId();
    long typeB = items.createStatType("synthetic ordered stat B", 72L).getId();
    var initial = orderedStatInput(category, grade, typeA, typeB, "0.02");
    var created = items.createItem(null, patch, initial);
    var laterVersion = items.createItem(null, patch, initial);
    var unaffected = items.createItem(null, patch, itemInput(category, grade, "no stats", null));
    runWithConflictingStatLocks(
        () ->
            items.updateItemVersion(
                created.id(), orderedStatInput(category, grade, typeA, typeB, "0.2")),
        () -> items.updateStatType(typeA, "synthetic ordered stat A", 73L),
        "ShareRowExclusiveLock");
    assertEquals(
        List.of(
            new StatValue(Long.toString(typeB), "200"), new StatValue(Long.toString(typeA), "0.2")),
        items.getItemVersion(created.id()).stats());
    assertEquals(
        List.of(
            new StatValue(Long.toString(typeB), "200"),
            new StatValue(Long.toString(typeA), "0.02")),
        items.getItemVersion(laterVersion.id()).stats());

    runWithConflictingStatLocks(
        () -> items.updateStatType(typeA, "synthetic ordered stat A", 71L),
        () ->
            items.updateItemVersion(
                created.id(), orderedStatInput(category, grade, typeA, typeB, "-0.5")),
        "ShareLock");
    assertEquals(
        List.of(
            new StatValue(Long.toString(typeA), "-0.5"),
            new StatValue(Long.toString(typeB), "200")),
        items.getItemVersion(created.id()).stats());
    assertEquals(
        List.of(
            new StatValue(Long.toString(typeA), "0.02"),
            new StatValue(Long.toString(typeB), "200")),
        items.getItemVersion(laterVersion.id()).stats());
    assertEquals("[]", items.getItemVersion(unaffected.id()).statJson());
  }

  @Test
  void itemStorageRollsBackOrderAndCachesWhenRebuildingFails() throws Exception {
    long season =
        service.createSeason(25, "synthetic order rollback season", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long laterPatch = service.createPatch(season, 0, 2, null, null).getId();
    long category = service.createCategory("synthetic order rollback category", null).getId();
    long grade = service.createGrade("synthetic order rollback grade", 704).getId();
    long typeA = items.createStatType("synthetic rollback A", 81L).getId();
    long typeB = items.createStatType("synthetic rollback B", 82L).getId();
    var earlier =
        items.createItem(null, patch, orderedStatInput(category, grade, typeA, typeB, "1.25"));
    var later =
        items.createItemVersion(
            earlier.itemId(), laterPatch, orderedStatInput(category, grade, typeA, typeB, "2.5"));

    String earlierCache = items.getItemVersion(earlier.id()).statJson();
    String laterCache = items.getItemVersion(later.id()).statJson();
    assertCacheWriteRejected(later, () -> items.updateStatType(typeA, "changed rollback A", 83L));

    var statType =
        items.listStatTypes().stream()
            .filter(type -> typeA == type.getId())
            .findFirst()
            .orElseThrow();
    assertEquals(81L, statType.getSortOrder());
    assertEquals("synthetic rollback A", statType.getName());
    assertEquals(earlierCache, items.getItemVersion(earlier.id()).statJson());
    assertEquals(laterCache, items.getItemVersion(later.id()).statJson());
    try (var app = appConnection()) {
      assertEquals(
          "1.25,200,2.5,200",
          scalar(
              app,
              """
              select string_agg(value::text, ',' order by item_version_id, stat_type_id)
              from public.item_stat where item_version_id in (%d, %d)
              """
                  .formatted(earlier.id(), later.id())));
    }

    items.updateStatType(typeA, "changed rollback A", 83L);
    assertEquals(earlier.stats().reversed(), items.getItemVersion(earlier.id()).stats());
    assertEquals(later.stats().reversed(), items.getItemVersion(later.id()).stats());
  }

  @Test
  void itemStorageSerializesWritesForOneItemAndAllowsOtherItemsToProceed() throws Exception {
    long season =
        service.createSeason(26, "synthetic concurrent writes season", null, null, null).getId();
    long patch = service.createPatch(season, 0, 1, null, null).getId();
    long later = service.createPatch(season, 0, 2, null, null).getId();
    long category = service.createCategory("synthetic concurrent writes category", null).getId();
    long grade = service.createGrade("synthetic concurrent writes grade", 705).getId();
    long typeA = items.createStatType("synthetic concurrent A", 91L).getId();
    long typeB = items.createStatType("synthetic concurrent B", 92L).getId();
    var original = orderedStatInput(category, grade, typeA, typeB, "1");
    var firstWrite = orderedStatInput(category, grade, typeA, typeB, "2");
    var laterWrite = orderedStatInput(category, grade, typeA, typeB, "3");
    var version = items.createItem(null, patch, original);
    var sameItem = items.createItemVersion(version.itemId(), later, original);
    var otherItem = items.createItem(null, patch, original);
    var jdbc = new JdbcTemplate(context.getBean(DataSource.class));

    for (long waitingVersion : List.of(version.id(), sameItem.id())) {
      runConcurrentWrites(
          () -> items.updateItemVersion(version.id(), firstWrite),
          () -> items.updateItemVersion(waitingVersion, laterWrite),
          waiting -> {
            int holdingPid = jdbc.queryForObject("select pg_backend_pid()", Integer.class);
            assertTrue(
                waitForDatabaseLock(
                    """
                    select exists (
                      select 1 from pg_locks
                      where locktype = 'transactionid' and not granted
                        and %d = any(pg_blocking_pids(pid)))::text
                    """
                        .formatted(holdingPid)));
            assertFalse(waiting.isDone());
          });
      assertEquals("3", items.getItemVersion(waitingVersion).stats().getFirst().value());
    }

    var concurrentWrite = orderedStatInput(category, grade, typeA, typeB, "4");
    runConcurrentWrites(
        () -> items.updateItemVersion(version.id(), concurrentWrite),
        () -> items.updateItemVersion(otherItem.id(), laterWrite),
        worker -> assertDoesNotThrow(() -> worker.get(5, TimeUnit.SECONDS)));
    assertEquals("4", items.getItemVersion(version.id()).stats().getFirst().value());
    assertEquals("3", items.getItemVersion(otherItem.id()).stats().getFirst().value());
    try (var app = appConnection()) {
      for (var expected : List.of(version, sameItem, otherItem)) {
        var result = items.getItemVersion(expected.id());
        assertEquals(
            result.stats().getFirst().value(),
            scalar(
                app,
                "select value::text from public.item_stat where item_version_id=%d and stat_type_id=%d"
                    .formatted(expected.id(), typeA)));
      }
    }
  }

  private static VersionInput orderedStatInput(
      long category, long grade, long typeA, long typeB, String valueA) {
    return new VersionInput(
        category,
        grade,
        "synthetic order item",
        null,
        null,
        null,
        List.of(
            new StatInput(typeB, new BigDecimal("200")),
            new StatInput(typeA, new BigDecimal(valueA))),
        null);
  }

  private void runWithConflictingStatLocks(Runnable first, Runnable second, String waitingMode)
      throws Exception {
    runConcurrentWrites(
        first,
        second,
        waiting -> {
          assertTrue(
              waitForDatabaseLock(
                  """
                  select exists(select 1 from pg_locks
                  where relation = 'public.stat_type'::regclass and not granted and mode = '%s')::text
                  """
                      .formatted(waitingMode)));
          assertFalse(waiting.isDone());
        });
  }

  private void runConcurrentWrites(
      Runnable first, Runnable second, Consumer<Future<?>> whileFirstOpen) throws Exception {
    var transaction = new TransactionTemplate(context.getBean(PlatformTransactionManager.class));
    try (var workers = Executors.newSingleThreadExecutor()) {
      var secondWrite =
          transaction.execute(status -> {
            first.run();
            var future = workers.submit(second);
            whileFirstOpen.accept(future);
            return future;
          });
      assertNotNull(secondWrite);
      secondWrite.get(10, TimeUnit.SECONDS);
    }
  }

  private boolean waitForDatabaseLock(String query) {
    long deadline = System.nanoTime() + Duration.ofSeconds(5).toNanos();
    try (var app = appConnection()) {
      do {
        if ("true".equals(scalar(app, query))) return true;
        Thread.sleep(20);
      } while (System.nanoTime() < deadline);
      return false;
    } catch (InterruptedException error) {
      Thread.currentThread().interrupt();
      throw new AssertionError(error);
    } catch (SQLException error) {
      throw new AssertionError(error);
    }
  }

  @Test
  void itemStorageUpgradesV1V2AndV3WithoutChangingExistingCategoryReferences() throws Exception {
    String name = "catalog_item_upgrade";
    String url = createIsolatedDatabase(name);
    Flyway v1 =
        Flyway.configure()
            .dataSource(url, "lumia_migrator", MIGRATOR_PASSWORD)
            .locations("classpath:db/migration")
            .target("1")
            .load();
    assertEquals(1, v1.migrate().migrationsExecuted);
    long season;
    long patch;
    long category;
    try (var app = DriverManager.getConnection(url, "lumia_app", APP_PASSWORD)) {
      assertNull(scalar(app, "select to_regclass('public.item')"));
      season =
          Long.parseLong(
              scalar(
                  app,
                  """
                  insert into public.season(season_number,display_name,sort_order)
                  values (1,'upgrade season',10) returning id
                  """));
      patch =
          Long.parseLong(
              scalar(
                  app,
                  """
                  insert into public.game_patch(season_id,major_no,minor_no,sort_order)
                  values (%d,0,1,100001) returning id
                  """
                      .formatted(season)));
      category =
          Long.parseLong(
              scalar(
                  app,
                  """
                  insert into public.item_category(name) values ('upgrade category') returning id
                  """));
    }

    Flyway v2 =
        Flyway.configure()
            .dataSource(url, "lumia_migrator", MIGRATOR_PASSWORD)
            .locations("classpath:db/migration")
            .target("2")
            .load();
    assertEquals(1, v2.migrate().migrationsExecuted);
    long legacyVersion;
    try (var app = DriverManager.getConnection(url, "lumia_app", APP_PASSWORD)) {
      long item =
          Long.parseLong(scalar(app, "insert into public.item default values returning id"));
      legacyVersion =
          Long.parseLong(
              scalar(
                  app,
                  """
                  insert into public.item_version(item_id,from_game_patch_id,category_id,name)
                  values (%d,%d,%d,'legacy V2 item') returning id
                  """
                      .formatted(item, patch, category)));
      assertNull(scalar(app, "select to_regclass('public.item_stat')"));
    }

    Flyway v3 =
        Flyway.configure()
            .dataSource(url, "lumia_migrator", MIGRATOR_PASSWORD)
            .locations("classpath:db/migration")
            .target("3")
            .load();
    assertEquals(1, v3.migrate().migrationsExecuted);
    long weaponCategory;
    long equipmentVersion;
    long preservedStatType;
    long preservedSkillVersion;
    try (var app = DriverManager.getConnection(url, "lumia_app", APP_PASSWORD)) {
      weaponCategory =
          Long.parseLong(
              scalar(
                  app,
                  """
                  with root as (
                    insert into public.item_category(name) values ('장비') returning id
                  )
                  insert into public.item_category(name,parent_id)
                  select '무기',id from root returning id
                  """));
      long item =
          Long.parseLong(scalar(app, "insert into public.item default values returning id"));
      equipmentVersion =
          Long.parseLong(
              scalar(
                  app,
                  """
                  insert into public.item_version(
                    item_id,from_game_patch_id,category_id,name,equipment_slot,max_stack_size)
                  values (%d,%d,%d,'legacy V3 item','CHEST',6) returning id
                  """
                      .formatted(item, patch, weaponCategory)));
      assertEquals(
          "CHEST",
          scalar(
              app, "select equipment_slot from public.item_version where id=" + equipmentVersion));
      preservedStatType =
          Long.parseLong(
              scalar(
                  app,
                  "insert into public.stat_type(name,sort_order) values ('retained stat',10) returning id"));
      execute(
          app,
          "insert into public.item_stat(item_version_id,stat_type_id,value) values (%d,%d,12.5)"
              .formatted(equipmentVersion, preservedStatType));
      execute(
          app,
          """
          update public.item_version set stat_json=jsonb_build_array(jsonb_build_object('statTypeId','%d'::text,'value',12.5))
          where id=%d
          """
              .formatted(preservedStatType, equipmentVersion));
      long skillId =
          Long.parseLong(
              scalar(app, "insert into public.item_skill_definition default values returning id"));
      preservedSkillVersion =
          Long.parseLong(
              scalar(
                  app,
                  """
                  insert into public.item_skill_definition_version(item_skill_definition_id,from_game_patch_id,internal_name,description)
                  values (%d,%d,'retained skill','retained original') returning id
                  """
                      .formatted(skillId, patch)));
      execute(
          app,
          """
          insert into public.item_version_skill_link(item_version_id,item_version_patch_id,
            item_skill_definition_id,item_skill_definition_version_id,description)
          values (%d,%d,%d,%d,'retained link')
          """
              .formatted(equipmentVersion, patch, skillId, preservedSkillVersion));
    }

    Flyway v4 =
        Flyway.configure()
            .dataSource(url, "lumia_migrator", MIGRATOR_PASSWORD)
            .locations("classpath:db/migration")
            .target("4")
            .load();
    assertEquals(1, v4.migrate().migrationsExecuted);
    try (var upgraded = startProduct(name)) {
      var common = upgraded.getBean(CommonCatalogService.class);
      assertEquals("upgrade season", common.get(Season.class, season).getDisplayName());
      assertEquals("upgrade category", common.get(ItemCategory.class, category).getName());
      try (var app = upgraded.getBean(DataSource.class).getConnection()) {
        assertEquals(
            season + ":100001",
            scalar(
                app,
                "select season_id::text || ':' || sort_order from public.game_patch where id="
                    + patch));
        assertEquals(
            "0:0",
            scalar(
                app,
                """
                select num_nonnulls(material_a_item_id, material_a_version_id, material_b_item_id,
                                    material_b_version_id, craft_output_count,
                                    delivery_acquire_count, deliverable, delivery_price)::text || ':' ||
                       (select count(*) from public.item_acquisition)::text
                from public.item_version where id=
                """
                    + legacyVersion));
        assertEquals(
            "12.5",
            scalar(
                app,
                "select value::text from public.item_stat where item_version_id="
                    + equipmentVersion));
      }
      var upgradedItems = upgraded.getBean(ItemCatalogService.class);
      var upgradedEquipment = upgradedItems.getItemVersion(equipmentVersion);
      assertEquals(weaponCategory, upgradedEquipment.categoryId());
      assertEquals(patch, upgradedEquipment.fromGamePatchId());
      assertEquals("legacy V3 item", upgradedEquipment.name());
      assertEquals(6, upgradedEquipment.maxStackSize());
      assertEquals(EquipmentSlot.WEAPON, upgradedEquipment.equipmentSlot());
      long equipmentRoot;
      try (var app = upgraded.getBean(DataSource.class).getConnection()) {
        equipmentRoot =
            Long.parseLong(
                scalar(
                    app, "select parent_id from public.item_category where id=" + weaponCategory));
      }
      common.updateCategory(weaponCategory, "전투 도구", equipmentRoot);
      assertEquals(
          EquipmentSlot.WEAPON, upgradedItems.getItemVersion(equipmentVersion).equipmentSlot());
      assertEquals(
          List.of(new StatValue(Long.toString(preservedStatType), "12.5")),
          upgradedEquipment.stats());
      assertEquals(preservedSkillVersion, upgradedEquipment.skills().getFirst().skillVersionId());
      assertEquals("retained link", upgradedEquipment.skills().getFirst().description());
      var old = upgradedItems.getItemVersion(legacyVersion);
      assertEquals("legacy V2 item", old.name());
      assertEquals(patch, old.fromGamePatchId());
      assertEquals(category, old.categoryId());
      assertNull(old.gradeId());
      assertNull(old.equipmentSlot());
      assertNull(old.maxStackSize());
      assertEquals("[]", old.statJson());
      long deletePatch = common.createPatch(season, 0, 2, null, null).getId();
      long restorePatch = common.createPatch(season, 0, 3, null, null).getId();
      upgradedItems.setItemSearchable(old.itemId(), false);
      var deleted = upgradedItems.recordItemExistence(old.itemId(), deletePatch, true);
      var restored = upgradedItems.recordItemExistence(old.itemId(), restorePatch, false);
      assertTrue(upgradedItems.getItemVersion(deleted.id()).deleted());
      assertFalse(upgradedItems.getItemVersion(restored.id()).deleted());
      assertEquals(deletePatch, deleted.fromGamePatchId());
      assertEquals(restorePatch, restored.fromGamePatchId());
      assertNotEquals(legacyVersion, deleted.id());
      assertNotEquals(deleted.id(), restored.id());
      for (var change : List.of(deleted, restored)) {
        var readBack = upgradedItems.getItemVersion(change.id());
        assertEquals(old.itemId(), readBack.itemId());
        assertEquals(old.categoryId(), readBack.categoryId());
        assertEquals(old.name(), readBack.name());
        assertFalse(readBack.searchable());
        assertNull(readBack.gradeId());
        assertNull(readBack.equipmentSlot());
        assertNull(readBack.maxStackSize());
        assertEquals("[]", readBack.statJson());
      }
      var original = upgradedItems.getItemVersion(legacyVersion);
      assertFalse(original.deleted());
      assertNull(original.gradeId());
      assertEquals(patch, original.fromGamePatchId());

      long grade = common.createGrade("synthetic upgrade grade", 10).getId();
      var corrected =
          upgradedItems.updateItemVersion(
              legacyVersion, itemInput(category, grade, old.name(), null));
      assertEquals(legacyVersion, corrected.id());
      assertEquals(grade, corrected.gradeId());
      var created =
          upgradedItems.createItem(null, patch, itemInput(category, grade, "upgrade item", null));
      assertEquals(patch, upgradedItems.getItemVersion(created.id()).fromGamePatchId());
      assertEquals("5", upgraded.getBean(Flyway.class).info().current().getVersion().getVersion());
    }
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
    String failedUrl = createIsolatedDatabase("catalog_rollback");
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
