package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "weapon_type", schema = "public")
@Getter
public class WeaponType extends CatalogRow {
  @Column(name = "name", nullable = false, columnDefinition = "text")
  private String name;

  @OneToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "category_id", nullable = false, unique = true)
  private ItemCategory category;

  protected WeaponType() {}

  WeaponType(String name, ItemCategory category) {
    change(name, category);
  }

  void change(String name, ItemCategory category) {
    this.name = name;
    this.category = category;
  }
}
