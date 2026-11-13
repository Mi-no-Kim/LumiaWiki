package io.github.minokim.lumiawiki.catalog;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import java.util.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class CommonCatalogStoreTests {
  private EntityManager em;
  private Query query;
  private CommonCatalogStore store;

  @BeforeEach
  void setUp() {
    em = mock(EntityManager.class);
    query = mock(Query.class);
    when(em.createNativeQuery(anyString())).thenReturn(query);
    when(query.setParameter(anyString(), any())).thenReturn(query);
    store = new CommonCatalogStore(em);
  }

  @Test
  void missingQueryPatchHasNoMapResult() {
    when(query.getResultList()).thenReturn(List.of());
    assertTrue(store.readMap(7L).isEmpty());
  }

  @Test
  void nullMapAndConfirmedEmptyMapRemainDifferent() {
    when(query.getResultList())
        .thenReturn(Collections.singletonList(new Object[] {7L, null, null, null, null}));
    var unknown = store.readMap(7L).orElseThrow();
    assertFalse(unknown.known());
    assertTrue(unknown.regions().isEmpty());
    when(query.getResultList())
        .thenReturn(Collections.singletonList(new Object[] {7L, 9L, null, null, null}));
    var empty = store.readMap(7L).orElseThrow();
    assertTrue(empty.known());
    assertEquals(9L, empty.mapVersionId());
    assertTrue(empty.regions().isEmpty());
  }

  @Test
  void rowProjectionPreservesLargeIdsAndPublicNames() {
    long id = 9007199254740993L;
    when(query.getResultList())
        .thenReturn(Collections.singletonList(new Object[] {7L, 9L, id, "공개 지역", 10L}));
    var result = store.readMap(7L).orElseThrow();
    assertEquals(id, result.regions().getFirst().regionId());
    assertEquals("공개 지역", result.regions().getFirst().name());
    assertEquals(10L, result.regions().getFirst().sortOrder());
    assertThrows(UnsupportedOperationException.class, () -> result.regions().clear());
  }

  @Test
  void mapSelectionAndMembersUseOneQueryWithoutReaderLocks() {
    when(query.getResultList())
        .thenReturn(Collections.singletonList(new Object[] {7L, 9L, 1L, "A", 10L}));
    assertTrue(store.readMap(7L).orElseThrow().known());
    verify(em, times(1)).createNativeQuery(anyString());
    verify(query).setParameter("patchId", 7L);
    verify(query).getResultList();
    verifyNoMoreInteractions(em);
  }

  @Test
  void writersAcquireBasisLocksInTheAgreedOrder() {
    store.lockBasis(true, false);
    var sql = ArgumentCaptor.forClass(String.class);
    verify(em, times(2)).createNativeQuery(sql.capture());
    assertEquals(
        List.of(
            "LOCK TABLE public.game_patch IN SHARE ROW EXCLUSIVE MODE",
            "LOCK TABLE public.region_map_version IN SHARE MODE"),
        sql.getAllValues());
    verify(query, times(2)).executeUpdate();
  }
}
