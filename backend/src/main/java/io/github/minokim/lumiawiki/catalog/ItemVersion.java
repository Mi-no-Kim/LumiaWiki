package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;
import lombok.Getter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "item_version", schema = "public")
@Getter
public class ItemVersion extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_id", nullable = false, updatable = false)
  private Item item;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "from_game_patch_id", nullable = false, updatable = false)
  private GamePatch fromGamePatch;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "category_id", nullable = false)
  private ItemCategory category;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "grade_id")
  private ItemGrade grade;

  @Column(name = "max_stack_size")
  private Integer maxStackSize;

  @Column(name = "name", nullable = false, columnDefinition = "text")
  private String name;

  @Column(name = "image_path", columnDefinition = "text")
  private String imagePath;

  @Column(name = "is_deleted", nullable = false)
  private boolean deleted;

  @JdbcTypeCode(SqlTypes.JSON)
  @Column(name = "stat_json", columnDefinition = "jsonb", nullable = false)
  private String statJson = "[]";

  @OneToMany(mappedBy = "itemVersion", cascade = CascadeType.PERSIST, orphanRemoval = true)
  private List<ItemStat> stats = new ArrayList<>();

  @OneToMany(mappedBy = "itemVersion", cascade = CascadeType.PERSIST, orphanRemoval = true)
  @OrderBy("id ASC")
  private List<ItemVersionSkillLink> skillLinks = new ArrayList<>();

  protected ItemVersion() {}

  ItemVersion(
      Item item,
      GamePatch fromGamePatch,
      ItemCategory category,
      String name,
      String imagePath,
      boolean deleted) {
    this.item = item;
    this.fromGamePatch = fromGamePatch;
    change(category, name, imagePath, deleted);
  }

  void change(ItemCategory category, String name, String imagePath, boolean deleted) {
    this.category = category;
    this.name = name;
    this.imagePath = imagePath;
    this.deleted = deleted;
  }

  void changeDetails(ItemGrade grade, Integer maxStackSize) {
    this.grade = grade;
    this.maxStackSize = maxStackSize;
  }

  void rebuildStatCache() {
    statJson = ItemStatCache.build(stats);
  }
}
