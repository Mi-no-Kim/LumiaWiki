package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.math.BigDecimal;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Objects;
import java.util.function.Supplier;
import java.util.regex.Pattern;
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
      List<SkillInput> skills) {}

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
      List<SkillLink> skills) {
    public Version {
      stats = List.copyOf(stats);
      skills = List.copyOf(skills);
    }
  }

  public record SkillVersion(
      Long id, Long skillId, Long fromGamePatchId, String internalName, String description) {}

  private record ResolvedSkill(ItemSkillDefinitionVersion version, String description) {}

  private record ResolvedStat(StatType type, BigDecimal value) {}

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

  public ItemCatalogService(CommonCatalogStore store) {
    this.store = store;
  }

  public Version createItem(Boolean searchable, Long fromGamePatchId, VersionInput input) {
    Change change = Change.of("CREATE_ITEM", "ITEM", null);
    validate(input, change);
    lockVersionBasis();
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
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
    lockVersionBasis();
    Item item = lockItem(itemId, change);
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
    ItemVersion previous = store.findPreviousItemVersion(itemId, patch.getSortOrder()).orElse(null);
    return view(write(change, () -> newVersion(item, patch, input, previous, change)));
  }

  public Version updateItemVersion(Long versionId, VersionInput input) {
    Change change = Change.of("UPDATE_ITEM_VERSION", "ITEM_VERSION", versionId);
    validate(input, change);
    requireId(versionId, "id", change);
    lockVersionBasis();
    Long itemId = store.findItemIdByVersion(versionId).orElseThrow(ApiFailure::notFound);
    lockItem(itemId, change);
    ItemVersion version =
        store.locked(ItemVersion.class, versionId).orElseThrow(ApiFailure::notFound);
    ItemCategory category = reference(ItemCategory.class, input.categoryId(), "categoryId", change);
    ItemGrade grade = reference(ItemGrade.class, input.gradeId(), "gradeId", change);
    return view(
        write(
            change,
            () -> {
              boolean deleted = input.deleted() == null ? version.isDeleted() : input.deleted();
              version.change(category, input.name(), input.imagePath(), deleted);
              version.changeDetails(
                  grade, nextStackSize(input.maxStackChange(), version.getMaxStackSize()));
              if (input.skills() != null) replaceSkills(version, input.skills(), change);
              if (input.stats() != null) replaceStats(version, input.stats(), change);
              return version;
            }));
  }

  public Version recordItemExistence(Long itemId, Long fromGamePatchId, boolean deleted) {
    Change change = Change.of("CREATE_ITEM_VERSION", "ITEM_VERSION", null);
    lockVersionBasis();
    Item item = lockItem(itemId, change);
    GamePatch patch = reference(GamePatch.class, fromGamePatchId, "fromGamePatchId", change);
    ItemVersion previous =
        store
            .findPreviousItemVersion(itemId, patch.getSortOrder())
            .orElseThrow(() -> change.invalid("fromGamePatchId"));
    VersionInput input =
        new VersionInput(
            previous.getCategory().getId(),
            gradeId(previous),
            previous.getName(),
            previous.getImagePath(),
            deleted,
            null,
            null,
            null);
    return view(write(change, () -> newVersion(item, patch, input, previous, change)));
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
    return version;
  }

  private void lockVersionBasis() {
    store.lockGamePatch(false);
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
        skills);
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
