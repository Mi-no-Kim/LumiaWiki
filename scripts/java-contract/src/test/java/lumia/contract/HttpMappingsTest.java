package lumia.contract;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.web.servlet.function.RouterFunctions.route;

import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.mock.web.MockServletContext;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.function.RouterFunction;
import org.springframework.web.servlet.function.ServerResponse;

final class HttpMappingsTest {
    @Configuration(proxyBeanMethods = false)
    @EnableWebMvc
    static class Mvc {}

    @RestController
    @RequestMapping("/api")
    static class PublicController {
        @RequestMapping(path = {"/item/{Id}", "/item/"}, method = {RequestMethod.GET, RequestMethod.POST})
        String item() {
            return "";
        }
    }

    @RestController
    @Profile({"local", "test"})
    static class DevelopmentController {
        @GetMapping("/api/_dev/probe")
        String probe() {
            return "";
        }
    }

    @RestController
    static class UnrestrictedController {
        @RequestMapping("/api/unrestricted")
        String read() {
            return "";
        }
    }

    @Configuration(proxyBeanMethods = false)
    static class Router {
        @Bean
        static RouterFunction<ServerResponse> routes() {
            return route().path("/api", builder -> builder
                    .GET("/routed/{id}", request -> ServerResponse.ok().build())).build();
        }
    }

    @Configuration(proxyBeanMethods = false)
    static class DuplicateRouter {
        @Bean
        static RouterFunction<ServerResponse> other() {
            return route().GET("/api/routed/{id}", request -> ServerResponse.ok().build()).build();
        }
    }

    @Test
    void extractsRegisteredPathsAndExplicitMethodsIncludingRouter() {
        var expected = Set.of(
                endpoint("GET", "/api/item/{Id}"), endpoint("POST", "/api/item/{Id}"),
                endpoint("GET", "/api/item/"), endpoint("POST", "/api/item/"),
                endpoint("GET", "/api/routed/{id}"));
        var actual = collect("production", PublicController.class, Router.class);
        assertEquals(expected, actual.endpoints());
        assertEquals(java.util.List.of(), HttpMappings.compare(expected, actual));
    }

    @Test
    void emptyProductionListAndActualDevelopmentRegistration() {
        assertEquals(Set.of(), collect("production", DevelopmentController.class).endpoints());
        for (String profile : new String[] {"local", "test"}) {
            assertEquals(Set.of(endpoint("GET", "/api/_dev/probe")),
                    collect(profile, DevelopmentController.class).endpoints());
        }
    }

    @Test
    void reportsAddRemoveAndMethodChangeAgainstActualMappings() {
        var violations = HttpMappings.compare(
                Set.of(endpoint("DELETE", "/api/item/{Id}"), endpoint("GET", "/api/removed")),
                collect("production", PublicController.class));
        assertTrue(violations.contains("Missing approved HTTP mapping: GET /api/removed"), violations.toString());
        assertTrue(violations.contains("Missing approved HTTP mapping: DELETE /api/item/{Id}"), violations.toString());
        assertTrue(violations.contains("Unapproved HTTP mapping: GET /api/item/{Id}"), violations.toString());
    }

    @Test
    void aProductionDevelopmentHandlerIsRejectedEvenIfListed() {
        var found = endpoint("GET", "/api/_dev/probe");
        var actual = collect("production", lumia.contract.dev.LeakedController.class);
        assertEquals(Set.of(found), actual.endpoints());
        assertEquals(java.util.List.of("Development HTTP mapping registered in production: GET /api/_dev/probe"),
                HttpMappings.compare(Set.of(found), actual));
    }

    @Test
    void unrestrictedMethodsAreUnconfirmed() {
        assertThrows(IllegalArgumentException.class, () -> collect("production", UnrestrictedController.class));
    }

    @Test
    void distinctHandlersWithTheSamePathRemainIdentifiable() {
        assertEquals(Set.of(endpoint("GET", "/api/routed/{id}")),
                collect("production", Router.class, DuplicateRouter.class).endpoints());
    }

    private static HttpMappings.Endpoint endpoint(String method, String path) {
        return new HttpMappings.Endpoint(method, path);
    }

    private static HttpMappings.Inventory collect(String profile, Class<?>... configuration) {
        try (var context = new AnnotationConfigWebApplicationContext()) {
            context.setServletContext(new MockServletContext());
            context.getEnvironment().setActiveProfiles(profile);
            context.register(Mvc.class);
            context.register(configuration);
            context.refresh();
            return HttpMappings.collect(context, "lumia.contract");
        }
    }
}
