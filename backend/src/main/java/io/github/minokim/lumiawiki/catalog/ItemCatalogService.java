package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.math.BigDecimal;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeSet;
import java.util.function.Supplier;
import java.util.regex.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

/** Internal storage for an exact item version, its stats and its skill links. */
@Service
@Transactional(isolation = Isolation.READ_COMMITTED)
public class ItemCatalogService {
  private static final Pattern WHITE_SPACE = Pattern.compile("\\p{IsWhite_Space}*");

  public record SkillInput(Long skillId, Long skillVersionId, String description) {}

  public record StatInput(Long statTypeId, BigDecimal value) {}

  public record StatValue(String statTypeId, String value) {}

  /** A supplied change with a null value marks the maximum as unconfirmed. */
  public record MaxStackChange(Integer value) {}

  public record Material(Long itemId, Long itemVersionId, String requestKey) {
    public Material(Long itemId, Long itemVersionId) {
      this(itemId, itemVersionId, null);
    }

    public Material(String requestKey) {
      this(null, null, requestKey);
    }
  }

  public record Recipe(Material materialA, Material materialB, Integer outputCount) {}

  /** An omitted change retains the recipe. A supplied change with a null value clears it. */
  public record RecipeChange(Recipe value) {}

  /** Omit the group to retain it, or supply nulls to clear individual values. */
  public record Delivery(Integer acquireCount, Boolean deliverable, Integer price) {}

  public record AcquisitionInput(AcquisitionMethod method, Long regionId, Integer spawnCount) {}

  public record Acquisition(
      Long id,
      Long itemId,
      Long itemVersionId,
      Long gamePatchId,
      AcquisitionMethod method,
      Long regionId,
      Integer spawnCount,
      List<String> warnings) {}

  /** A request key is required for a new item and can be referenced by recipes in the same call. */
  public record PatchItem(
      String requestKey, Long itemId, Boolean searchable, VersionInput version) {}

  /**
   * Omitted stats, skills and max-stack changes retain their values during a correction and inherit
   * from the preceding version during an append. An empty list explicitly clears it.
   */
  public record VersionInput(
      Long categoryId,
      Long gradeId,
      String name,
      String imagePath,
      Boolean deleted,
      MaxStackChange maxStackChange,
      List<StatInput> stats,
      List<SkillInput> skills,
      RecipeChange recipeChange,
      Delivery delivery) {
    public VersionInput(
        Long categoryId,
        Long gradeId,
        String name,
        String imagePath,
        Boolean deleted,
        MaxStackChange maxStackChange,
        List<StatInput> stats,
        List<SkillInput> skills) {
      this(
          categoryId, gradeId, name, imagePath, deleted, maxStackChange, stats, skills, null, null);
    }
  }

  public record SkillLink(
      Long id,
      Long itemVersionPatchId,
      Long skillId,
      Long skillVersionId,
      Long skillFromGamePatchId,
      String description,
      String originalDescription) {
    public String displayDescription() {
      return description == null ? "" : description;
    }
  }

  public record Version(
      Long id,
      Long itemId,
      Long fromGamePatchId,
      Long categoryId,
      Long gradeId,
      EquipmentSlot equipmentSlot,
      Integer maxStackSize,
      String name,
      String imagePath,
      boolean deleted,
      boolean searchable,
      String statJson,
      List<StatValue> stats,
      List<SkillLink> skills,
      Recipe recipe,
      Delivery delivery,
      List<Acquisition> acquisitions) {
    public Version {
      stats = List.copyOf(stats);
      skills = List.copyOf(skills);
      acquisitions = List.copyOf(acquisitions);
    }
  }

  public record SkillVersion(
      Long id, Long skillId, Long fromGamePatchId, String internalName, String description) {}

  private record ResolvedSkill(ItemSkillDefinitionVersion version, String description) {}

  private record ResolvedStat(StatType type, BigDecimal value) {}

  private record LockedPatchPlan(ItemPatchPlan plan, Map<Long, Item> items) {}

  private record Change(String operation, ApiFailure.Target target) {
    static Change of(String operation, String type, Long id) {
      return new Change(
          operation, new ApiFailure.Target(type, id == null || id < 1 ? null : id.toString()));
    }

    ApiFailure invalid(String field) {
      return invalid(field, "Invalid", "입력값을 확인해 주세요.");
    }

    ApiFailure invalid(String field, String code, String message) {
      return ApiFailure.invalidInput(
          operation, target, new ApiFailure.FieldError(field, code, message));
    }
  }

  private final CommonCatalogStore store;
  private final List<HuntingAcquisitionCheck> huntingChecks;

  public ItemCatalogService(CommonCatalogStore store) {
    this(store, List.of());
  }

  @Autowired
  public ItemCatalogService(CommonCatalogStore store, List<HuntingAcquisitionCheck> huntingChecks) {
    this.store = store;
    this.huntingChecks = List.copyOf(huntingChecks);
  }

  public Version createItem(Boolean searchable, Long fromGamePatchId, VersionInput input) {
    Change change = Change.of("CREATE_ITEM", "ITEM", null);
    validate(input, change);
    lockVersionBasis();
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
    lockExplicitMaterialItems(input, change);
    ItemVersion result =
        write(
            change,
            () -> {
              Item item = new Item(searchable == null || searchable);
              store.persist(item);
              return newVersion(item, patch, input, null, change);
            });
    return view(result);
  }

  public Version createItemVersion(Long itemId, Long fromGamePatchId, VersionInput input) {
    Change change = Change.of("CREATE_ITEM_VERSION", "ITEM_VERSION", null);
    validate(input, change);
    requireId(itemId, "itemId", change);
    lockVersionBasis();
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
    return writePatchItems(
            patch, List.of(new PatchItem(null, itemId, null, input)), true, false, change)
        .getFirst();
  }

  public Version updateItemVersion(Long versionId, VersionInput input) {
    Change change = Change.of("UPDATE_ITEM_VERSION", "ITEM_VERSION", versionId);
    validate(input, change);
    requireId(versionId, "id", change);
    lockVersionBasis();
    Long itemId = store.findItemIdByVersion(versionId).orElseThrow(ApiFailure::notFound);
    if (input.recipeChange() == null) {
      lockItem(itemId, change);
    } else {
      Long patchId = store.findPatchIdByItemVersion(versionId).orElseThrow(ApiFailure::notFound);
      GamePatch patch = reference(GamePatch.class, patchId, "fromGamePatchId", change);
      lockPatchPlan(patch, List.of(new PatchItem(null, itemId, null, input)), change);
    }
    ItemVersion version =
        store.locked(ItemVersion.class, versionId).orElseThrow(ApiFailure::notFound);
    return view(write(change, () -> correctVersion(version, input, change)));
  }

  public Version recordItemExistence(Long itemId, Long fromGamePatchId, boolean deleted) {
    Change change = Change.of("CREATE_ITEM_VERSION", "ITEM_VERSION", null);
    requireId(itemId, "itemId", change);
    lockVersionBasis();
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
    VersionInput input = new VersionInput(null, null, null, null, deleted, null, null, null);
    return writePatchItems(
            patch, List.of(new PatchItem(null, itemId, null, input)), true, true, change)
        .getFirst();
  }

  public List<Version> savePatchItems(Long patchId, List<PatchItem> inputs) {
    Change change = Change.of("SAVE_PATCH_ITEMS", "GAME_PATCH", patchId);
    if (inputs == null || inputs.isEmpty()) throw change.invalid("changes");
    for (PatchItem input : inputs) {
      if (input == null) throw change.invalid("changes");
      validate(input.version(), change);
    }
    lockVersionBasis();
    GamePatch patch = reference(GamePatch.class, patchId, "gamePatchId", change);
    return writePatchItems(patch, List.copyOf(inputs), false, false, change);
  }

  private LockedPatchPlan lockPatchPlan(GamePatch patch, List<PatchItem> inputs, Change change) {
    var initial =
        ItemPatchPlan.build(patch.getId(), inputs, store.itemVersionsAtPatch(patch.getSortOrder()));
    Map<Long, Item> locked = new LinkedHashMap<>();
    for (Long id : initial.itemLocks()) locked.put(id, lockItem(id, change));
    var plan =
        ItemPatchPlan.build(patch.getId(), inputs, store.itemVersionsAtPatch(patch.getSortOrder()));
    if (!locked.keySet().containsAll(plan.itemLocks())) {
      throw change.invalid("changes", "ITEM_RELATIONS_CHANGED", "재료 사용처가 바뀌었습니다. 다시 시도해 주세요.");
    }
    return new LockedPatchPlan(plan, locked);
  }

  private List<Version> writePatchItems(
      GamePatch patch,
      List<PatchItem> inputs,
      boolean appendOnly,
      boolean existenceOnly,
      Change change) {
    LockedPatchPlan locked = lockPatchPlan(patch, inputs, change);
    ItemPatchPlan plan = locked.plan();
    return write(
        change,
        () -> {
          Map<ItemPatchPlan.Key, ItemVersion> saved = new LinkedHashMap<>();
          for (ItemPatchPlan.Entry entry : plan.ordered()) {
            Long itemId = entry.key().itemId();
            Item item = locked.items().get(itemId);
            if (item == null) {
              Boolean searchable = entry.input().searchable();
              item = new Item(searchable == null || searchable);
              store.persist(item);
            } else if (entry.input() != null && entry.input().searchable() != null) {
              item.setSearchable(entry.input().searchable());
            }
            ItemVersion previous =
                entry.previous() == null
                    ? itemId == null
                        ? null
                        : store.findPreviousItemVersion(itemId, patch.getSortOrder()).orElse(null)
                    : reference(
                        ItemVersion.class, entry.previous().versionId(), "itemVersionId", change);
            boolean samePatch =
                previous != null && previous.getFromGamePatch().getId().equals(patch.getId());
            if (samePatch && appendOnly && entry.input() != null)
              throw change.invalid("fromGamePatchId");

            Recipe recipe =
                entry.materialA() == null
                    ? null
                    : new Recipe(
                        resolvePatchMaterial(entry.materialA(), plan, saved, change),
                        resolvePatchMaterial(entry.materialB(), plan, saved, change),
                        entry.outputCount());
            ItemVersion version;
            if (entry.input() == null && samePatch) {
              previous.changeRecipe(recipe);
              version = previous;
            } else {
              VersionInput input;
              if (entry.input() == null || existenceOnly) {
                if (previous == null) throw change.invalid("fromGamePatchId");
                boolean deleted =
                    entry.input() == null
                        ? previous.isDeleted()
                        : entry.input().version().deleted();
                input =
                    new VersionInput(
                        previous.getCategory().getId(),
                        gradeId(previous),
                        previous.getName(),
                        previous.getImagePath(),
                        deleted,
                        null,
                        null,
                        null);
              } else {
                input = entry.input().version();
              }
              VersionInput resolved =
                  new VersionInput(
                      input.categoryId(),
                      input.gradeId(),
                      input.name(),
                      input.imagePath(),
                      input.deleted(),
                      input.maxStackChange(),
                      input.stats(),
                      input.skills(),
                      new RecipeChange(recipe),
                      input.delivery());
              version =
                  samePatch
                      ? correctVersion(previous, resolved, change)
                      : newVersion(item, patch, resolved, previous, change);
            }
            saved.put(entry.key(), version);
            store.flush();
          }
          return plan.requested().stream().map(saved::get).map(this::view).toList();
        });
  }

  private static Material resolvePatchMaterial(
      ItemPatchPlan.Key key,
      ItemPatchPlan plan,
      Map<ItemPatchPlan.Key, ItemVersion> saved,
      Change change) {
    ItemVersion version = saved.get(key);
    if (version != null) return new Material(version.getItem().getId(), version.getId());
    var active = plan.active().get(key.itemId());
    if (active == null) throw change.invalid("recipe");
    return new Material(key.itemId(), active.versionId());
  }

  private void lockExplicitMaterialItems(VersionInput input, Change change) {
    var ids = new TreeSet<Long>();
    Recipe recipe = input.recipeChange() == null ? null : input.recipeChange().value();
    if (recipe != null) {
      for (Material material : new Material[] {recipe.materialA(), recipe.materialB()}) {
        if (material == null || material.requestKey() != null) throw change.invalid("recipe");
        requireId(material.itemId(), "recipe.itemId", change);
        ids.add(material.itemId());
      }
    }
    for (Long id : ids) lockItem(id, change);
  }

  private ItemVersion correctVersion(ItemVersion version, VersionInput input, Change change) {
    ItemCategory category = reference(ItemCategory.class, input.categoryId(), "categoryId", change);
    ItemGrade grade = reference(ItemGrade.class, input.gradeId(), "gradeId", change);
    boolean deleted = input.deleted() == null ? version.isDeleted() : input.deleted();
    version.change(category, input.name(), input.imagePath(), deleted);
    version.changeDetails(grade, nextStackSize(input.maxStackChange(), version.getMaxStackSize()));
    applyRelations(version, version, input, change);
    if (deleted) version.getAcquisitions().clear();
    if (input.skills() != null) replaceSkills(version, input.skills(), change);
    if (input.stats() != null) replaceStats(version, input.stats(), change);
    return version;
  }

  public void setItemSearchable(Long itemId, boolean searchable) {
    Change change = Change.of("UPDATE_ITEM", "ITEM", itemId);
    Item item = lockItem(itemId, change);
    item.setSearchable(searchable);
    store.flush();
  }

  @Transactional(readOnly = true)
  public Version getItemVersion(Long id) {
    requireId(id);
    return view(store.readItemVersion(id).orElseThrow(ApiFailure::notFound));
  }

  public Acquisition createAcquisition(Long versionId, AcquisitionInput input) {
    Change change = Change.of("CREATE_ITEM_ACQUISITION", "ITEM_VERSION", versionId);
    ItemVersion owner = lockAcquisitionOwner(versionId, change);
    return acquisitionView(
        writeAcquisition(
            change,
            () -> {
              validateAcquisition(owner, null, input, change);
              var row =
                  new ItemAcquisition(owner, input.method(), input.regionId(), input.spawnCount());
              owner.getAcquisitions().add(row);
              store.persist(row);
              return row;
            }));
  }

  public Acquisition updateAcquisition(Long versionId, Long id, AcquisitionInput input) {
    Change change = Change.of("UPDATE_ITEM_ACQUISITION", "ITEM_ACQUISITION", id);
    ItemVersion owner = lockAcquisitionOwner(versionId, change);
    return acquisitionView(
        writeAcquisition(
            change,
            () -> {
              ItemAcquisition row = acquisition(owner, id, change);
              validateAcquisition(owner, id, input, change);
              row.change(input.method(), input.regionId(), input.spawnCount());
              return row;
            }));
  }

  public void deleteAcquisition(Long versionId, Long id) {
    Change change = Change.of("DELETE_ITEM_ACQUISITION", "ITEM_ACQUISITION", id);
    ItemVersion owner = lockAcquisitionOwner(versionId, change);
    write(change, () -> owner.getAcquisitions().remove(acquisition(owner, id, change)));
  }

  private ItemVersion lockAcquisitionOwner(Long versionId, Change change) {
    requireId(versionId, "itemVersionId", change);
    store.lockBasis(false, false);
    Long itemId = store.findItemIdByVersion(versionId).orElseThrow(ApiFailure::notFound);
    lockItem(itemId, change);
    return store.locked(ItemVersion.class, versionId).orElseThrow(ApiFailure::notFound);
  }

  private static ItemAcquisition acquisition(ItemVersion owner, Long id, Change change) {
    requireId(id, "id", change);
    return owner.getAcquisitions().stream()
        .filter(row -> id.equals(row.getId()))
        .findFirst()
        .orElseThrow(ApiFailure::notFound);
  }

  private void validateAcquisition(
      ItemVersion owner, Long excludedId, AcquisitionInput input, Change change) {
    if (owner.isDeleted()) throw change.invalid("itemVersionId");
    if (input == null || input.method() == null) throw change.invalid("method");
    Long regionId = input.regionId();
    if (input.method() == AcquisitionMethod.CHEST && regionId == null)
      throw change.invalid("regionId");
    if (input.method() != AcquisitionMethod.CHEST && input.spawnCount() != null)
      throw change.invalid("spawnCount");
    if (regionId != null) {
      reference(Region.class, regionId, "regionId", change);
      if (store.acquisitionRegionUnavailable(owner.getId(), regionId))
        throw change.invalid("regionId");
    }
    boolean overlaps =
        owner.getAcquisitions().stream()
            .filter(row -> !Objects.equals(excludedId, row.getId()) || excludedId == null)
            .filter(row -> row.getMethod() == input.method())
            .anyMatch(row ->
                row.getRegionId() == null
                    || regionId == null
                    || regionId.equals(row.getRegionId()));
    if (overlaps) throw change.invalid("regionId");
  }

  private Acquisition acquisitionView(ItemAcquisition row) {
    Long versionId = row.getItemVersion().getId();
    boolean differs =
        row.getMethod() == AcquisitionMethod.HUNTING
            && huntingChecks.stream()
                .anyMatch(check -> check.differs(versionId, row.getRegionId()));
    return new Acquisition(
        row.getId(),
        row.getItemId(),
        versionId,
        row.getGamePatchId(),
        row.getMethod(),
        row.getRegionId(),
        row.getSpawnCount(),
        differs ? List.of("HUNTING_DETAIL_MISMATCH") : List.of());
  }

  public StatType createStatType(String name, Long sortOrder) {
    Change change = Change.of("CREATE_STAT_TYPE", "STAT_TYPE", null);
    validateStatType(name, sortOrder, change);
    store.lockStatTypeOrder();
    return write(
        change,
        () -> {
          StatType value = new StatType(name, sortOrder);
          store.persist(value);
          return value;
        });
  }

  public StatType updateStatType(Long id, String name, Long sortOrder) {
    Change change = Change.of("UPDATE_STAT_TYPE", "STAT_TYPE", id);
    requireId(id, "id", change);
    validateStatType(name, sortOrder, change);
    store.lockStatTypeOrder();
    return write(
        change,
        () -> {
          StatType value = store.locked(StatType.class, id).orElseThrow(ApiFailure::notFound);
          boolean orderChanged = value.getSortOrder() != sortOrder;
          value.change(name, sortOrder);
          if (orderChanged) {
            store.lockVersionsUsingStatType(id).forEach(ItemVersion::rebuildStatCache);
          }
          return value;
        });
  }

  @Transactional(readOnly = true)
  public List<StatType> listStatTypes() {
    return store.list(StatType.class);
  }

  public Long createSkillDefinition() {
    ItemSkillDefinition definition = new ItemSkillDefinition();
    store.persist(definition);
    return definition.getId();
  }

  public SkillVersion createSkillVersion(
      Long skillId, Long fromGamePatchId, String internalName, String description) {
    Change change = Change.of("CREATE_SKILL_VERSION", "SKILL_VERSION", null);
    validateSkillText(internalName, description, change);
    ItemSkillDefinition skill = reference(ItemSkillDefinition.class, skillId, "skillId", change);
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
    return skillView(
        write(
            change,
            () -> {
              var version = new ItemSkillDefinitionVersion(skill, patch, internalName, description);
              store.persist(version);
              return version;
            }));
  }

  public SkillVersion updateSkillVersion(Long id, String internalName, String description) {
    Change change = Change.of("UPDATE_SKILL_VERSION", "SKILL_VERSION", id);
    requireId(id, "id", change);
    validateSkillText(internalName, description, change);
    return skillView(
        write(
            change,
            () -> {
              var version =
                  store
                      .locked(ItemSkillDefinitionVersion.class, id)
                      .orElseThrow(ApiFailure::notFound);
              version.change(internalName, description);
              return version;
            }));
  }

  @Transactional(readOnly = true)
  public SkillVersion getSkillVersion(Long id) {
    requireId(id);
    return skillView(
        store.find(ItemSkillDefinitionVersion.class, id).orElseThrow(ApiFailure::notFound));
  }

  private ItemVersion newVersion(
      Item item, GamePatch patch, VersionInput input, ItemVersion previous, Change change) {
    ItemCategory category = reference(ItemCategory.class, input.categoryId(), "categoryId", change);
    // Complete inputs require a grade. An existence-only version can inherit an unknown grade.
    ItemGrade grade =
        input.gradeId() == null
            ? null
            : reference(ItemGrade.class, input.gradeId(), "gradeId", change);
    ItemVersion version =
        new ItemVersion(
            item,
            patch,
            category,
            input.name(),
            input.imagePath(),
            Boolean.TRUE.equals(input.deleted()));
    version.changeDetails(
        grade,
        nextStackSize(
            input.maxStackChange(), previous == null ? null : previous.getMaxStackSize()));
    applyRelations(version, previous, input, change);
    if (input.skills() != null) {
      replaceSkills(version, input.skills(), change);
    } else if (previous != null) {
      replaceSkills(version, copySkills(previous), change);
    }
    if (input.stats() != null) {
      replaceStats(version, input.stats(), change);
    } else if (previous != null) {
      replaceStats(version, copyStats(previous), change);
    }
    store.persist(version);
    if (previous != null && !version.isDeleted()) {
      for (ItemAcquisition row : previous.getAcquisitions()) {
        if (row.getRegionId() != null
            && store.acquisitionRegionUnavailable(version.getId(), row.getRegionId())) {
          throw change.invalid("regionId");
        }
        version
            .getAcquisitions()
            .add(
                new ItemAcquisition(
                    version, row.getMethod(), row.getRegionId(), row.getSpawnCount()));
      }
    }
    return version;
  }

  private void applyRelations(
      ItemVersion version, ItemVersion previous, VersionInput input, Change change) {
    Recipe recipe =
        input.recipeChange() == null
            ? previous == null ? null : previous.recipe()
            : input.recipeChange().value();
    if (version.isDeleted()) recipe = null;
    if (recipe != null) {
      Material a = validateMaterial(recipe.materialA(), version, "recipe.materialA", change);
      Material b = validateMaterial(recipe.materialB(), version, "recipe.materialB", change);
      if (recipe.outputCount() == null) throw change.invalid("recipe.outputCount");
      if (a.itemId().equals(b.itemId())) throw change.invalid("recipe.materialB");
    }
    version.changeRecipe(recipe);
    Delivery delivery =
        input.delivery() != null ? input.delivery() : previous == null ? null : previous.delivery();
    if (delivery != null) {
      if (delivery.price() != null && !Boolean.TRUE.equals(delivery.deliverable())) {
        throw change.invalid("delivery.price");
      }
      version.changeDelivery(delivery);
    }
  }

  private Material validateMaterial(
      Material material, ItemVersion owner, String field, Change change) {
    if (material == null || material.requestKey() != null) throw change.invalid(field);
    requireId(material.itemId(), field + ".itemId", change);
    ItemVersion target =
        reference(ItemVersion.class, material.itemVersionId(), field + ".itemVersionId", change);
    if (!material.itemId().equals(target.getItem().getId())
        || owner.getItem().getId().equals(material.itemId())
        || !material
            .itemVersionId()
            .equals(
                store
                    .findEffectiveItemVersionId(
                        material.itemId(), owner.getFromGamePatch().getSortOrder())
                    .orElse(null))) {
      throw change.invalid(field + ".itemVersionId");
    }
    return material;
  }

  private void lockVersionBasis() {
    store.lockBasis(false, false);
    store.lockStatTypesForStorage();
  }

  private static Integer nextStackSize(MaxStackChange change, Integer previous) {
    return change == null ? previous : change.value();
  }

  private Item lockItem(Long id, Change change) {
    requireId(id, "itemId", change);
    return store.locked(Item.class, id).orElseThrow(ApiFailure::notFound);
  }

  private void replaceSkills(ItemVersion owner, List<SkillInput> inputs, Change change) {
    var replacements = new LinkedHashMap<Long, ResolvedSkill>();
    for (int index = 0; index < inputs.size(); index++) {
      SkillInput input = inputs.get(index);
      String field = "skills[" + index + "]";
      if (input == null) throw change.invalid(field);
      requireId(input.skillId(), field + ".skillId", change);
      if (replacements.containsKey(input.skillId())) {
        throw change.invalid(field + ".skillId", "DUPLICATE_SKILL_LINK", "같은 스킬은 한 번만 연결할 수 있습니다.");
      }

      String versionField = field + ".skillVersionId";
      ItemSkillDefinitionVersion version =
          reference(ItemSkillDefinitionVersion.class, input.skillVersionId(), versionField, change);
      if (!Objects.equals(input.skillId(), version.getDefinition().getId())) {
        throw change.invalid(versionField, "SKILL_VERSION_OWNER_MISMATCH", "선택한 스킬의 버전이 아닙니다.");
      }
      if (version.getFromGamePatch().getSortOrder() > owner.getFromGamePatch().getSortOrder()) {
        throw change.invalid(
            versionField, "SKILL_VERSION_AFTER_ITEM_PATCH", "아이템의 기준 패치에서 사용할 수 없는 스킬 버전입니다.");
      }
      replacements.put(input.skillId(), new ResolvedSkill(version, input.description()));
    }

    var links = owner.getSkillLinks();
    links.removeIf(link -> {
      ResolvedSkill replacement = replacements.remove(link.getSkillDefinition().getId());
      if (replacement == null) return true;
      link.change(replacement.version(), replacement.description());
      return false;
    });
    for (ResolvedSkill skill : replacements.values()) {
      links.add(new ItemVersionSkillLink(owner, skill.version(), skill.description()));
    }
  }

  private static List<SkillInput> copySkills(ItemVersion previous) {
    return previous.getSkillLinks().stream()
        .map(link ->
            new SkillInput(
                link.getSkillDefinition().getId(),
                link.getSkillVersion().getId(),
                link.getDescription()))
        .toList();
  }

  private void replaceStats(ItemVersion owner, List<StatInput> inputs, Change change) {
    var replacements = new LinkedHashMap<Long, ResolvedStat>();
    for (int index = 0; index < inputs.size(); index++) {
      StatInput input = inputs.get(index);
      String field = "stats[" + index + "]";
      if (input == null) throw change.invalid(field);
      if (input.value() == null) throw change.invalid(field + ".value");
      String typeField = field + ".statTypeId";
      requireId(input.statTypeId(), typeField, change);
      if (replacements.containsKey(input.statTypeId())) {
        throw change.invalid(typeField, "DUPLICATE_STAT_TYPE", "같은 능력치 종류는 한 번만 저장할 수 있습니다.");
      }
      StatType type = reference(StatType.class, input.statTypeId(), typeField, change);
      replacements.put(input.statTypeId(), new ResolvedStat(type, input.value()));
    }

    var stats = owner.getStats();
    stats.removeIf(stat -> {
      ResolvedStat replacement = replacements.remove(stat.getStatType().getId());
      if (replacement == null) return true;
      stat.setValue(replacement.value());
      return false;
    });
    for (ResolvedStat stat : replacements.values()) {
      stats.add(new ItemStat(owner, stat.type(), stat.value()));
    }
    owner.rebuildStatCache();
  }

  private static List<StatInput> copyStats(ItemVersion previous) {
    return previous.getStats().stream()
        .map(stat -> new StatInput(stat.getStatType().getId(), stat.getValue()))
        .toList();
  }

  private static Long gradeId(ItemVersion version) {
    return version.getGrade() == null ? null : version.getGrade().getId();
  }

  private Version view(ItemVersion version) {
    List<SkillLink> skills =
        version.getSkillLinks().stream()
            .map(link ->
                new SkillLink(
                    link.getId(),
                    link.getItemVersionPatch().getId(),
                    link.getSkillDefinition().getId(),
                    link.getSkillVersion().getId(),
                    link.getSkillVersion().getFromGamePatch().getId(),
                    link.getDescription(),
                    link.getSkillVersion().getDescription()))
            .toList();
    return new Version(
        version.getId(),
        version.getItem().getId(),
        version.getFromGamePatch().getId(),
        version.getCategory().getId(),
        gradeId(version),
        store.readEquipmentSlot(version.getCategory().getId()),
        version.getMaxStackSize(),
        version.getName(),
        version.getImagePath(),
        version.isDeleted(),
        version.getItem().isSearchable(),
        version.getStatJson(),
        ItemStatCache.read(version.getStatJson()),
        skills,
        version.recipe(),
        version.delivery(),
        version.getAcquisitions().stream().map(this::acquisitionView).toList());
  }

  private static SkillVersion skillView(ItemSkillDefinitionVersion version) {
    return new SkillVersion(
        version.getId(),
        version.getDefinition().getId(),
        version.getFromGamePatch().getId(),
        version.getInternalName(),
        version.getDescription());
  }

  private <T extends CatalogRow> T reference(Class<T> type, Long id, String field, Change change) {
    requireId(id, field, change);
    return store.find(type, id).orElseThrow(() -> change.invalid(field));
  }

  private <T> T write(Change change, Supplier<T> action) {
    try {
      T result = action.get();
      store.flush();
      return result;
    } catch (RuntimeException failure) {
      throw CatalogErrors.translate(failure, change::invalid);
    }
  }

  private <T> T writeAcquisition(Change change, Supplier<T> action) {
    try {
      return write(change, action);
    } catch (RuntimeException failure) {
      throw CatalogErrors.translateAcquisition(failure, change::invalid);
    }
  }

  private static void validate(VersionInput input, Change change) {
    if (input == null) throw change.invalid("version");
    requireId(input.categoryId(), "categoryId", change);
    if (blank(input.name())) throw change.invalid("name");
    requireId(input.gradeId(), "gradeId", change);
    Integer maxStackSize = nextStackSize(input.maxStackChange(), null);
    if (maxStackSize != null && maxStackSize <= 0) throw change.invalid("maxStackSize");
    String imagePath = input.imagePath();
    if (imagePath != null
        && (imagePath.indexOf('\\') >= 0
            || imagePath.indexOf(':') >= 0
            || Arrays.stream(imagePath.split("/", -1))
                .anyMatch(
                    segment -> blank(segment) || segment.equals(".") || segment.equals("..")))) {
      throw change.invalid("imagePath");
    }
  }

  private static void validateSkillText(String name, String description, Change change) {
    if (blank(name)) throw change.invalid("internalName");
    if (blank(description)) {
      throw change.invalid("description", "SKILL_DESCRIPTION_REQUIRED", "스킬 설명 원문을 입력해 주세요.");
    }
  }

  private static void validateStatType(String name, Long sortOrder, Change change) {
    if (blank(name)) throw change.invalid("name");
    if (sortOrder == null) throw change.invalid("sortOrder");
  }

  private static boolean blank(String value) {
    return value == null || WHITE_SPACE.matcher(value).matches();
  }

  private static void requireId(Long id, String field, Change change) {
    if (id == null || id <= 0) throw change.invalid(field);
  }

  private static void requireId(Long id) {
    if (id == null || id <= 0) throw ApiFailure.invalidInput("id");
  }
}
