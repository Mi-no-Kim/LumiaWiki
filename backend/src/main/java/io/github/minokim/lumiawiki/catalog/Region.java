package io.github.minokim.lumiawiki.catalog;

import jakarta.persistence.*;
import java.time.*;
import lombok.Getter;

@Entity
@Table(name = "region", schema = "public")
@Getter
public class Region extends CatalogRow {
  @Column(name = "display_name", nullable = false, columnDefinition = "text")
  private String displayName;

  protected Region() {}

  Region(String displayName) {
    change(displayName);
  }

  void change(String displayName) {
    this.displayName = displayName;
  }
}
