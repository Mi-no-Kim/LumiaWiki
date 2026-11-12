package io.github.minokim.lumiawiki.dev;

import org.springframework.stereotype.Service;
import org.springframework.context.annotation.Profile;
import java.util.List;
import io.github.minokim.lumiawiki.common.api.ApiFailure;

@Service
@Profile({"local", "test"})
public class FoundationService {
    public FoundationResponse response(String scenario) {
        switch (scenario) {
            case "empty": return new FoundationResponse(List.of());
            case "bad-input": throw ApiFailure.invalidInput("scenario");
            case "missing": throw ApiFailure.notFound();
            case "failure": throw new IllegalStateException("Controlled foundation failure");
            case "slow":
                try { Thread.sleep(1000); }
                catch (InterruptedException failure) { Thread.currentThread().interrupt(); throw new IllegalStateException("Foundation request interrupted"); }
                break;
            case "ok": break;
            default: throw ApiFailure.invalidInput("scenario");
        }
        // No database transaction is needed for this controlled, immutable fixture.
        return new FoundationResponse(List.of(new FoundationResponse.Item("sample-a", "연결 확인")));
    }
}
