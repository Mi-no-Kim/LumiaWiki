package io.github.minokim.lumiawiki.catalog;

/**
 * Downstream Tasks 003/004 must register their reference checks before persisting consumers. Runs
 * after flush under the patch/map basis locks, in the caller's transaction. The initial eight-table
 * model has no downstream consumer tables.
 */
@FunctionalInterface
public interface CatalogReferenceCheck {
  void verify();
}
