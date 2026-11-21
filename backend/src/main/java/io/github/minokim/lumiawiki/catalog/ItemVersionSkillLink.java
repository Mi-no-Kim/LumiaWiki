package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import lombok.Getter;

@Entity
@Table(name = "item_version_skill_link", schema = "public")
@Getter
public class ItemVersionSkillLink extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_version_id", nullable = false, updatable = false)
  private ItemVersion itemVersion;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_version_patch_id", nullable = false, updatable = false)
  private GamePatch itemVersionPatch;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_skill_definition_id", nullable = false, updatable = false)
  private ItemSkillDefinition skillDefinition;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_skill_definition_version_id", nullable = false)
  private ItemSkillDefinitionVersion skillVersion;

  @Column(columnDefinition = "text")
  private String description;

  protected ItemVersionSkillLink() {}

  ItemVersionSkillLink(
      ItemVersion itemVersion, ItemSkillDefinitionVersion skillVersion, String description) {
    this.itemVersion = itemVersion;
    this.itemVersionPatch = itemVersion.getFromGamePatch();
    this.skillDefinition = skillVersion.getDefinition();
    change(skillVersion, description);
  }

  void change(ItemSkillDefinitionVersion skillVersion, String description) {
    this.skillVersion = skillVersion;
    this.description = description;
  }
}
