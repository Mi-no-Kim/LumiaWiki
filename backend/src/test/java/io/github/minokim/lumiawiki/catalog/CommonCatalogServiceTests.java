package io.github.minokim.lumiawiki.catalog;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.*;
import org.hibernate.exception.ConstraintViolationException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.aop.framework.ProxyFactory;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.transaction.*;
import org.springframework.transaction.annotation.AnnotationTransactionAttributeSource;
import org.springframework.transaction.interceptor.TransactionInterceptor;
import org.springframework.transaction.support.SimpleTransactionStatus;

class CommonCatalogServiceTests {
  private CommonCatalogStore store;
  private CommonCatalogService service;

  @BeforeEach
  void setUp() {
    store = mock(CommonCatalogStore.class);
    service = new CommonCatalogService(store, List.of());
    doAnswer(
            invocation -> {
              CatalogRow row = invocation.getArgument(0);
              if (row.getId() == null) ReflectionTestUtils.setField(row, "id", 100L);
              return null;
            })
        .when(store)
        .persist(any());
  }

  @Test
  void seasonKeepsUnknownMetadataAndComputesWideOrder() {
    Season season = service.createSeason(Integer.MAX_VALUE, "display", null, null, null);
    assertEquals(2147483656L, season.getSortOrder());
    assertNull(season.getSeasonName());
    assertNull(season.getStartDate());
    assertNull(season.getEndDate());
  }

  @Test
  void patchUsesSeasonOrderAndTruncatesSubseconds() {
    Season season = row(new Season(), "id", 7L, "sortOrder", 10L);
    when(store.findSeason(7L)).thenReturn(Optional.of(season));
    GamePatch patch =
        service.createPatch(7L, 2, 3, null, Instant.parse("2020-01-01T00:00:00.987654321Z"));
    assertEquals(100203L, patch.getSortOrder());
    assertEquals(Instant.parse("2020-01-01T00:00:00Z"), patch.getAppliedAt());
    assertNull(patch.getVersionName());
    verify(store).lockBasis(true, false);
  }

  @Test
  void patchBoundaryZeroAndNinetyNineAreAccepted() {
    when(store.findSeason(7L))
        .thenReturn(Optional.of(row(new Season(), "id", 7L, "sortOrder", 10L)));
    assertEquals(100000L, service.createPatch(7L, 0, 0, null, null).getSortOrder());
    assertEquals(109999L, service.createPatch(7L, 99, 99, null, null).getSortOrder());
  }

  @Test
  void patchBoundsAreRejectedBeforeWriting() {
    for (int number : new int[] {-1, 100}) {
      assertThrows(ApiFailure.class, () -> service.createPatch(7L, number, 0, null, null));
      assertThrows(ApiFailure.class, () -> service.createPatch(7L, 0, number, null, null));
    }
    verify(store, never()).persist(any());
  }

  @Test
  void badNamesAndReversedDatesAreRejected() {
    assertThrows(ApiFailure.class, () -> service.createRegion("   "));
    assertThrows(ApiFailure.class, () -> service.createSeason(0, "name", null, null, null));
    assertThrows(
        ApiFailure.class,
        () ->
            service.createSeason(
                1, "name", null, LocalDate.of(2020, 2, 2), LocalDate.of(2020, 1, 1)));
    assertEquals("  작업명  ", service.createRegion("  작업명  ").getDisplayName());
  }

  @Test
  void categoryCycleIsRejectedUnderTheTreeLock() {
    ItemCategory first = row(new ItemCategory(), "id", 1L, "name", "first");
    ItemCategory second = row(new ItemCategory(), "id", 2L, "name", "second", "parent", first);
    when(store.lockCategory(1L)).thenReturn(Optional.of(first));
    when(store.findCategory(2L)).thenReturn(Optional.of(second));
    assertThrows(ApiFailure.class, () -> service.updateCategory(1L, "first", 2L));
    assertNull(first.getParent());
    verify(store).lockCategoryTree();
  }

  @Test
  void mapDuplicatesAreRejectedBeforeReplacement() {
    for (List<CatalogViews.MapRegion> entries :
        List.of(
            List.of(entry(1L, "A", 10), entry(1L, "B", 20)),
            List.of(entry(1L, "A", 10), entry(2L, "A", 20)),
            List.of(entry(1L, "A", 10), entry(2L, "B", 10)))) {
      assertThrows(ApiFailure.class, () -> service.saveMap(50L, 7L, entries));
    }
    verify(store, never()).deleteMapMembers(any());
    verify(store, never()).persist(any());
  }

  @Test
  void missingMapRegionsAreRejected() {
    when(store.findPatch(7L)).thenReturn(Optional.of(row(new GamePatch(), "id", 7L)));
    when(store.findRegion(88L)).thenReturn(Optional.empty());
    ApiFailure failure =
        assertThrows(
            ApiFailure.class, () -> service.saveMap(null, 7L, List.of(entry(88L, "A", 10))));
    assertEquals("API_INPUT_INVALID", failure.code());
    verify(store, never()).persist(any());
  }

  @Test
  void workingRegionRenameDoesNotChangeMapHistory() {
    Region region = row(new Region(), "id", 1L, "displayName", "old working name");
    when(store.lockRegion(1L)).thenReturn(Optional.of(region));
    service.renameRegion(1L, "new working name");
    assertEquals("new working name", region.getDisplayName());
    verify(store, never()).lockBasis(anyBoolean(), anyBoolean());
    verify(store, never()).deleteMapMembers(any());
  }

  @Test
  void mapQueryDistinguishesUnknownFromConfirmedEmpty() {
    when(store.readMap(7L)).thenReturn(Optional.of(new CatalogViews.RegionMap(null, List.of())));
    assertFalse(service.readMap(7L).known());
    when(store.readMap(7L)).thenReturn(Optional.of(new CatalogViews.RegionMap(9L, List.of())));
    assertTrue(service.readMap(7L).known());
    when(store.readMap(7L)).thenReturn(Optional.empty());
    assertEquals(
        "API_RESOURCE_NOT_FOUND", assertThrows(ApiFailure.class, () -> service.readMap(7L)).code());
  }

  @Test
  void mapQueryReturnsPublicNamesOnly() {
    when(store.readMap(7L))
        .thenReturn(Optional.of(new CatalogViews.RegionMap(9L, List.of(entry(1L, "공개 이름", 10)))));
    assertEquals("공개 이름", service.readMap(7L).regions().getFirst().name());
    assertEquals(
        Set.of("regionId", "name", "sortOrder"),
        Arrays.stream(CatalogViews.MapRegion.class.getRecordComponents())
            .map(component -> component.getName())
            .collect(java.util.stream.Collectors.toSet()));
  }

  @Test
  void knownBusinessConstraintsUseExistingInputError() {
    RuntimeException failure =
        new ConstraintViolationException(
            "not public", new SQLException("hidden", "23505"), "uq_item_grade_name");
    assertEquals(
        "API_INPUT_INVALID",
        assertInstanceOf(ApiFailure.class, CatalogErrors.translate(failure)).code());
  }

  @Test
  void unexpectedPkGuardRemainsAnInternalFailure() {
    RuntimeException failure = new RuntimeException(new SQLException("hidden", "LW001"));
    assertSame(failure, CatalogErrors.translate(failure));
    RuntimeException unnamed =
        new ConstraintViolationException("hidden", new SQLException("hidden", "23505"), null);
    assertSame(unnamed, CatalogErrors.translate(unnamed));
  }

  @Test
  void dependentReferenceFailureIsPropagated() {
    CommonCatalogService checked = checkedService();
    assertThrows(ApiFailure.class, () -> checked.saveMap(null, 7L, List.of()));
    verify(store).lockBasis(false, true);
  }

  @Test
  void writeTransactionUsesReadCommitted() {
    PlatformTransactionManager manager = transactionManager();
    proxied(service, manager).createSeason(1, "display", null, null, null);
    var definition = ArgumentCaptor.forClass(TransactionDefinition.class);
    verify(manager).getTransaction(definition.capture());
    assertEquals(
        TransactionDefinition.ISOLATION_READ_COMMITTED, definition.getValue().getIsolationLevel());
    verify(manager).commit(any());
  }

  @Test
  void dependentFailureRollsBackTheSpringTransactionBoundary() {
    PlatformTransactionManager manager = transactionManager();
    assertThrows(
        ApiFailure.class, () -> proxied(checkedService(), manager).saveMap(null, 7L, List.of()));
    verify(manager).rollback(any());
    verify(manager, never()).commit(any());
  }

  private CommonCatalogService checkedService() {
    when(store.findPatch(7L)).thenReturn(Optional.of(row(new GamePatch(), "id", 7L)));
    return new CommonCatalogService(
        store,
        List.of(() -> {
          throw ApiFailure.invalidInput("regionId");
        }));
  }

  private static PlatformTransactionManager transactionManager() {
    PlatformTransactionManager manager = mock(PlatformTransactionManager.class);
    when(manager.getTransaction(any())).thenReturn(new SimpleTransactionStatus());
    return manager;
  }

  private static CommonCatalogService proxied(
      CommonCatalogService service, PlatformTransactionManager manager) {
    ProxyFactory factory = new ProxyFactory(service);
    factory.addAdvice(
        new TransactionInterceptor(manager, new AnnotationTransactionAttributeSource()));
    return (CommonCatalogService) factory.getProxy();
  }

  private static CatalogViews.MapRegion entry(Long id, String name, long order) {
    return new CatalogViews.MapRegion(id, name, order);
  }

  private static <T> T row(T value, Object... fields) {
    for (int i = 0; i < fields.length; i += 2)
      ReflectionTestUtils.setField(value, (String) fields[i], fields[i + 1]);
    return value;
  }
}
