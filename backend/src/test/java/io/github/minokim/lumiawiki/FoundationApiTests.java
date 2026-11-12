package io.github.minokim.lumiawiki;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import io.github.minokim.lumiawiki.common.api.ApiExceptionAdvice;
import io.github.minokim.lumiawiki.common.api.RequestIdFilter;
import io.github.minokim.lumiawiki.dev.FoundationController;
import io.github.minokim.lumiawiki.dev.FoundationService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.beans.factory.config.YamlPropertiesFactoryBean;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
import org.springframework.web.bind.annotation.*;

class FoundationApiTests {
    static final String API = "/api/v1/_dev/foundation";
    MockMvc mvc;
    LocalValidatorFactoryBean validator;

    @RestController
    static class InputProbe {
        record Input(@NotBlank String name) {}
        @PostMapping("/test-only/input") Input input(@Valid @RequestBody Input input) { return input; }
        @GetMapping("/test-only/number") int number(@RequestParam int value) { return value; }
        @GetMapping("/test-only/failure") String failure() { throw new IllegalStateException("SQL password=private-test-value"); }
    }

    @BeforeEach void setUp() {
        validator = new LocalValidatorFactoryBean();
        validator.afterPropertiesSet();
        mvc = MockMvcBuilders.standaloneSetup(new FoundationController(new FoundationService()), new InputProbe())
                .setControllerAdvice(new ApiExceptionAdvice()).addFilters(new RequestIdFilter()).setValidator(validator).build();
    }

    @AfterEach void cleanUp() { validator.close(); MDC.clear(); }

    @Test void normalAndEmptyResponsesHaveServerOwnedRequestIds() throws Exception {
        var result = mvc.perform(get(API).header("X-Request-ID", "attacker-secret")).andExpect(status().isOk())
                .andExpect(jsonPath("$.items[0].id").value("sample-a"))
                .andExpect(jsonPath("$.items[0].label").value("연결 확인")).andReturn();
        String id = result.getResponse().getHeader("X-Request-ID");
        assertNotNull(id);
        assertEquals(id, UUID.fromString(id).toString());
        assertNotEquals("attacker-secret", id);
        assertNull(MDC.get("requestId"));
        mvc.perform(get(API).param("scenario", "empty")).andExpect(status().isOk()).andExpect(jsonPath("$.items").isEmpty());
    }

    @Test void badInputAndMissingUseProblemDetail() throws Exception {
        var bad = mvc.perform(get(API).param("scenario", "bad-input")).andExpect(status().isBadRequest())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
                .andExpect(jsonPath("$.code").value("API_INPUT_INVALID"))
                .andExpect(jsonPath("$.fieldErrors[0].field").value("scenario")).andReturn();
        String id = bad.getResponse().getHeader("X-Request-ID");
        assertNotNull(id);
        assertTrue(bad.getResponse().getContentAsString().contains(id));
        mvc.perform(get(API).param("scenario", "missing")).andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404)).andExpect(jsonPath("$.code").value("API_RESOURCE_NOT_FOUND"));
        mvc.perform(get(API).param("scenario", "private-test-value")).andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("입력 내용을 확인해 주세요."));
    }

    @Test void internalFailureRedactsResponsesAndLogs() throws Exception {
        mvc.perform(get(API)).andExpect(status().isOk());
        Logger logger = (Logger) LoggerFactory.getLogger(ApiExceptionAdvice.class);
        var appender = new ListAppender<ILoggingEvent>(); appender.start(); logger.addAppender(appender);
        try {
            var result = mvc.perform(get("/test-only/failure")).andExpect(status().isInternalServerError())
                    .andExpect(jsonPath("$.code").value("API_INTERNAL_ERROR")).andReturn();
            String body = result.getResponse().getContentAsString();
            assertFalse(body.contains("SQL")); assertFalse(body.contains("private-test-value"));
            assertFalse(body.contains("IllegalStateException"));
            assertEquals(1, appender.list.size());
            var event = appender.list.getFirst();
            assertTrue(event.getFormattedMessage().contains(result.getResponse().getHeader("X-Request-ID")));
            assertFalse(event.getFormattedMessage().contains("private-test-value"));
            assertNotNull(event.getThrowableProxy());
            assertFalse(event.getThrowableProxy().getMessage().contains("private-test-value"));
            assertTrue(event.getThrowableProxy().getStackTraceElementProxyArray().length > 0);
            assertNull(event.getThrowableProxy().getCause());
            assertNull(MDC.get("requestId"));
        } finally { logger.detachAppender(appender); appender.stop(); }
    }

    @Test void mvcValidationAndParsingRemain400() throws Exception {
        mvc.perform(post("/test-only/input").contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"\"}"))
                .andExpect(status().isBadRequest()).andExpect(header().exists("X-Request-ID"))
                .andExpect(jsonPath("$.fieldErrors[0].field").value("name"))
                .andExpect(jsonPath("$.fieldErrors[0].rejectedValue").doesNotExist());
        mvc.perform(post("/test-only/input").contentType(MediaType.APPLICATION_JSON).content("invalid-secret-json"))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("API_INPUT_INVALID"))
                .andExpect(jsonPath("$.detail").value("입력 내용을 확인해 주세요."));
        mvc.perform(get("/test-only/number").param("value", "private-test-value"))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.fieldErrors[0].field").value("value"));
    }

    @Test void unsupportedMethodKeeps405() throws Exception {
        mvc.perform(get(API)).andExpect(status().isOk());
        mvc.perform(post(API)).andExpect(status().isMethodNotAllowed())
                .andExpect(jsonPath("$.status").value(405)).andExpect(jsonPath("$.code").value("API_INPUT_INVALID"));
    }

    @Test void profileGatesDevEndpoint() {
        try (var production = new AnnotationConfigApplicationContext()) {
            production.register(FoundationController.class, FoundationService.class); production.refresh();
            assertEquals(0, production.getBeanNamesForType(FoundationController.class).length);
        }
        for (String profile : new String[]{"local", "test"}) {
            try (var context = new AnnotationConfigApplicationContext()) {
                context.getEnvironment().setActiveProfiles(profile);
                context.register(FoundationController.class, FoundationService.class); context.refresh();
                assertEquals(1, context.getBeanNamesForType(FoundationController.class).length);
            }
        }
        for (String config : new String[]{"application.yaml", "application-local.yaml", "application-test.yaml"}) {
            var yaml = new YamlPropertiesFactoryBean(); yaml.setResources(new ClassPathResource(config));
            var props = yaml.getObject(); assertNotNull(props);
            String enabled = config.equals("application.yaml") ? "false" : "true";
            assertEquals(enabled, props.getProperty("springdoc.api-docs.enabled"));
            assertEquals(enabled, props.getProperty("springdoc.swagger-ui.enabled"));
        }
    }

    @Test void slowResponseUsesOneSecondDelay() throws Exception {
        mvc.perform(get(API)).andExpect(status().isOk());
        long start = System.nanoTime();
        mvc.perform(get(API).param("scenario", "slow")).andExpect(status().isOk()).andExpect(jsonPath("$.items[0].id").value("sample-a"));
        assertTrue(System.nanoTime() - start >= 900_000_000L);
    }
}
