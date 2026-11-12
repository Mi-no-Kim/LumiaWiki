package io.github.minokim.lumiawiki.common.api;

import java.util.List;
import org.springframework.http.HttpStatus;

/** Explicit, safe business errors. Never wrap a raw exception message here. */
public class ApiFailure extends RuntimeException {
    public record FieldError(String field, String code, String message) {}
    private final HttpStatus status;
    private final String code;
    private final List<FieldError> fields;

    private ApiFailure(HttpStatus status, String code, List<FieldError> fields) {
        super(code);
        this.status = status;
        this.code = code;
        this.fields = List.copyOf(fields);
    }

    public static ApiFailure invalidInput(String field) {
        return new ApiFailure(HttpStatus.BAD_REQUEST, "API_INPUT_INVALID",
                List.of(new FieldError(field, "Invalid", "입력값을 확인해 주세요.")));
    }

    public static ApiFailure notFound() {
        return new ApiFailure(HttpStatus.NOT_FOUND, "API_RESOURCE_NOT_FOUND", List.of());
    }

    public HttpStatus status() { return status; }
    public String code() { return code; }
    public List<FieldError> fields() { return fields; }
}
