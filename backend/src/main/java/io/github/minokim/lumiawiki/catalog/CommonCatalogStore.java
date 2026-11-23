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

  <T extends CatalogRow> Optional<T> locked(Class<T> type, Long id) {
    return Optional.ofNullable(em.find(type, id, LockModeType.PESSIMISTIC_WRITE));
  }

  public void lockBasis(boolean patchWrite, boolean mapWrite) {
    lockGamePatch(patchWrite);
    em.createNativeQuery(
            mapWrite
                ? "LOCK TABLE public.region_map_version IN SHARE ROW EXCLUSIVE MODE"
                : "LOCK TABLE public.region_map_version IN SHARE MODE")
        .executeUpdate();
  }

  void lockGamePatch(boolean patchWrite) {
    em.createNativeQuery(
            patchWrite
                ? "LOCK TABLE public.game_patch IN SHARE ROW EXCLUSIVE MODE"
                : "LOCK TABLE public.game_patch IN SHARE MODE")
        .executeUpdate();
  }

  void lockStatTypeOrder() {
    em.createNativeQuery("LOCK TABLE public.stat_type IN SHARE ROW EXCLUSIVE MODE").executeUpdate();
  }

  public void lockCategoryTree() {
    em.createNativeQuery("LOCK TABLE public.item_category IN SHARE ROW EXCLUSIVE MODE")
        .executeUpdate();
  }

  void lockStatTypesForStorage() {
    em.createNativeQuery("LOCK TABLE public.stat_type IN SHARE MODE").executeUpdate();
  }

  List<ItemVersion> lockVersionsUsingStatType(Long statTypeId) {
    return em.createQuery(
            """
            select v from ItemVersion v
            where v.id in (
              select s.itemVersion.id from ItemStat s where s.statType.id = :statTypeId
            )
            order by v.id
            """,
            ItemVersion.class)
        .setParameter("statTypeId", statTypeId)
        .setLockMode(LockModeType.PESSIMISTIC_WRITE)
        .getResultList();
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
        type == Season.class
                || type == GamePatch.class
                || type == ItemGrade.class
                || type == StatType.class
            ? "e.sortOrder"
            : "e.id";
    return em.createQuery("select e from " + type.getSimpleName() + " e order by " + order, type)
        .getResultList();
  }

  public <T extends CatalogRow> Optional<T> find(Class<T> type, Long id) {
    return Optional.ofNullable(em.find(type, id));
  }

  Optional<Long> findItemIdByVersion(Long versionId) {
    return em
        .createQuery("select v.item.id from ItemVersion v where v.id = :id", Long.class)
        .setParameter("id", versionId)
        .getResultList()
        .stream()
        .findFirst();
  }

  Optional<Long> findPatchIdByItemVersion(Long versionId) {
    return em
        .createQuery("select v.fromGamePatch.id from ItemVersion v where v.id = :id", Long.class)
        .setParameter("id", versionId)
        .getResultList()
        .stream()
        .findFirst();
  }

  Optional<ItemVersion> findPreviousItemVersion(Long itemId, long patchOrder) {
    return em
        .createQuery(
            """
            select v from ItemVersion v
            where v.item.id = :itemId and v.fromGamePatch.sortOrder < :patchOrder
            order by v.fromGamePatch.sortOrder desc
            """,
            ItemVersion.class)
        .setParameter("itemId", itemId)
        .setParameter("patchOrder", patchOrder)
        .setMaxResults(1)
        .getResultList()
        .stream()
        .findFirst();
  }

  Map<Long, ItemPatchPlan.ActiveVersion> itemVersionsAtPatch(long patchOrder) {
    List<?> rows =
        em.createNativeQuery(
                """
                select distinct on (v.item_id) v.item_id, v.id, v.from_game_patch_id, v.is_deleted,
                       v.material_a_item_id, v.material_a_version_id,
                       v.material_b_item_id, v.material_b_version_id, v.craft_output_count
                from public.item_version v
                join public.game_patch patch on patch.id = v.from_game_patch_id
                where patch.sort_order <= :patchOrder
                order by v.item_id, patch.sort_order desc
                """)
            .setParameter("patchOrder", patchOrder)
            .getResultList();
    Map<Long, ItemPatchPlan.ActiveVersion> versions = new LinkedHashMap<>();
    for (Object result : rows) {
      Object[] row = (Object[]) result;
      var recipe =
          row[8] == null
              ? null
              : new ItemCatalogService.Recipe(
                  new ItemCatalogService.Material((Long) row[4], (Long) row[5]),
                  new ItemCatalogService.Material((Long) row[6], (Long) row[7]),
                  (Integer) row[8]);
      versions.put(
          (Long) row[0],
          new ItemPatchPlan.ActiveVersion((Long) row[1], (Long) row[2], (Boolean) row[3], recipe));
    }
    return versions;
  }

  Optional<Long> findEffectiveItemVersionId(Long itemId, long patchOrder) {
    return em
        .createQuery(
            """
            select v.id from ItemVersion v where v.item.id = :itemId
              and v.fromGamePatch.sortOrder <= :patchOrder
            order by v.fromGamePatch.sortOrder desc
            """,
            Long.class)
        .setParameter("itemId", itemId)
        .setParameter("patchOrder", patchOrder)
        .setMaxResults(1)
        .getResultList()
        .stream()
        .findFirst();
  }

  EquipmentSlot readEquipmentSlot(Long categoryId) {
    // Resolve the whole path in one statement, independent of previously loaded category entities.
    List<?> roles =
        em.createNativeQuery(
                """
                WITH RECURSIVE category_path AS (
                  SELECT c.id, c.parent_id, c.equipment_role, ARRAY[c.id] AS visited, 0 AS depth
                  FROM public.item_category c WHERE c.id = :categoryId
                  UNION ALL
                  SELECT parent.id, parent.parent_id, parent.equipment_role,
                         child.visited || parent.id, child.depth + 1
                  FROM category_path child JOIN public.item_category parent ON parent.id = child.parent_id
                  WHERE NOT parent.id = ANY(child.visited)
                )
                SELECT branch.equipment_role
                FROM category_path branch
                JOIN public.item_category parent ON parent.id = branch.parent_id
                WHERE parent.equipment_role = 'ROOT'
                ORDER BY branch.depth
                LIMIT 1
                """)
            .setParameter("categoryId", categoryId)
            .getResultList();
    if (roles.isEmpty() || roles.getFirst() == null) return null;
    return EquipmentCategoryRole.valueOf((String) roles.getFirst()).slot();
  }

  Optional<ItemVersion> readItemVersion(Long versionId) {
    return em
        .createQuery(
            """
            select v from ItemVersion v
            join fetch v.item
            left join fetch v.skillLinks l
            left join fetch l.skillVersion
            where v.id = :id
            """,
            ItemVersion.class)
        .setParameter("id", versionId)
        .getResultList()
        .stream()
        .findFirst();
  }

  Optional<Long> findItemVersionWithFutureSkill() {
    return em
        .createQuery(
            """
            select l.itemVersion.id from ItemVersionSkillLink l
            where l.skillVersion.fromGamePatch.sortOrder > l.itemVersionPatch.sortOrder
            order by l.itemVersion.id
            """,
            Long.class)
        .setMaxResults(1)
        .getResultList()
        .stream()
        .findFirst();
  }

  boolean acquisitionRegionUnavailable(Long versionId, Long regionId) {
    return (Boolean)
        em.createNativeQuery(
                """
                select exists (
                  select 1 from public.item_version v
                  join public.game_patch start_patch on start_patch.id = v.from_game_patch_id
                  where v.id = :versionId and
                """
                    + unavailableRegion(":regionId")
                    + ")")
            .setParameter("versionId", versionId)
            .setParameter("regionId", regionId)
            .getSingleResult();
  }

  Optional<Long> findAcquisitionOutsideMap() {
    List<?> ids =
        em.createNativeQuery(
                """
                select a.id from public.item_acquisition a
                join public.item_version v on v.id = a.item_version_id
                join public.game_patch start_patch on start_patch.id = v.from_game_patch_id
                where a.region_id is not null and
                """
                    + unavailableRegion("a.region_id")
                    + " order by a.id limit 1")
            .getResultList();
    return ids.isEmpty() ? Optional.empty() : Optional.of(((Number) ids.getFirst()).longValue());
  }

  // A region must appear at the version's start and after every map boundary within its interval.
  private static String unavailableRegion(String reference) {
    return """
    exists (
      select 1 from public.game_patch q
      where q.sort_order >= start_patch.sort_order
        and (q.id = start_patch.id or exists (
          select 1 from public.region_map_version boundary where boundary.from_game_patch_id = q.id
        ))
        and not exists (
          select 1 from public.item_version next_version
          join public.game_patch next_patch on next_patch.id = next_version.from_game_patch_id
          where next_version.item_id = v.item_id
            and next_patch.sort_order > start_patch.sort_order
            and next_patch.sort_order <= q.sort_order
        )
        and not exists (
          select 1 from public.region_map_member member
          where member.region_id = %s and member.map_version_id = (
            select map.id from public.region_map_version map
            join public.game_patch map_patch on map_patch.id = map.from_game_patch_id
            where map_patch.sort_order <= q.sort_order
            order by map_patch.sort_order desc limit 1
          )
        )
    )
    """
        .formatted(reference);
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
