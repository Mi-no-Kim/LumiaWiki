package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.EntityManager;
import jakarta.persistence.LockModeType;
import java.util.*;
import org.springframework.stereotype.Repository;

@Repository
public class CommonCatalogStore {
  private final EntityManager em;

  public CommonCatalogStore(EntityManager em) {
    this.em = em;
  }

  public void persist(CatalogRow row) {
    em.persist(row);
  }

  public void flush() {
    em.flush();
  }

  public Optional<Season> findSeason(Long id) {
    return Optional.ofNullable(em.find(Season.class, id));
  }

  public Optional<Season> lockSeason(Long id) {
    return locked(Season.class, id);
  }

  public Optional<GamePatch> findPatch(Long id) {
    return Optional.ofNullable(em.find(GamePatch.class, id));
  }

  public Optional<GamePatch> lockPatch(Long id) {
    return locked(GamePatch.class, id);
  }

  public Optional<Region> findRegion(Long id) {
    return Optional.ofNullable(em.find(Region.class, id));
  }

  public Optional<Region> lockRegion(Long id) {
    return locked(Region.class, id);
  }

  public Optional<ItemCategory> findCategory(Long id) {
    return Optional.ofNullable(em.find(ItemCategory.class, id));
  }

  public Optional<ItemCategory> lockCategory(Long id) {
    return locked(ItemCategory.class, id);
  }

  public Optional<ItemGrade> lockGrade(Long id) {
    return locked(ItemGrade.class, id);
  }

  public Optional<WeaponType> lockWeaponType(Long id) {
    return locked(WeaponType.class, id);
  }

  public Optional<RegionMapVersion> lockMapVersion(Long id) {
    return locked(RegionMapVersion.class, id);
  }

  private <T> Optional<T> locked(Class<T> type, Long id) {
    return Optional.ofNullable(em.find(type, id, LockModeType.PESSIMISTIC_WRITE));
  }

  public void lockBasis(boolean patchWrite, boolean mapWrite) {
    em.createNativeQuery(
            patchWrite
                ? "LOCK TABLE public.game_patch IN SHARE ROW EXCLUSIVE MODE"
                : "LOCK TABLE public.game_patch IN SHARE MODE")
        .executeUpdate();
    em.createNativeQuery(
            mapWrite
                ? "LOCK TABLE public.region_map_version IN SHARE ROW EXCLUSIVE MODE"
                : "LOCK TABLE public.region_map_version IN SHARE MODE")
        .executeUpdate();
  }

  public void lockCategoryTree() {
    em.createNativeQuery("LOCK TABLE public.item_category IN SHARE ROW EXCLUSIVE MODE")
        .executeUpdate();
  }

  public List<GamePatch> lockedPatchesForSeason(Long seasonId) {
    return em.createQuery(
            "select p from GamePatch p where p.season.id = :id order by p.id", GamePatch.class)
        .setParameter("id", seasonId)
        .setLockMode(LockModeType.PESSIMISTIC_WRITE)
        .getResultList();
  }

  public void deleteMapMembers(Long mapVersionId) {
    em.createQuery("delete from RegionMapMember m where m.mapVersion.id = :id")
        .setParameter("id", mapVersionId)
        .executeUpdate();
  }

  public <T extends CatalogRow> List<T> list(Class<T> type) {
    String order =
        type == Season.class || type == GamePatch.class || type == ItemGrade.class
            ? "e.sortOrder"
            : "e.id";
    return em.createQuery("select e from " + type.getSimpleName() + " e order by " + order, type)
        .getResultList();
  }

  public <T extends CatalogRow> Optional<T> find(Class<T> type, Long id) {
    return Optional.ofNullable(em.find(type, id));
  }

  /**
   * A single statement chooses both the query patch's current order and the map members. A target
   * without a map produces one null-map row; a missing target produces no rows.
   */
  public Optional<CatalogViews.RegionMap> readMap(Long patchId) {
    List<?> rows =
        em.createNativeQuery(
                """
                WITH target AS (
                  SELECT id, sort_order FROM public.game_patch WHERE id = :patchId
                ), selected AS (
                  SELECT v.id
                  FROM public.region_map_version v
                  JOIN public.game_patch start_patch ON start_patch.id = v.from_game_patch_id
                  CROSS JOIN target q
                  WHERE start_patch.sort_order <= q.sort_order
                  ORDER BY start_patch.sort_order DESC
                  LIMIT 1
                )
                SELECT q.id, v.id, m.region_id, m.name, m.sort_order
                FROM target q
                LEFT JOIN selected v ON true
                LEFT JOIN public.region_map_member m ON m.map_version_id = v.id
                ORDER BY m.sort_order
                """)
            .setParameter("patchId", patchId)
            .getResultList();
    if (rows.isEmpty()) return Optional.empty();
    Object[] first = (Object[]) rows.getFirst();
    Long versionId = first[1] == null ? null : ((Number) first[1]).longValue();
    List<CatalogViews.MapRegion> regions = new ArrayList<>();
    for (Object row : rows) {
      Object[] values = (Object[]) row;
      if (values[2] != null)
        regions.add(
            new CatalogViews.MapRegion(
                ((Number) values[2]).longValue(),
                (String) values[3],
                ((Number) values[4]).longValue()));
    }
    return Optional.of(new CatalogViews.RegionMap(versionId, regions));
  }
}
