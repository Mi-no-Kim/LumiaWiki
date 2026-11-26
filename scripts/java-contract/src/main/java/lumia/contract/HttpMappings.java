package lumia.contract;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.function.Function;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.annotation.AnnotatedBeanDefinition;
import org.springframework.beans.factory.support.RootBeanDefinition;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpMethod;
import org.springframework.web.servlet.function.HandlerFunction;
import org.springframework.web.servlet.function.RequestPredicate;
import org.springframework.web.servlet.function.RequestPredicates;
import org.springframework.web.servlet.function.RouterFunction;
import org.springframework.web.servlet.function.RouterFunctions;
import org.springframework.web.servlet.function.ServerRequest;
import org.springframework.web.servlet.function.support.RouterFunctionMapping;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;
import org.springframework.web.util.pattern.PathPatternParser;

/** Reads effective registrations from a refreshed Spring MVC application context. */
public final class HttpMappings {
    private HttpMappings() {}

    public record Endpoint(String method, String path) implements Comparable<Endpoint> {
        public Endpoint {
            if (!method.matches("[A-Z][A-Z0-9_-]*") || !path.startsWith("/")) {
                throw new IllegalArgumentException("Unsupported HTTP registration: " + method + " " + path);
            }
        }

        @Override
        public int compareTo(Endpoint other) {
            int byPath = path.compareTo(other.path());
            return byPath == 0 ? method.compareTo(other.method()) : byPath;
        }

        @Override
        public String toString() {
            return method + " " + path;
        }
    }

    public record Inventory(Set<Endpoint> endpoints, Set<Endpoint> developmentSources) {}

    public static Inventory collect(ConfigurableApplicationContext context, String basePackage) {
        var endpoints = new TreeSet<Endpoint>();
        var development = new TreeSet<Endpoint>();
        var controllerMappings = context.getBeansOfType(RequestMappingHandlerMapping.class);
        if (controllerMappings.isEmpty()) {
            throw new IllegalArgumentException("No Spring MVC controller registry was available");
        }
        for (var registry : controllerMappings.values()) {
            registry.getHandlerMethods().forEach((mapping, handler) -> {
                String owner = handler.getBeanType().getPackageName();
                if (!inPackage(owner, basePackage)) {
                    return;
                }
                var methods = mapping.getMethodsCondition().getMethods();
                if (methods.isEmpty() || mapping.getPatternValues().isEmpty()) {
                    throw new IllegalArgumentException("Cannot confirm explicit methods and paths: " + handler);
                }
                for (String path : mapping.getPatternValues()) {
                    for (var method : methods) {
                        add(new Endpoint(method.name(), fullPath(path)), owner, basePackage, endpoints, development);
                    }
                }
            });
        }
        collectRouters(context, basePackage, endpoints, development);
        return new Inventory(Set.copyOf(endpoints), Set.copyOf(development));
    }

    private static void collectRouters(
            ConfigurableApplicationContext context, String basePackage,
            Set<Endpoint> endpoints, Set<Endpoint> development) {
        var registry = context.getBeansOfType(RouterFunctionMapping.class);
        var registered = new HashSet<Route>();
        for (var mapping : registry.values()) {
            if (mapping.getRouterFunction() != null) {
                registered.addAll(routes(mapping.getRouterFunction()));
            }
        }
        var identified = new HashSet<Route>();
        for (var bean : context.getBeansOfType(RouterFunction.class).entrySet()) {
            var candidates = routes(bean.getValue());
            if (!registered.containsAll(candidates)) {
                throw new IllegalArgumentException("Cannot establish routing registration: " + bean.getKey());
            }
            if (candidates.stream().anyMatch(identified::contains)) {
                throw new IllegalArgumentException("Cannot distinguish the owners of registered Spring routes");
            }
            identified.addAll(candidates);
            String owner = routerOwner(context.getBeanFactory(), bean.getKey());
            if (inPackage(owner, basePackage)) {
                for (var route : candidates) {
                    add(route.endpoint(), owner, basePackage, endpoints, development);
                }
            }
        }
        if (!registered.equals(identified)) {
            throw new IllegalArgumentException("Cannot establish the owner of a registered Spring router");
        }
    }

    private static String routerOwner(ConfigurableListableBeanFactory beans, String name) {
        if (!beans.containsBeanDefinition(name)) {
            throw new IllegalArgumentException("Cannot establish the owner of router " + name);
        }
        var definition = beans.getBeanDefinition(name);
        if (definition instanceof AnnotatedBeanDefinition annotated
                && annotated.getFactoryMethodMetadata() != null) {
            String declaring = annotated.getFactoryMethodMetadata().getDeclaringClassName();
            return declaring.substring(0, declaring.lastIndexOf('.'));
        }
        if (beans.getMergedBeanDefinition(name) instanceof RootBeanDefinition root
                && root.getResolvedFactoryMethod() != null) {
            return root.getResolvedFactoryMethod().getDeclaringClass().getPackageName();
        }
        String className = definition.getBeanClassName();
        Class<?> owner = definition.getFactoryMethodName() == null && className != null ? beans.getType(name) : null;
        if (owner == null) {
            throw new IllegalArgumentException("Cannot establish the owner of router " + name);
        }
        return owner.getPackageName();
    }

    private static boolean inPackage(String typePackage, String root) {
        return typePackage.equals(root) || typePackage.startsWith(root + ".");
    }

    private static void add(Endpoint route, String owner, String basePackage,
                            Set<Endpoint> endpoints, Set<Endpoint> development) {
        endpoints.add(route);
        if (inPackage(owner, basePackage + ".dev")) {
            development.add(route);
        }
    }

    private static String fullPath(String path) {
        // A Spring empty mapping is the root mapping.
        return path.isEmpty() ? "/" : path;
    }

    public static List<String> compare(Set<Endpoint> approved, Inventory production) {
        var violations = new ArrayList<String>();
        var removed = new TreeSet<>(approved);
        removed.removeAll(production.endpoints());
        removed.forEach(endpoint -> violations.add("Missing approved HTTP mapping: " + endpoint));
        var added = new TreeSet<>(production.endpoints());
        added.removeAll(approved);
        added.forEach(endpoint -> violations.add("Unapproved HTTP mapping: " + endpoint));
        new TreeSet<>(production.developmentSources()).forEach(
                endpoint -> violations.add("Development HTTP mapping registered in production: " + endpoint));
        return List.copyOf(violations);
    }

    private record Route(Endpoint endpoint, HandlerFunction<?> handler, RequestPredicate predicate) {
        @Override
        public boolean equals(Object other) {
            return other instanceof Route route && endpoint.equals(route.endpoint)
                    && handler == route.handler && predicate == route.predicate;
        }

        @Override
        public int hashCode() {
            return endpoint.hashCode() + 31 * System.identityHashCode(handler)
                    + 31 * System.identityHashCode(predicate);
        }
    }

    private static Set<Route> routes(RouterFunction<?> router) {
        var visitor = new RouterVisitor();
        router.accept(visitor);
        return visitor.routes;
    }

    private static final class RouterVisitor implements RouterFunctions.Visitor {
        private final ArrayDeque<Conditions> nested = new ArrayDeque<>();
        private final Set<Route> routes = new HashSet<>();

        @Override public void startNested(RequestPredicate predicate) { nested.addLast(conditions(predicate)); }
        @Override public void endNested(RequestPredicate predicate) { nested.removeLast(); }
        @Override public void attributes(Map<String, Object> attributes) {}
        @Override public void unknown(RouterFunction<?> function) { throw unsupported(); }
        @Override public void resources(Function<ServerRequest, Optional<Resource>> lookup) { throw unsupported(); }

        @Override
        public void route(RequestPredicate predicate, HandlerFunction<?> handler) {
            String path = "";
            Set<String> methods = null;
            var predicates = new ArrayList<>(nested);
            predicates.add(conditions(predicate));
            for (var part : predicates) {
                if (part.path != null) {
                    path = path.isEmpty() ? part.path : PathPatternParser.defaultInstance.parse(path)
                            .combine(PathPatternParser.defaultInstance.parse(part.path)).getPatternString();
                }
                if (part.methods != null) {
                    if (methods == null) {
                        methods = new TreeSet<>(part.methods);
                    } else {
                        methods.retainAll(part.methods);
                    }
                }
            }
            if (path.isEmpty() || methods == null || methods.isEmpty()) {
                throw unsupported();
            }
            for (String method : methods) {
                if (!routes.add(new Route(new Endpoint(method, path), handler, predicate))) {
                    throw unsupported();
                }
            }
        }
    }

    private static Conditions conditions(RequestPredicate predicate) {
        var visitor = new Conditions();
        predicate.accept(visitor);
        return visitor;
    }

    private static IllegalArgumentException unsupported() {
        return new IllegalArgumentException("Cannot confirm the explicit method and path of a Spring router");
    }

    private static final class Conditions implements RequestPredicates.Visitor {
        private String path;
        private Set<String> methods;

        @Override
        public void method(Set<HttpMethod> values) {
            var names = new TreeSet<String>();
            values.forEach(method -> names.add(method.name()));
            if (methods == null) {
                methods = names;
            } else {
                methods.retainAll(names);
            }
        }

        @Override
        public void path(String pattern) {
            if (path != null && !path.equals(pattern)) {
                throw unsupported();
            }
            path = pattern;
        }

        @Override public void header(String name, String value) {}
        @Override public void param(String name, String value) {}
        @Override public void version(String version) {}
        @Override public void startAnd() {}
        @Override public void and() {}
        @Override public void endAnd() {}
        @Override public void startOr() { throw unsupported(); }
        @Override public void or() { throw unsupported(); }
        @Override public void endOr() { throw unsupported(); }
        @Override public void startNegate() { throw unsupported(); }
        @Override public void endNegate() { throw unsupported(); }
        @Override @SuppressWarnings("removal") public void pathExtension(String extension) { throw unsupported(); }
        @Override public void unknown(RequestPredicate predicate) { throw unsupported(); }
    }
}
