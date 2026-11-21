package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import org.springframework.stereotype.Component;

/** Rechecks existing item skill links under the common catalog's patch-order lock. */
@Component
class ItemSkillReferenceCheck implements CatalogReferenceCheck {
  private final CommonCatalogStore store;

  ItemSkillReferenceCheck(CommonCatalogStore store) {
    this.store = store;
  }

  @Override
  public void verify() {
    store
        .findItemVersionWithFutureSkill()
        .ifPresent(id -> {
          throw ApiFailure.invalidInput(
              "CHANGE_PATCH_ORDER",
              new ApiFailure.Target("ITEM_VERSION", id.toString()),
              new ApiFailure.FieldError(
                  "patchNumber",
                  "SKILL_VERSION_AFTER_ITEM_PATCH",
                  "패치 순서를 바꾸면 기존 아이템 스킬 연결이 유효하지 않습니다."));
        });
  }
}
