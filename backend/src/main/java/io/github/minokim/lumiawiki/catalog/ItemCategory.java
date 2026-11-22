package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.util.Objects;
import lombok.AccessLevel;
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

  @Enumerated(EnumType.STRING)
  @Column(name = "equipment_role", columnDefinition = "text")
  @Getter(AccessLevel.PACKAGE)
  private EquipmentCategoryRole equipmentRole;

  protected ItemCategory() {}

  ItemCategory(String name, ItemCategory parent) {
    change(name, parent);
    if ("장비".equals(name)) equipmentRole = EquipmentCategoryRole.ROOT;
  }

  void change(String name, ItemCategory parent) {
    if (equipmentRole == null
        && parent != null
        && (this.parent == null || !Objects.equals(this.parent.getId(), parent.getId()))) {
      equipmentRole = EquipmentCategoryRole.forEquipmentBranch(name, parent);
    }
    this.name = name;
    this.parent = parent;
  }
}
