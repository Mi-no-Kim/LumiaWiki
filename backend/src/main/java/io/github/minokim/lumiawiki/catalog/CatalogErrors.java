package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.util.Map;
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
          Map.entry("fk_region_map_member_region", new Expected("23503", "regionId")));

  public static RuntimeException translate(RuntimeException failure) {
    for (Throwable cause = failure; cause != null; cause = cause.getCause()) {
      if (cause instanceof ConstraintViolationException violation) {
        String constraint = violation.getConstraintName();
        Expected expected = constraint == null ? null : EXPECTED.get(constraint);
        if (expected != null && expected.state().equals(violation.getSQLState()))
          return ApiFailure.invalidInput(expected.field());
      }
    }
    // LW001, unknown constraints, programming and infrastructure failures remain internal errors.
    return failure;
  }
}
