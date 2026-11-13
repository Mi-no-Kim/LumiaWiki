package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "game_patch", schema = "public")
@Getter
public class GamePatch extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "season_id", nullable = false)
  private Season season;

  @Column(name = "major_no", nullable = false)
  private Integer majorNo;

  @Column(name = "minor_no", nullable = false)
  private Integer minorNo;

  @Column(name = "version_name", nullable = true, columnDefinition = "text")
  private String versionName;

  @Column(name = "sort_order", nullable = false)
  private Long sortOrder;

  @Column(name = "applied_at", nullable = true, columnDefinition = "timestamptz(0)")
  private Instant appliedAt;

  protected GamePatch() {}

  GamePatch(
      Season season,
      Integer majorNo,
      Integer minorNo,
      String versionName,
      Long sortOrder,
      Instant appliedAt) {
    change(season, majorNo, minorNo, versionName, sortOrder, appliedAt);
  }

  void change(
      Season season,
      Integer majorNo,
      Integer minorNo,
      String versionName,
      Long sortOrder,
      Instant appliedAt) {
    this.season = season;
    this.majorNo = majorNo;
    this.minorNo = minorNo;
    this.versionName = versionName;
    this.sortOrder = sortOrder;
    this.appliedAt = appliedAt;
  }
}
