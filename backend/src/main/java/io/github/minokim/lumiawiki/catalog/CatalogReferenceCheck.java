package io.github.minokim.lumiawiki.catalog;

/**
 * Downstream catalogs register their reference checks before persisting consumers. Runs after flush
 * under the patch/map basis locks, in the caller's transaction.
 */
@FunctionalInterface
public interface CatalogReferenceCheck {
  void verify();
}
