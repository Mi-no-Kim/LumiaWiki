package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "item_skill_definition", schema = "public")
public class ItemSkillDefinition extends CatalogRow {
  protected ItemSkillDefinition() {}
}
