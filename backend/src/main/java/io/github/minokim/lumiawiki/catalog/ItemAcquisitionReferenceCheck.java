package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.common.api.ApiFailure;
import org.springframework.stereotype.Component;

/** Map and patch edits recheck acquisition intervals while holding the catalog basis locks. */
@Component
class ItemAcquisitionReferenceCheck implements CatalogReferenceCheck {
  private final CommonCatalogStore store;

  ItemAcquisitionReferenceCheck(CommonCatalogStore store) {
    this.store = store;
  }

  @Override
  public void verify() {
    store
        .findAcquisitionOutsideMap()
        .ifPresent(id -> {
          throw ApiFailure.invalidInput(
              "CHANGE_ACQUISITION_BASIS",
              new ApiFailure.Target("ITEM_ACQUISITION", id.toString()),
              new ApiFailure.FieldError(
                  "regionId", "REGION_OUTSIDE_VERSION_MAP", "획득 지역이 적용 기간의 지도에 없습니다."));
        });
  }
}
