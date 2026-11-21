package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.math.BigDecimal;
import lombok.Getter;

@Entity
@Table(name = "item_stat", schema = "public")
@Getter
public class ItemStat extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_version_id", nullable = false, updatable = false)
  private ItemVersion itemVersion;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "stat_type_id", nullable = false, updatable = false)
  private StatType statType;

  @Column(nullable = false, columnDefinition = "numeric")
  private BigDecimal value;

  protected ItemStat() {}

  ItemStat(ItemVersion itemVersion, StatType statType, BigDecimal value) {
    this.itemVersion = itemVersion;
    this.statType = statType;
    setValue(value);
  }

  void setValue(BigDecimal value) {
    this.value = value;
  }
}
