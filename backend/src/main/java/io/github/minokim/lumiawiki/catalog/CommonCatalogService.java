package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.time.*;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.function.Supplier;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(isolation = Isolation.READ_COMMITTED)
public class CommonCatalogService {
  private final CommonCatalogStore store;
  private final List<CatalogReferenceCheck> referenceChecks;

  public CommonCatalogService(
      CommonCatalogStore store, List<CatalogReferenceCheck> referenceChecks) {
    this.store = store;
    this.referenceChecks = List.copyOf(referenceChecks);
  }

  public Season createSeason(
      int number, String displayName, String actualName, LocalDate start, LocalDate end) {
    seasonInput(number, displayName, actualName, start, end);
    return write(
        () -> {
          Season value =
              new Season(number, displayName, actualName, seasonOrder(number), start, end);
          store.persist(value);
          return value;
        },
        false);
  }

  public Season updateSeason(
      Long id, int number, String displayName, String actualName, LocalDate start, LocalDate end) {
    id(id);
    seasonInput(number, displayName, actualName, start, end);
    return write(
        () -> {
          store.lockBasis(true, false);
          Season value = store.lockSeason(id).orElseThrow(ApiFailure::notFound);
          List<GamePatch> patches = store.lockedPatchesForSeason(id);
          value.change(number, displayName, actualName, seasonOrder(number), start, end);
          for (GamePatch patch : patches)
            patch.change(
                value,
                patch.getMajorNo(),
                patch.getMinorNo(),
                patch.getVersionName(),
                patchOrder(value, patch.getMajorNo(), patch.getMinorNo()),
                patch.getAppliedAt());
          return value;
        },
        true);
  }

  public GamePatch createPatch(
      Long seasonId, int major, int minor, String name, Instant appliedAt) {
    id(seasonId);
    patchInput(major, minor, name);
    return write(
        () -> {
          store.lockBasis(true, false);
          Season season =
              store.findSeason(seasonId).orElseThrow(() -> ApiFailure.invalidInput("seasonId"));
          GamePatch patch =
              new GamePatch(
                  season, major, minor, name, patchOrder(season, major, minor), seconds(appliedAt));
          store.persist(patch);
          return patch;
        },
        true);
  }

  public GamePatch updatePatch(
      Long id, Long seasonId, int major, int minor, String name, Instant appliedAt) {
    id(id);
    id(seasonId);
    patchInput(major, minor, name);
    return write(
        () -> {
          store.lockBasis(true, false);
          GamePatch patch = store.lockPatch(id).orElseThrow(ApiFailure::notFound);
          Season season =
              store.findSeason(seasonId).orElseThrow(() -> ApiFailure.invalidInput("seasonId"));
          patch.change(
              season, major, minor, name, patchOrder(season, major, minor), seconds(appliedAt));
          return patch;
        },
        true);
  }

  public Region createRegion(String displayName) {
    name(displayName, "displayName");
    return write(
        () -> {
          Region value = new Region(displayName);
          store.persist(value);
          return value;
        },
        false);
  }

  public Region renameRegion(Long id, String displayName) {
    id(id);
    name(displayName, "displayName");
    return write(
        () -> {
          Region value = store.lockRegion(id).orElseThrow(ApiFailure::notFound);
          value.change(displayName);
          return value;
        },
        false);
  }

  public ItemCategory createCategory(String name, Long parentId) {
    name(name, "name");
    if (parentId != null) id(parentId);
    return write(
        () -> {
          store.lockCategoryTree();
          ItemCategory parent = parent(parentId);
          checkCycle(null, parent);
          ItemCategory value = new ItemCategory(name, parent);
          store.persist(value);
          return value;
        },
        false);
  }

  public ItemCategory updateCategory(Long id, String name, Long parentId) {
    id(id);
    name(name, "name");
    if (parentId != null) id(parentId);
    return write(
        () -> {
          store.lockCategoryTree();
          ItemCategory value = store.lockCategory(id).orElseThrow(ApiFailure::notFound);
          ItemCategory parent = parent(parentId);
          checkCycle(id, parent);
          value.change(name, parent);
          return value;
        },
        false);
  }

  public ItemGrade createGrade(String name, long order) {
    name(name, "name");
    return write(
        () -> {
          ItemGrade value = new ItemGrade(name, order);
          store.persist(value);
          return value;
        },
        false);
  }

  public ItemGrade updateGrade(Long id, String name, long order) {
    id(id);
    name(name, "name");
    return write(
        () -> {
          ItemGrade value = store.lockGrade(id).orElseThrow(ApiFailure::notFound);
          value.change(name, order);
          return value;
        },
        false);
  }

  public WeaponType createWeaponType(String name, Long categoryId) {
    name(name, "name");
    id(categoryId);
    return write(
        () -> {
          ItemCategory category =
              store
                  .findCategory(categoryId)
                  .orElseThrow(() -> ApiFailure.invalidInput("categoryId"));
          WeaponType value = new WeaponType(name, category);
          store.persist(value);
          return value;
        },
        false);
  }

  public WeaponType updateWeaponType(Long id, String name, Long categoryId) {
    id(id);
    name(name, "name");
    id(categoryId);
    return write(
        () -> {
          WeaponType value = store.lockWeaponType(id).orElseThrow(ApiFailure::notFound);
          ItemCategory category =
              store
                  .findCategory(categoryId)
                  .orElseThrow(() -> ApiFailure.invalidInput("categoryId"));
          value.change(name, category);
          return value;
        },
        false);
  }

  /** A null map id registers a complete new snapshot; a non-null id corrects that snapshot. */
  public RegionMapVersion saveMap(
      Long mapId, Long fromPatchId, List<CatalogViews.MapRegion> entries) {
    if (mapId != null) id(mapId);
    id(fromPatchId);
    mapInput(entries);
    List<CatalogViews.MapRegion> snapshot = List.copyOf(entries);
    return write(
        () -> {
          store.lockBasis(false, true);
          GamePatch patch =
              store
                  .findPatch(fromPatchId)
                  .orElseThrow(() -> ApiFailure.invalidInput("fromGamePatchId"));
          List<Region> regions =
              snapshot.stream()
                  .map(entry ->
                      store
                          .findRegion(entry.regionId())
                          .orElseThrow(() -> ApiFailure.invalidInput("regionId")))
                  .toList();
          RegionMapVersion version;
          if (mapId == null) {
            version = new RegionMapVersion(patch);
            store.persist(version);
          } else {
            version = store.lockMapVersion(mapId).orElseThrow(ApiFailure::notFound);
            version.change(patch);
            store.deleteMapMembers(mapId);
          }
          for (int i = 0; i < snapshot.size(); i++) {
            CatalogViews.MapRegion entry = snapshot.get(i);
            store.persist(
                new RegionMapMember(version, regions.get(i), entry.name(), entry.sortOrder()));
          }
          return version;
        },
        true);
  }

  @Transactional(readOnly = true)
  public CatalogViews.RegionMap readMap(Long patchId) {
    id(patchId);
    return store.readMap(patchId).orElseThrow(ApiFailure::notFound);
  }

  @Transactional(readOnly = true)
  public <T extends CatalogRow> T get(Class<T> type, Long id) {
    id(id);
    return store.find(type, id).orElseThrow(ApiFailure::notFound);
  }

  @Transactional(readOnly = true)
  public <T extends CatalogRow> List<T> list(Class<T> type) {
    return store.list(type);
  }

  private <T> T write(Supplier<T> operation, boolean checkReferences) {
    try {
      T value = operation.get();
      store.flush();
      if (checkReferences) referenceChecks.forEach(CatalogReferenceCheck::verify);
      return value;
    } catch (RuntimeException failure) {
      throw CatalogErrors.translate(failure);
    }
  }

  private ItemCategory parent(Long id) {
    return id == null
        ? null
        : store.findCategory(id).orElseThrow(() -> ApiFailure.invalidInput("parentId"));
  }

  private static void checkCycle(Long changedId, ItemCategory parent) {
    Set<Long> seen = new HashSet<>();
    if (changedId != null) seen.add(changedId);
    for (ItemCategory value = parent; value != null; value = value.getParent())
      if (!seen.add(value.getId())) throw ApiFailure.invalidInput("parentId");
  }

  private static void mapInput(List<CatalogViews.MapRegion> entries) {
    if (entries == null) throw ApiFailure.invalidInput("regions");
    Set<Long> ids = new HashSet<>(), orders = new HashSet<>();
    Set<String> names = new HashSet<>();
    for (CatalogViews.MapRegion entry : entries) {
      if (entry == null) throw ApiFailure.invalidInput("regions");
      id(entry.regionId());
      name(entry.name(), "regions");
      if (entry.sortOrder() < 10
          || entry.sortOrder() % 10 != 0
          || !ids.add(entry.regionId())
          || !names.add(entry.name())
          || !orders.add(entry.sortOrder())) throw ApiFailure.invalidInput("regions");
    }
  }

  private static void seasonInput(
      int number, String display, String actual, LocalDate start, LocalDate end) {
    if (number < 1) throw ApiFailure.invalidInput("seasonNumber");
    name(display, "displayName");
    if (actual != null) name(actual, "seasonName");
    if (start != null && end != null && end.isBefore(start))
      throw ApiFailure.invalidInput("endDate");
  }

  private static void patchInput(int major, int minor, String actualName) {
    if (major < 0 || major > 99) throw ApiFailure.invalidInput("majorNo");
    if (minor < 0 || minor > 99) throw ApiFailure.invalidInput("minorNo");
    if (actualName != null) name(actualName, "versionName");
  }

  private static long seasonOrder(int number) {
    return (long) number + 9;
  }

  private static long patchOrder(Season season, int major, int minor) {
    return season.getSortOrder() * 10000 + major * 100L + minor;
  }

  private static Instant seconds(Instant value) {
    return value == null ? null : value.truncatedTo(ChronoUnit.SECONDS);
  }

  private static void id(Long id) {
    if (id == null || id <= 0) throw ApiFailure.invalidInput("id");
  }

  private static void name(String value, String field) {
    if (value == null || value.replace(" ", "").isEmpty()) throw ApiFailure.invalidInput(field);
  }
}
