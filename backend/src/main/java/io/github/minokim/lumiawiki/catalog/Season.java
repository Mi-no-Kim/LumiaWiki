package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "season", schema = "public")
@Getter
public class Season extends CatalogRow {
  @Column(name = "season_number", nullable = false)
  private Integer seasonNumber;

  @Column(name = "display_name", nullable = false, columnDefinition = "text")
  private String displayName;

  @Column(name = "season_name", nullable = true, columnDefinition = "text")
  private String seasonName;

  @Column(name = "sort_order", nullable = false)
  private Long sortOrder;

  @Column(name = "start_date", nullable = true)
  private LocalDate startDate;

  @Column(name = "end_date", nullable = true)
  private LocalDate endDate;

  protected Season() {}

  Season(
      Integer seasonNumber,
      String displayName,
      String seasonName,
      Long sortOrder,
      LocalDate startDate,
      LocalDate endDate) {
    change(seasonNumber, displayName, seasonName, sortOrder, startDate, endDate);
  }

  void change(
      Integer seasonNumber,
      String displayName,
      String seasonName,
      Long sortOrder,
      LocalDate startDate,
      LocalDate endDate) {
    this.seasonNumber = seasonNumber;
    this.displayName = displayName;
    this.seasonName = seasonName;
    this.sortOrder = sortOrder;
    this.startDate = startDate;
    this.endDate = endDate;
  }
}
