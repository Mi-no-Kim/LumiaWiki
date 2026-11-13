package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "region_map_member", schema = "public")
@Getter
public class RegionMapMember extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "map_version_id", nullable = false)
  private RegionMapVersion mapVersion;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "region_id", nullable = false)
  private Region region;

  @Column(name = "name", nullable = false, columnDefinition = "text")
  private String name;

  @Column(name = "sort_order", nullable = false)
  private Long sortOrder;

  protected RegionMapMember() {}

  RegionMapMember(RegionMapVersion mapVersion, Region region, String name, Long sortOrder) {
    change(mapVersion, region, name, sortOrder);
  }

  void change(RegionMapVersion mapVersion, Region region, String name, Long sortOrder) {
    this.mapVersion = mapVersion;
    this.region = region;
    this.name = name;
    this.sortOrder = sortOrder;
  }
}
