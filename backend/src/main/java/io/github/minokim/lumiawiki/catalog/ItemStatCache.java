package io.github.minokim.lumiawiki.catalog;

import java.math.BigDecimal;
import java.util.Comparator;
import java.util.List;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.json.JsonMapper;

final class ItemStatCache {
  private static final JsonMapper MAPPER = JsonMapper.builder().build();
  private static final TypeReference<List<Entry>> ENTRIES = new TypeReference<>() {};

  private ItemStatCache() {}

  private record Entry(String statTypeId, BigDecimal value) {}

  static String build(List<ItemStat> stats) {
    List<Entry> entries =
        stats.stream()
            .sorted(Comparator.comparingLong(stat -> stat.getStatType().getSortOrder()))
            .map(stat -> new Entry(stat.getStatType().getId().toString(), stat.getValue()))
            .toList();
    return MAPPER.writeValueAsString(entries);
  }

  static List<ItemCatalogService.StatValue> read(String json) {
    return MAPPER.readValue(json, ENTRIES).stream()
        .map(stat ->
            new ItemCatalogService.StatValue(stat.statTypeId(), stat.value().toPlainString()))
        .toList();
  }
}
