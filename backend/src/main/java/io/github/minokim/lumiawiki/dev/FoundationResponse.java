package io.github.minokim.lumiawiki.dev;

import java.util.List;

public record FoundationResponse(List<Item> items) {
    public record Item(String id, String label) {}
}
