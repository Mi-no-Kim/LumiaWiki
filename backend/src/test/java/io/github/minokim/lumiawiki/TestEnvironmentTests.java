package io.github.minokim.lumiawiki;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

// Test-only HTTP fixture: no product controller, database, or business contract.
class TestEnvironmentTests {
    interface Echo { String echo(String value); }
    record Input(@NotBlank String value) {}

    @RestController
    static class ProbeController {
        private final Echo echo;
        ProbeController(Echo echo) { this.echo = echo; }
        @PostMapping("/test-only/probe")
        String probe(@Valid @RequestBody Input input) { return echo.echo(input.value()); }
    }

    Echo echo;
    MockMvc mvc;

    @BeforeEach
    void setUp() {
        echo = mock(Echo.class);
        var validator = new LocalValidatorFactoryBean();
        validator.afterPropertiesSet();
        mvc = MockMvcBuilders.standaloneSetup(new ProbeController(echo)).setValidator(validator).build();
    }

    @Test
    void junitMockitoAndMockMvcRunWithoutDocker() throws Exception {
        when(echo.echo("ready")).thenReturn("ok");
        mvc.perform(post("/test-only/probe").contentType(MediaType.APPLICATION_JSON)
                .content("{\"value\":\"ready\"}"))
                .andExpect(status().isOk()).andExpect(content().string("ok"));
        verify(echo).echo("ready");
    }

    @Test
    void beanValidationRejectsInputBeforeCallingTheCollaborator() throws Exception {
        mvc.perform(post("/test-only/probe").contentType(MediaType.APPLICATION_JSON)
                .content("{\"value\":\"\"}"))
                .andExpect(status().isBadRequest());
        verifyNoInteractions(echo);
    }
}
