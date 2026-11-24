package lumia.contract.dev;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public final class LeakedController {
    @GetMapping("/api/_dev/probe")
    public String probe() {
        return "";
    }
}
