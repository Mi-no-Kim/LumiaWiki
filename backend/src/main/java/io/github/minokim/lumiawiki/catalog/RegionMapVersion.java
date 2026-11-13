package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "region_map_version", schema = "public")
@Getter
public class RegionMapVersion extends CatalogRow {
  @OneToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "from_game_patch_id", nullable = false, unique = true)
  private GamePatch fromGamePatch;

  protected RegionMapVersion() {}

  RegionMapVersion(GamePatch fromGamePatch) {
    change(fromGamePatch);
  }

  void change(GamePatch fromGamePatch) {
    this.fromGamePatch = fromGamePatch;
  }
}
