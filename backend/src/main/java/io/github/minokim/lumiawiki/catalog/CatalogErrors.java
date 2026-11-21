package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.util.Map;
import java.util.function.Function;
import org.hibernate.exception.ConstraintViolationException;

public final class CatalogErrors {
  private CatalogErrors() {}

  private record Expected(String state, String field) {}

  private static final Map<String, Expected> EXPECTED =
      Map.ofEntries(
          Map.entry("uq_season_number", new Expected("23505", "seasonNumber")),
          Map.entry("ck_season_number", new Expected("23514", "seasonNumber")),
          Map.entry("ck_season_order", new Expected("23514", "seasonNumber")),
          Map.entry("ck_season_dates", new Expected("23514", "endDate")),
          Map.entry("uq_game_patch_number", new Expected("23505", "patchNumber")),
          Map.entry("uq_game_patch_order", new Expected("23505", "patchNumber")),
          Map.entry("ck_game_patch_major", new Expected("23514", "majorNo")),
          Map.entry("ck_game_patch_minor", new Expected("23514", "minorNo")),
          Map.entry("fk_game_patch_season", new Expected("23503", "seasonId")),
          Map.entry("uq_region_display_name", new Expected("23505", "displayName")),
          Map.entry("uq_item_category_parent_name", new Expected("23505", "name")),
          Map.entry("fk_item_category_parent", new Expected("23503", "parentId")),
          Map.entry("ck_item_category_parent", new Expected("23514", "parentId")),
          Map.entry("uq_item_grade_name", new Expected("23505", "name")),
          Map.entry("uq_item_grade_order", new Expected("23505", "sortOrder")),
          Map.entry("uq_weapon_type_name", new Expected("23505", "name")),
          Map.entry("uq_weapon_type_category", new Expected("23505", "categoryId")),
          Map.entry("fk_weapon_type_category", new Expected("23503", "categoryId")),
          Map.entry("uq_region_map_start", new Expected("23505", "fromGamePatchId")),
          Map.entry("fk_region_map_start", new Expected("23503", "fromGamePatchId")),
          Map.entry("uq_region_map_member_region", new Expected("23505", "regions")),
          Map.entry("uq_region_map_member_name", new Expected("23505", "regions")),
          Map.entry("uq_region_map_member_order", new Expected("23505", "regions")),
          Map.entry("ck_region_map_member_order", new Expected("23514", "regions")),
          Map.entry("fk_region_map_member_map", new Expected("23503", "mapVersionId")),
          Map.entry("fk_region_map_member_region", new Expected("23503", "regionId")),
          Map.entry("uq_item_version_item_patch", new Expected("23505", "fromGamePatchId")),
          Map.entry("fk_item_version_item", new Expected("23503", "itemId")),
          Map.entry("fk_item_version_patch", new Expected("23503", "fromGamePatchId")),
          Map.entry("fk_item_version_category", new Expected("23503", "categoryId")),
          Map.entry("fk_item_version_grade", new Expected("23503", "gradeId")),
          Map.entry("ck_item_version_equipment_slot", new Expected("23514", "equipmentSlot")),
          Map.entry("ck_item_version_max_stack_size", new Expected("23514", "maxStackSize")),
          Map.entry("ck_item_version_name", new Expected("23514", "name")),
          Map.entry("uq_item_stat_version_type", new Expected("23505", "stats")),
          Map.entry("fk_item_stat_type", new Expected("23503", "stats")),
          Map.entry("ck_item_stat_finite", new Expected("23514", "stats")),
          Map.entry("uq_stat_type_name", new Expected("23505", "name")),
          Map.entry("uq_stat_type_order", new Expected("23505", "sortOrder")),
          Map.entry("ck_stat_type_name", new Expected("23514", "name")),
          Map.entry(
              "uq_item_skill_definition_version_start_patch",
              new Expected("23505", "fromGamePatchId")),
          Map.entry("fk_item_skill_definition_version_owner", new Expected("23503", "skillId")),
          Map.entry(
              "fk_item_skill_definition_version_patch", new Expected("23503", "fromGamePatchId")),
          Map.entry("ck_item_skill_definition_version_name", new Expected("23514", "internalName")),
          Map.entry(
              "ck_item_skill_definition_version_description", new Expected("23514", "description")),
          Map.entry("uq_item_version_skill_link_item_definition", new Expected("23505", "skills")),
          Map.entry(
              "fk_item_version_skill_link_definition_version", new Expected("23503", "skills")));

  public static RuntimeException translate(RuntimeException failure) {
    return translate(failure, ApiFailure::invalidInput);
  }

  static RuntimeException translate(
      RuntimeException failure, Function<String, ApiFailure> invalidInput) {
    for (Throwable cause = failure; cause != null; cause = cause.getCause()) {
      if (cause instanceof ConstraintViolationException violation) {
        String constraint = violation.getConstraintName();
        Expected expected = constraint == null ? null : EXPECTED.get(constraint);
        if (expected != null && expected.state().equals(violation.getSQLState()))
          return invalidInput.apply(expected.field());
      }
    }
    // LW001, unknown constraints, programming and infrastructure failures remain internal errors.
    return failure;
  }
}
