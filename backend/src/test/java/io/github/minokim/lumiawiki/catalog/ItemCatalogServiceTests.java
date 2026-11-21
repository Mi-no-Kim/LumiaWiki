package io.github.minokim.lumiawiki.catalog;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import io.github.minokim.lumiawiki.catalog.ItemCatalogService.MaxStackChange;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.SkillInput;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.StatInput;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.StatValue;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.VersionInput;
import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class ItemCatalogServiceTests {
  private static final long EARLIER_PATCH = 1L;
  private static final long ITEM_PATCH = 3L;
  private static final long LATER_PATCH = 4L;
  private final CommonCatalogStore store = mock(CommonCatalogStore.class);
  private final ItemCatalogService service = new ItemCatalogService(store);

  @Test
  void packagesTheItemMigrationAtTheProductFlywayLocation() {
    assertNotNull(getClass().getResource("/db/migration/V2__create_item_storage.sql"));
  }

  @Test
  void rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext() {
    for (String blank : new String[] {null, "", "\t\n\u3000", "\u00a0\u0085"}) {
      var failure =
          assertThrows(ApiFailure.class, () -> service.createSkillVersion(1L, 3L, "skill", blank));
      assertEquals("API_INPUT_INVALID", failure.code());
      assertEquals("CREATE_SKILL_VERSION", failure.operation());
      assertEquals(new ApiFailure.Target("SKILL_VERSION", null), failure.target());
      assertEquals(
          new ApiFailure.FieldError(
              "description", "SKILL_DESCRIPTION_REQUIRED", "스킬 설명 원문을 입력해 주세요."),
          failure.fields().getFirst());
    }
    verifyNoInteractions(store);
  }

  @Test
  void checksRequiredItemAndStatTypeNamesBeforeWriting() {
    for (String blank : new String[] {null, "", "\t\n\u3000"}) {
      var itemError =
          assertThrows(
              ApiFailure.class, () -> service.createItem(null, 3L, versionInput(blank, null)));
      assertEquals("name", itemError.fields().getFirst().field());
      var statError = assertThrows(ApiFailure.class, () -> service.createStatType(blank, 7L));
      assertEquals("name", statError.fields().getFirst().field());
      var skillError =
          assertThrows(
              ApiFailure.class, () -> service.createSkillVersion(1L, 3L, blank, "description"));
      assertEquals("internalName", skillError.fields().getFirst().field());
    }
    verifyNoInteractions(store);
  }

  @Test
  void separatesMismatchedOwnersDuplicateLinksAndFutureVersions() {
    stubItemVersion();
    var a1 = skill(1L, EARLIER_PATCH, 10L);
    var b1 = skill(2L, ITEM_PATCH, 20L);
    var future = skill(1L, LATER_PATCH, 30L);

    assertFailure(
        List.of(new SkillInput(1L, b1.getId(), null)),
        "skills[0].skillVersionId",
        "SKILL_VERSION_OWNER_MISMATCH");
    assertFailure(
        List.of(new SkillInput(1L, a1.getId(), ""), new SkillInput(1L, future.getId(), null)),
        "skills[1].skillId",
        "DUPLICATE_SKILL_LINK");
    assertFailure(
        List.of(new SkillInput(1L, future.getId(), null)),
        "skills[0].skillVersionId",
        "SKILL_VERSION_AFTER_ITEM_PATCH");
    verify(store, never()).flush();
  }

  @Test
  void keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct() {
    stubItemVersion();
    var previous = skill(1L, EARLIER_PATCH, 10L);
    var samePatch = skill(2L, ITEM_PATCH, 20L);
    var result =
        service.updateItemVersion(
            42L,
            versionInput(
                " item ",
                List.of(
                    new SkillInput(1L, previous.getId(), null),
                    new SkillInput(2L, samePatch.getId(), ""))));

    assertEquals(" item ", result.name());
    assertEquals("[]", result.statJson());
    assertEquals(
        List.of(10L, 20L),
        result.skills().stream().map(ItemCatalogService.SkillLink::skillVersionId).toList());
    assertEquals(
        List.of(EARLIER_PATCH, ITEM_PATCH),
        result.skills().stream().map(ItemCatalogService.SkillLink::skillFromGamePatchId).toList());
    assertEquals(
        List.of(ITEM_PATCH, ITEM_PATCH),
        result.skills().stream().map(ItemCatalogService.SkillLink::itemVersionPatchId).toList());
    assertEquals(" original ", result.skills().getFirst().originalDescription());
    assertNull(result.skills().getFirst().description());
    assertEquals("", result.skills().getFirst().displayDescription());
    assertEquals("", result.skills().getLast().displayDescription());
  }

  @Test
  void readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput() {
    var version = stubItemVersion();
    when(store.readItemVersion(42L)).thenReturn(Optional.of(version));
    var legacy = service.getItemVersion(42L);
    assertNull(legacy.gradeId());
    assertNull(legacy.equipmentSlot());
    assertNull(legacy.maxStackSize());
    assertTrue(legacy.stats().isEmpty());

    var missingGrade = new VersionInput(7L, null, null, "name", null, null, null, null, null);
    var error =
        assertThrows(ApiFailure.class, () -> service.createItem(null, ITEM_PATCH, missingGrade));
    assertEquals("gradeId", error.fields().getFirst().field());
    verify(store, never()).persist(any());
  }

  @Test
  void preservesUnknownLegacyGradeWhenOnlyExistenceChanges() {
    var prior = stubItemVersion();
    when(store.find(GamePatch.class, LATER_PATCH)).thenReturn(Optional.of(patch(LATER_PATCH)));
    when(store.findPreviousItemVersion(5L, LATER_PATCH)).thenReturn(Optional.of(prior));

    var deleted = assertDoesNotThrow(() -> service.recordItemExistence(5L, LATER_PATCH, true));

    assertNull(deleted.gradeId());
    assertEquals(prior.getName(), deleted.name());
    assertEquals(prior.getCategory().getId(), deleted.categoryId());
    assertTrue(deleted.deleted());
  }

  @Test
  void distinguishesStackSizePreservingSettingAndClearing() {
    stubItemVersion();
    var set = service.updateItemVersion(42L, detailedInput(new MaxStackChange(12), null));
    assertEquals(8L, set.gradeId());
    assertEquals(EquipmentSlot.ACCESSORY, set.equipmentSlot());
    assertEquals(12, set.maxStackSize());
    assertEquals(12, service.updateItemVersion(42L, detailedInput(null, null)).maxStackSize());
    var unknown = service.updateItemVersion(42L, detailedInput(new MaxStackChange(null), null));
    assertNull(unknown.maxStackSize());
    for (int invalid : List.of(0, -1)) {
      var error =
          assertThrows(
              ApiFailure.class,
              () ->
                  service.updateItemVersion(42L, detailedInput(new MaxStackChange(invalid), null)));
      assertEquals("maxStackSize", error.fields().getFirst().field());
    }
  }

  @Test
  void preservesExactDecimalsAndBigIdsInTheSortedCacheView() {
    var version = stubItemVersion();
    long largeId = 9_007_199_254_740_993L;
    statType(largeId, 30);
    statType(11L, 10);
    statType(22L, 20);
    var inputs =
        List.of(
            new StatInput(largeId, new BigDecimal("1080")),
            new StatInput(22L, new BigDecimal("-0.0000119")),
            new StatInput(11L, new BigDecimal("0.2")));
    var saved = service.updateItemVersion(42L, detailedInput(null, inputs));
    assertEquals(
        List.of(
            new StatValue("11", "0.2"),
            new StatValue("22", "-0.0000119"),
            new StatValue(Long.toString(largeId), "1080")),
        saved.stats());
    assertTrue(saved.statJson().contains("\"statTypeId\":\"9007199254740993\""));
    assertTrue(saved.statJson().contains("\"value\":0.2"));
    assertEquals(inputs.get(1).value(), version.getStats().get(1).getValue());
    assertEquals(saved.stats(), service.updateItemVersion(42L, detailedInput(null, null)).stats());
    assertEquals("[]", service.updateItemVersion(42L, detailedInput(null, List.of())).statJson());
    assertTrue(version.getStats().isEmpty());
  }

  @Test
  void rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals() {
    var version = stubItemVersion();
    var type = statType(11L, 10);
    version.getStats().add(new ItemStat(version, type, BigDecimal.TEN));
    version.rebuildStatCache();
    var input = new StatInput(11L, BigDecimal.ONE);
    var duplicate =
        assertThrows(
            ApiFailure.class,
            () -> service.updateItemVersion(42L, detailedInput(null, List.of(input, input))));
    assertEquals("DUPLICATE_STAT_TYPE", duplicate.fields().getFirst().code());
    var missing =
        assertThrows(
            ApiFailure.class,
            () ->
                service.updateItemVersion(
                    42L, detailedInput(null, List.of(new StatInput(22L, BigDecimal.ZERO)))));
    assertEquals("stats[0].statTypeId", missing.fields().getFirst().field());
    assertEquals(BigDecimal.TEN, version.getStats().getFirst().getValue());
    verify(store, never()).flush();
  }

  @Test
  void rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues() {
    var version = stubItemVersion();
    StatType earlier = statType(11L, 10);
    StatType later = statType(22L, 20);
    version.getStats().add(new ItemStat(version, earlier, BigDecimal.valueOf(5)));
    version.getStats().add(new ItemStat(version, later, BigDecimal.valueOf(8)));
    version.rebuildStatCache();
    when(store.locked(StatType.class, 22L)).thenReturn(Optional.of(later));
    when(store.lockVersionsUsingStatType(22L)).thenReturn(List.of(version));

    service.updateStatType(22L, "stat name", 5L);
    assertEquals(
        List.of(new StatValue("22", "8"), new StatValue("11", "5")),
        ItemStatCache.read(version.getStatJson()));
    var lockSequence = inOrder(store);
    lockSequence.verify(store).lockStatTypeOrder();
    lockSequence.verify(store).lockVersionsUsingStatType(22L);
    assertEquals(BigDecimal.valueOf(5), version.getStats().getFirst().getValue());
  }

  private void assertFailure(List<SkillInput> skills, String field, String code) {
    var failure =
        assertThrows(
            ApiFailure.class, () -> service.updateItemVersion(42L, versionInput("item", skills)));
    assertEquals("UPDATE_ITEM_VERSION", failure.operation());
    assertEquals(new ApiFailure.Target("ITEM_VERSION", "42"), failure.target());
    assertEquals(field, failure.fields().getFirst().field());
    assertEquals(code, failure.fields().getFirst().code());
  }

  private ItemVersion stubItemVersion() {
    Item item = id(new Item(true), 5L);
    ItemCategory category = id(new ItemCategory(), 7L);
    ItemVersion version =
        id(new ItemVersion(item, patch(ITEM_PATCH), category, "item", null, false), 42L);
    when(store.findItemIdByVersion(42L)).thenReturn(Optional.of(5L));
    when(store.locked(Item.class, 5L)).thenReturn(Optional.of(item));
    when(store.locked(ItemVersion.class, 42L)).thenReturn(Optional.of(version));
    when(store.find(ItemCategory.class, 7L)).thenReturn(Optional.of(category));
    when(store.find(ItemGrade.class, 8L))
        .thenReturn(Optional.of(id(new ItemGrade("grade", 10L), 8L)));
    return version;
  }

  private StatType statType(long id, long order) {
    var type = id(new StatType("stat " + id, order), id);
    when(store.find(StatType.class, id)).thenReturn(Optional.of(type));
    return type;
  }

  private static VersionInput versionInput(String name, List<SkillInput> skills) {
    return new VersionInput(7L, 8L, null, name, null, null, null, null, skills);
  }

  private static VersionInput detailedInput(MaxStackChange maxStack, List<StatInput> stats) {
    return new VersionInput(
        7L, 8L, EquipmentSlot.ACCESSORY, "item", null, null, maxStack, stats, null);
  }

  private ItemSkillDefinitionVersion skill(long definitionId, long patchId, long skillVersionId) {
    var version =
        id(
            new ItemSkillDefinitionVersion(
                id(new ItemSkillDefinition(), definitionId), patch(patchId), "skill", " original "),
            skillVersionId);
    when(store.find(ItemSkillDefinitionVersion.class, skillVersionId))
        .thenReturn(Optional.of(version));
    return version;
  }

  private static GamePatch patch(long id) {
    return id(new GamePatch(new Season(), 0, (int) id, null, id, null), id);
  }

  private static <T extends CatalogRow> T id(T value, long id) {
    ReflectionTestUtils.setField(value, "id", id);
    return value;
  }
}
