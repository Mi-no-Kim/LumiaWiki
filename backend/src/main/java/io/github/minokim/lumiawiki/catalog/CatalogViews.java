package io.github.minokim.lumiawiki.catalog;

import java.util.List;

public final class CatalogViews {
  private CatalogViews() {}

  // Public map information never includes Region.displayName.
  public record MapRegion(Long regionId, String name, long sortOrder) {}

  public record RegionMap(Long mapVersionId, List<MapRegion> regions) {
    public RegionMap {
      regions = List.copyOf(regions);
    }

    public boolean known() {
      return mapVersionId != null;
    }
  }
}
