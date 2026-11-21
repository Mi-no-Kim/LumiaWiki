package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import lombok.Getter;

@Entity
@Table(name = "item_skill_definition_version", schema = "public")
@Getter
public class ItemSkillDefinitionVersion extends CatalogRow {
  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "item_skill_definition_id", nullable = false, updatable = false)
  private ItemSkillDefinition definition;

  @ManyToOne(fetch = FetchType.LAZY, optional = false)
  @JoinColumn(name = "from_game_patch_id", nullable = false, updatable = false)
  private GamePatch fromGamePatch;

  @Column(name = "internal_name", nullable = false, columnDefinition = "text")
  private String internalName;

  @Column(nullable = false, columnDefinition = "text")
  private String description;

  protected ItemSkillDefinitionVersion() {}

  ItemSkillDefinitionVersion(
      ItemSkillDefinition definition,
      GamePatch fromGamePatch,
      String internalName,
      String description) {
    this.definition = definition;
    this.fromGamePatch = fromGamePatch;
    change(internalName, description);
  }

  void change(String internalName, String description) {
    this.internalName = internalName;
    this.description = description;
  }
}
