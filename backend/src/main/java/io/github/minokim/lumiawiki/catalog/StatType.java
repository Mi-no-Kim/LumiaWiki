package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;

@Entity
@Table(name = "stat_type", schema = "public")
@Getter
public class StatType extends CatalogRow {
  @Column(nullable = false, columnDefinition = "text")
  private String name;

  @Column(name = "sort_order", nullable = false)
  private long sortOrder;

  protected StatType() {}

  StatType(String name, long sortOrder) {
    change(name, sortOrder);
  }

  void change(String name, long sortOrder) {
    this.name = name;
    this.sortOrder = sortOrder;
  }
}
