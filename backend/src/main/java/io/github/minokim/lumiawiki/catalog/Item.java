package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;

@Entity
@Table(name = "item", schema = "public")
@Getter
public class Item extends CatalogRow {
  @Column(nullable = false)
  private boolean searchable;

  protected Item() {}

  Item(boolean searchable) {
    setSearchable(searchable);
  }

  void setSearchable(boolean searchable) {
    this.searchable = searchable;
  }
}
