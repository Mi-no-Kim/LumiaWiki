package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "item_grade", schema = "public")
@Getter
public class ItemGrade extends CatalogRow {
  @Column(name = "name", nullable = false, columnDefinition = "text")
  private String name;

  @Column(name = "sort_order", nullable = false)
  private Long sortOrder;

  protected ItemGrade() {}

  ItemGrade(String name, Long sortOrder) {
    change(name, sortOrder);
  }

  void change(String name, Long sortOrder) {
    this.name = name;
    this.sortOrder = sortOrder;
  }
}
