package io.github.minokim.lumiawiki.dev;

import org.springframework.context.annotation.Profile;
import org.springframework.web.bind.annotation.*;

@RestController
@Profile({"local", "test"})
@RequestMapping("/api/v1/_dev/foundation")
public class FoundationController {
  private final FoundationService service;

  public FoundationController(FoundationService service) {
    this.service = service;
  }

  @GetMapping
  public FoundationResponse response(@RequestParam(defaultValue = "ok") String scenario) {
    return service.response(scenario);
  }
}
