package lumia.contract;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import org.springframework.boot.SpringApplication;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Runs the module or runtime HTTP check against the compiled submitted application. */
public final class ContractRunner {
    private static final JsonMapper JSON = JsonMapper.builder().build();

    private ContractRunner() {}

    public static void main(String[] args) {
        List<String> violations;
        try {
            if (args.length != 4) {
                throw new IllegalArgumentException("Expected check, backend snapshot, Java policy and HTTP approval list");
            }
            var snapshot = read(args[1]);
            var policy = read(args[2]);
            violations = switch (args[0]) {
                case "module" -> module(snapshot, policy.get("java"));
                case "http" -> http(policy, read(args[3]));
                default -> throw new IllegalArgumentException("Unknown Java contract check " + args[0]);
            };
        } catch (Exception | LinkageError error) {
            System.err.println("Java contract unconfirmed: " + error.getMessage());
            System.err.println("Next: Restore the submitted inputs or application startup and rerun this check.");
            System.exit(2);
            return;
        }
        if (!violations.isEmpty()) {
            violations.forEach(System.err::println);
            System.err.println("Next: Correct the submitted " + args[0] + " violations or verify their approved scope.");
            System.exit(1);
            return;
        }
        System.out.println("Java " + args[0] + " contract passed");
    }

    private static JsonNode read(String path) throws Exception {
        return JSON.readTree(Files.readString(Path.of(path)));
    }

    private static List<String> module(JsonNode snapshot, JsonNode java) throws Exception {
        var modules = new TreeMap<String, Set<String>>();
        for (Map.Entry<String, JsonNode> entry : java.get("modules").properties()) {
            modules.put(entry.getKey(), new TreeSet<>(strings(entry.getValue().get("publicTypes"))));
        }
        var policy = new ModuleCheck.Policy(java.get("basePackage").asString(), modules,
                new TreeSet<>(strings(java.get("commonContractTypes"))));
        return ModuleCheck.check(policy, paths(snapshot.get("production")), paths(snapshot.get("tests")),
                optionalPath(snapshot.get("productionReferences")), optionalPath(snapshot.get("testReferences")));
    }

    private static List<String> http(JsonNode policy, JsonNode approvals) throws Exception {
        var java = policy.get("java");
        String basePackage = java.get("basePackage").asString();
        var rootTypes = strings(java.get("rootTypes").get("production"));
        if (rootTypes.size() != 1) {
            throw new IllegalArgumentException("Cannot establish the Spring application class from Java policy");
        }
        Class<?> main = Class.forName(basePackage + "." + rootTypes.getFirst());
        Set<HttpMappings.Endpoint> expected = new TreeSet<>();
        for (JsonNode item : approvals.get("entries")) {
            expected.add(new HttpMappings.Endpoint(item.get("method").asString(), item.get("path").asString()));
        }
        for (String profile : List.of("", "production")) {
            var observed = collect(main, basePackage, profile);
            var violations = HttpMappings.compare(expected, observed);
            if (!violations.isEmpty()) {
                return violations;
            }
        }
        for (String profile : strings(policy.get("http").get("developmentProfiles"))) {
            collect(main, basePackage, profile);
        }
        return List.of();
    }

    private static HttpMappings.Inventory collect(Class<?> main, String basePackage, String profile) {
        var args = new ArrayList<>(List.of("--server.port=0", "--spring.main.banner-mode=off"));
        if (!profile.isEmpty()) {
            args.add("--spring.profiles.active=" + profile);
        }
        try (var context = SpringApplication.run(main, args.toArray(String[]::new))) {
            var environment = context.getEnvironment();
            Set<String> active = new TreeSet<>(Arrays.asList(environment.getActiveProfiles()));
            Set<String> defaults = new TreeSet<>(Arrays.asList(environment.getDefaultProfiles()));
            String requested = profile.isEmpty() ? "default" : profile;
            System.out.println("Spring profiles [" + requested + "]: active=" + active + ", default=" + defaults);
            if (profile.isEmpty() ? (!active.isEmpty() || !defaults.equals(Set.of("default")))
                    : !active.equals(Set.of(profile))) {
                throw new IllegalArgumentException("Unexpected active/default Spring profiles for " + requested);
            }
            var inventory = HttpMappings.collect(context, basePackage);
            System.out.println("Project mappings [" + requested + "]: " + new TreeSet<>(inventory.endpoints()));
            return inventory;
        }
    }

    private static List<String> strings(JsonNode values) {
        if (!values.isArray()) {
            throw new IllegalArgumentException("Expected a list in the Java policy or candidate snapshot");
        }
        var result = new ArrayList<String>();
        values.forEach(item -> result.add(item.asString()));
        return result;
    }

    private static List<Path> paths(JsonNode values) {
        return strings(values).stream().map(Path::of).toList();
    }

    private static Path optionalPath(JsonNode value) {
        return value.isNull() ? null : Path.of(value.asString());
    }
}
