package io.github.minokim.lumiawiki.catalog;

/** A provider reports a discrepancy only when comparable hunting detail is available. */
@FunctionalInterface
public interface HuntingAcquisitionCheck {
  boolean differs(Long itemVersionId, Long regionId);
}
