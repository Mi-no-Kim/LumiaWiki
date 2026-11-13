package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "item_category", schema = "public")
@Getter
public class ItemCategory extends CatalogRow {
  @Column(name = "name", nullable = false, columnDefinition = "text")
  private String name;

  @ManyToOne(fetch = FetchType.LAZY, optional = true)
  @JoinColumn(name = "parent_id", nullable = true)
  private ItemCategory parent;

  protected ItemCategory() {}

  ItemCategory(String name, ItemCategory parent) {
    change(name, parent);
  }

  void change(String name, ItemCategory parent) {
    this.name = name;
    this.parent = parent;
  }
}
