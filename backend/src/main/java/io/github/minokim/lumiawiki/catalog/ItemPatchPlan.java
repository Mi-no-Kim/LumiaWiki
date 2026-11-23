package io.github.minokim.lumiawiki.catalog;

import io.github.minokim.lumiawiki.catalog.ItemCatalogService.Material;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.PatchItem;
import io.github.minokim.lumiawiki.catalog.ItemCatalogService.Recipe;
import io.github.minokim.lumiawiki.common.api.ApiFailure;
import java.util.*;

/** Resolves a single patch's final recipes before any versions in the request are written. */
record ItemPatchPlan(
    List<Entry> ordered,
    List<Key> requested,
    SortedSet<Long> itemLocks,
    Map<Long, ActiveVersion> active) {
  record ActiveVersion(Long versionId, Long patchId, boolean deleted, Recipe recipe) {}

  record Key(Long itemId, String requestKey) {
    static Key existing(Long itemId) {
      return new Key(itemId, null);
    }
  }

  record Entry(
      Key key,
      PatchItem input,
      ActiveVersion previous,
      Key materialA,
      Key materialB,
      Integer outputCount) {}

  static ItemPatchPlan build(
      long patchId, List<PatchItem> inputs, Map<Long, ActiveVersion> active) {
    Map<Key, PatchItem> explicit = new LinkedHashMap<>();
    Map<String, Key> aliases = new HashMap<>();
    for (PatchItem input : inputs) {
      if (input == null || input.version() == null) throw ApiFailure.invalidInput("changes");
      Long id = input.itemId();
      String requestKey = input.requestKey();
      if (id != null && id <= 0) throw ApiFailure.invalidInput("changes.itemId");
      if (id == null && (requestKey == null || requestKey.isBlank())) {
        throw ApiFailure.invalidInput("changes.requestKey");
      }
      Key key = id == null ? new Key(null, requestKey) : Key.existing(id);
      if (explicit.putIfAbsent(key, input) != null) throw ApiFailure.invalidInput("changes.itemId");
      if (requestKey != null
          && (requestKey.isBlank() || aliases.putIfAbsent(requestKey, key) != null)) {
        throw ApiFailure.invalidInput("changes.requestKey");
      }
    }

    Map<Key, Entry> entries = new LinkedHashMap<>();
    for (var each : active.entrySet()) {
      Key key = Key.existing(each.getKey());
      ActiveVersion previous = each.getValue();
      entries.put(key, entry(patchId, key, explicit.get(key), previous, aliases, active));
    }
    for (var each : explicit.entrySet()) {
      if (!entries.containsKey(each.getKey())) {
        entries.put(
            each.getKey(), entry(patchId, each.getKey(), each.getValue(), null, aliases, active));
      }
    }

    Map<Key, List<Key>> uses = new HashMap<>();
    for (Entry entry : entries.values()) {
      if (entry.materialA() == null) continue;
      uses.computeIfAbsent(entry.materialA(), ignored -> new ArrayList<>()).add(entry.key());
      uses.computeIfAbsent(entry.materialB(), ignored -> new ArrayList<>()).add(entry.key());
    }
    Set<Key> affected = new LinkedHashSet<>(explicit.keySet());
    Deque<Key> pending = new ArrayDeque<>(affected);
    while (!pending.isEmpty()) {
      for (Key owner : uses.getOrDefault(pending.removeFirst(), List.of())) {
        if (affected.add(owner)) pending.addLast(owner);
      }
    }

    List<Entry> ordered = new ArrayList<>();
    Set<Key> visiting = new HashSet<>();
    Set<Key> finished = new HashSet<>();
    SortedSet<Long> itemLocks = new TreeSet<>();
    for (Key key : affected) {
      sort(key, entries, affected, visiting, finished, ordered);
      Entry entry = entries.get(key);
      collectLock(itemLocks, key);
      collectLock(itemLocks, entry.materialA());
      collectLock(itemLocks, entry.materialB());
    }
    return new ItemPatchPlan(ordered, List.copyOf(explicit.keySet()), itemLocks, active);
  }

  private static Entry entry(
      long patchId,
      Key key,
      PatchItem input,
      ActiveVersion previous,
      Map<String, Key> aliases,
      Map<Long, ActiveVersion> active) {
    boolean explicitRecipe = input != null && input.version().recipeChange() != null;
    Recipe recipe =
        explicitRecipe
            ? input.version().recipeChange().value()
            : previous == null ? null : previous.recipe();
    boolean deleted = previous != null && previous.deleted();
    if (input != null) {
      Boolean requestedDeletion = input.version().deleted();
      deleted =
          requestedDeletion != null
              ? requestedDeletion
              : deleted && previous.patchId().equals(patchId);
    }
    if (deleted || recipe == null) return new Entry(key, input, previous, null, null, null);
    Key a = materialKey(recipe.materialA(), "recipe.materialA", explicitRecipe, aliases, active);
    Key b = materialKey(recipe.materialB(), "recipe.materialB", explicitRecipe, aliases, active);
    if (a.equals(b)) throw ApiFailure.invalidInput("recipe.materialB");
    if (recipe.outputCount() == null) throw ApiFailure.invalidInput("recipe.outputCount");
    return new Entry(key, input, previous, a, b, recipe.outputCount());
  }

  private static Key materialKey(
      Material material,
      String field,
      boolean explicit,
      Map<String, Key> aliases,
      Map<Long, ActiveVersion> active) {
    if (material == null) throw ApiFailure.invalidInput(field);
    if (material.requestKey() != null) {
      Key key = aliases.get(material.requestKey());
      if (key == null || material.itemId() != null || material.itemVersionId() != null) {
        throw ApiFailure.invalidInput(field + ".requestKey");
      }
      return key;
    }
    Long id = material.itemId();
    if (id == null || id <= 0) throw ApiFailure.invalidInput(field + ".itemId");
    if (explicit && material.itemVersionId() != null) {
      ActiveVersion materialVersion = active.get(id);
      if (materialVersion == null
          || !material.itemVersionId().equals(materialVersion.versionId())) {
        throw ApiFailure.invalidInput(field + ".itemVersionId");
      }
    }
    return Key.existing(id);
  }

  private static void sort(
      Key key,
      Map<Key, Entry> entries,
      Set<Key> affected,
      Set<Key> visiting,
      Set<Key> finished,
      List<Entry> ordered) {
    if (key == null || !affected.contains(key) || finished.contains(key)) return;
    if (!visiting.add(key)) throw ApiFailure.invalidInput("recipe");
    Entry entry = entries.get(key);
    sort(entry.materialA(), entries, affected, visiting, finished, ordered);
    sort(entry.materialB(), entries, affected, visiting, finished, ordered);
    visiting.remove(key);
    finished.add(key);
    ordered.add(entry);
  }

  private static void collectLock(Set<Long> locks, Key key) {
    if (key != null && key.itemId() != null) locks.add(key.itemId());
  }
}
