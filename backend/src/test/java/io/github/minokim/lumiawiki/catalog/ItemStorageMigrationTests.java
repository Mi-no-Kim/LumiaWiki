package io.github.minokim.lumiawiki.catalog;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;

class ItemStorageMigrationTests {
  @Test
  void packagesTheFollowupMigrationAtTheProductFlywayLocation() {
    assertNotNull(getClass().getResource("/db/migration/V3__complete_item_storage.sql"));
  }
}
