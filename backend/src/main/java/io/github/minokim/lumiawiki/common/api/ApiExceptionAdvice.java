package io.github.minokim.lumiawiki.common.api;

import jakarta.servlet.http.HttpServletRequest;
import java.net.URI;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.context.request.ServletWebRequest;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

@Slf4j
@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)
public class ApiExceptionAdvice extends ResponseEntityExceptionHandler {
    @ExceptionHandler(ApiFailure.class)
    ResponseEntity<Object> business(ApiFailure failure, HttpServletRequest request) {
        return response(failure.status(), failure.code(), failure.fields(), request, new HttpHeaders());
    }

    @ExceptionHandler(Exception.class)
    ResponseEntity<Object> unexpected(Exception failure, HttpServletRequest request) {
        // Keep the exception type and stack locations, excluding messages, causes and request values.
        var diagnostic = new RuntimeException(failure.getClass().getName());
        diagnostic.setStackTrace(failure.getStackTrace());
        log.error("Unexpected API failure requestId={}", request.getAttribute(RequestIdFilter.ATTRIBUTE), diagnostic);
        return response(HttpStatus.INTERNAL_SERVER_ERROR, "API_INTERNAL_ERROR", List.of(), request, new HttpHeaders());
    }

    @Override
    protected ResponseEntity<Object> handleExceptionInternal(Exception failure, Object body, HttpHeaders headers,
            HttpStatusCode status, WebRequest webRequest) {
        HttpServletRequest request = ((ServletWebRequest) webRequest).getRequest();
        if (status.is5xxServerError()) return unexpected(failure, request);
        List<ApiFailure.FieldError> fields = List.of();
        if (failure instanceof MethodArgumentNotValidException invalid) {
            fields = invalid.getBindingResult().getFieldErrors().stream()
                    .map(error -> new ApiFailure.FieldError(error.getField(),
                            error.getCode() == null ? "Invalid" : error.getCode(), "입력값을 확인해 주세요.")).toList();
        } else if (failure instanceof MethodArgumentTypeMismatchException invalid) {
            fields = List.of(new ApiFailure.FieldError(invalid.getName(), "Invalid", "입력값을 확인해 주세요."));
        }
        return response(status, status.value() == 404 ? "API_RESOURCE_NOT_FOUND" : "API_INPUT_INVALID", fields, request, headers);
    }

    private ResponseEntity<Object> response(HttpStatusCode status, String code, List<ApiFailure.FieldError> fields,
            HttpServletRequest request, HttpHeaders headers) {
        String detail = status.value() == 404 ? "요청한 대상을 찾을 수 없습니다." : status.is5xxServerError()
                ? "요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요." : "입력 내용을 확인해 주세요.";
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setInstance(URI.create(request.getRequestURI()));
        problem.setProperty("code", code);
        problem.setProperty("requestId", request.getAttribute(RequestIdFilter.ATTRIBUTE));
        if (!fields.isEmpty()) problem.setProperty("fieldErrors", fields);
        if (status.is4xxClientError()) log.warn("API rejection code={} requestId={}", code, request.getAttribute(RequestIdFilter.ATTRIBUTE));
        return new ResponseEntity<>(problem, headers, status);
    }
}
