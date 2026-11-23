package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import lombok.Getter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "item_acquisition", schema = "public")
@Getter
class ItemAcquisition extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_version_id", nullable = false, updatable = false)
  private ItemVersion itemVersion;

  @Column(name = "item_id", nullable = false, updatable = false)
  private Long itemId;

  @Column(name = "game_patch_id", nullable = false, updatable = false)
  private Long gamePatchId;

  @Enumerated(EnumType.STRING)
  @JdbcTypeCode(SqlTypes.NAMED_ENUM)
  @Column(name = "method", nullable = false, columnDefinition = "acquisition_method")
  private AcquisitionMethod method;

  @Column(name = "region_id")
  private Long regionId;

  @Column(name = "spawn_count")
  private Integer spawnCount;

  protected ItemAcquisition() {}

  ItemAcquisition(
      ItemVersion version, AcquisitionMethod method, Long regionId, Integer spawnCount) {
    this.itemVersion = version;
    this.itemId = version.getItem().getId();
    this.gamePatchId = version.getFromGamePatch().getId();
    change(method, regionId, spawnCount);
  }

  void change(AcquisitionMethod method, Long regionId, Integer spawnCount) {
    this.method = method;
    this.regionId = regionId;
    this.spawnCount = spawnCount;
  }
}
