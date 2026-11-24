package lumia.contract;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sun.source.util.JavacTask;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.tools.ToolProvider;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

final class ModuleCheckTest {
    private static final Set<String> COMMON_TYPES = Set.of("example.common.api.Message");
    private static final ModuleCheck.Policy POLICY = new ModuleCheck.Policy(
            "example", Map.of(
                    "alpha", Set.of("example.alpha.api.Alpha"),
                    "beta", Set.of("example.beta.api.Beta"),
                    "gamma", Set.of("example.gamma.api.Gamma")), COMMON_TYPES);

    @TempDir Path directory;

    @Test
    void allowsPublicNonCyclicReferencesAndSameModuleInternalTypes() throws Exception {
        Path out = compile("main", null, Map.of(
                "alpha.application.Use", """
                        public class Use {
                            example.beta.api.Beta api;
                            example.alpha.domain.PrivateType own;
                            example.common.api.Message message;
                        }
                        """,
                "alpha.domain.PrivateType", "public class PrivateType {}",
                "beta.api.Beta", "public class Beta {}",
                "common.api.Message", "public class Message {}"));
        assertEquals(List.of(), ModuleCheck.check(POLICY, List.of(out), List.of()));
    }

    @Test
    void rejectsFullyQualifiedInternalAndUnregisteredApiTypes() throws Exception {
        Path out = compile("main", null, Map.of(
                "alpha.application.Use", """
                        public class Use {
                            example.beta.domain.PrivateType internal;
                            example.beta.api.Unregistered unregistered;
                        }
                        """,
                "beta.domain.PrivateType", "public class PrivateType {}",
                "beta.api.Unregistered", "public class Unregistered {}"));
        var violations = ModuleCheck.check(POLICY, List.of(out), List.of());
        assertTrue(violations.stream().anyMatch(line -> line.contains("beta.domain.PrivateType")), violations.toString());
        assertTrue(violations.stream().anyMatch(line -> line.contains("beta.api.Unregistered")), violations.toString());
    }

    @Test
    void detectsApiExposingAnInternalGenericType() throws Exception {
        Path out = compile("main", null, Map.of(
                "alpha.api.Alpha", """
                        public interface Alpha {
                            java.util.List<example.alpha.domain.Secret> secret();
                        }
                        """,
                "alpha.domain.Secret", "public class Secret {}"));
        var violations = ModuleCheck.check(POLICY, List.of(out), List.of());
        assertTrue(violations.contains(
                "Public Java contract example.alpha.api.Alpha exposes inaccessible type example.alpha.domain.Secret"),
                violations.toString());
    }

    @Test
    void detectsBoundsOnPublicTypesMethodsAndConstructors() throws Exception {
        Path out = compile("main", null, Map.of(
                "alpha.api.Alpha", """
                        public class Alpha<T extends example.alpha.domain.TypeBound> {
                            public <C extends example.alpha.domain.ConstructorBound> Alpha() {}
                            public <M extends example.alpha.domain.MethodBound> void method() {}
                        }
                        """,
                "alpha.domain.TypeBound", "public class TypeBound {}",
                "alpha.domain.ConstructorBound", "public class ConstructorBound {}",
                "alpha.domain.MethodBound", "public class MethodBound {}"));
        var violations = ModuleCheck.check(POLICY, List.of(out), List.of());
        for (String type : List.of("TypeBound", "ConstructorBound", "MethodBound")) {
            assertTrue(violations.stream().anyMatch(line -> line.endsWith("alpha.domain." + type)),
                    violations.toString());
        }
    }

    @Test
    void detectsReferencesErasedByCompilation() throws Exception {
        Path out = compile("main", null, Map.of(
                "alpha.application.Probe", """
                        public class Probe {
                            int value() {
                                example.beta.domain.Local erased = null;
                                return example.beta.domain.Constants.NUMBER;
                            }
                        }
                        """,
                "beta.domain.Local", "public class Local {}",
                "beta.domain.Constants", "public class Constants { public static final int NUMBER = 17; }"));
        var violations = ModuleCheck.check(POLICY, List.of(out), List.of(), directory.resolve("main.refs"), null);
        for (String type : List.of("Local", "Constants")) {
            assertTrue(violations.stream().anyMatch(line -> line.endsWith("beta.domain." + type)),
                    violations.toString());
        }
    }

    @Test
    void sourceOnlyPackageAnnotationIsChecked() throws Exception {
        Path out = compile("main", null, Map.of(
                "alpha.package-info", "@example.beta.domain.InternalTag package example.alpha;",
                "beta.domain.InternalTag", """
                        @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.SOURCE)
                        public @interface InternalTag {}
                        """));
        var violations = ModuleCheck.check(POLICY, List.of(out), List.of(), directory.resolve("main.refs"), null);
        assertTrue(violations.stream().anyMatch(line -> line.contains("alpha.package-info")
                && line.endsWith("beta.domain.InternalTag")), violations.toString());
    }

    @Test
    void separatelyListedNestedTypeHasSamePolicyWithEitherSpelling() throws Exception {
        var policy = new ModuleCheck.Policy("example",
                Map.of("alpha", Set.of(), "beta", Set.of("example.beta.api.Outer.Nested")), COMMON_TYPES);
        Path out = compile("main", null, Map.of(
                "alpha.application.FullyQualified", """
                        public class FullyQualified { example.beta.api.Outer.Nested value; }
                        """,
                "alpha.application.Imported", """
                        import example.beta.api.Outer.Nested;
                        public class Imported { Nested value; }
                        """,
                "beta.api.Outer", "public class Outer { public static class Nested {} }"));
        assertEquals(List.of(), ModuleCheck.check(policy, List.of(out), List.of(), directory.resolve("main.refs"), null));
    }

    @Test
    void rejectsAnUnreachableRegisteredContractAndRootInternalUse() throws Exception {
        var policy = new ModuleCheck.Policy("example", Map.of(
                "alpha", Set.of("example.alpha.api.Wrapper.PublicType")), COMMON_TYPES);
        Path out = compile("main", null, Map.of(
                "alpha.api.Wrapper", "class Wrapper { public static class PublicType {} }",
                "alpha.domain.Internal", "public class Internal {}",
                "Bootstrap", "public class Bootstrap { example.alpha.domain.Internal internal; }"));
        var violations = ModuleCheck.check(policy, List.of(out), List.of());
        assertTrue(violations.contains(
                "Registered Java contract is not publicly accessible: example.alpha.api.Wrapper.PublicType"),
                violations.toString());
        assertTrue(violations.stream().anyMatch(line -> line.contains("Bootstrap")
                && line.contains("alpha.domain.Internal")), violations.toString());
    }

    @Test
    void sharedFixturesAreAvailableOnlyToTests() throws Exception {
        Path main = compile("main", null, Map.of(
                "alpha.api.Alpha", "public class Alpha { example.fixture.Setup fixture; }",
                "fixture.Setup", "public class Setup {}"));
        assertTrue(ModuleCheck.check(POLICY, List.of(main), List.of()).stream()
                .anyMatch(line -> line.contains("fixture.Setup")));
        Path clean = compile("clean", null, Map.of("alpha.api.Alpha", "public class Alpha {}"));
        Path tests = compile("tests", clean, Map.of(
                "alpha.application.Probe", "public class Probe { example.fixture.Setup fixture; }",
                "fixture.Setup", "public class Setup {}"));
        assertEquals(List.of(), ModuleCheck.check(POLICY, List.of(clean), List.of(tests)));
    }

    @Test
    void reportsDirectAndIndirectProductionCycles() throws Exception {
        Path direct = compile("direct", null, Map.of(
                "alpha.api.Alpha", "public class Alpha { example.beta.api.Beta other; }",
                "beta.api.Beta", "public class Beta { example.alpha.api.Alpha other; }"));
        assertEquals(List.of("Java module cycle: alpha -> beta -> alpha"),
                ModuleCheck.check(POLICY, List.of(direct), List.of()));

        Path indirect = compile("indirect", null, Map.of(
                "alpha.api.Alpha", "public class Alpha { example.beta.api.Beta other; }",
                "beta.api.Beta", "public class Beta { example.gamma.api.Gamma other; }",
                "gamma.api.Gamma", "public class Gamma { example.alpha.api.Alpha other; }"));
        assertEquals(List.of("Java module cycle: alpha -> beta -> gamma -> alpha"),
                ModuleCheck.check(POLICY, List.of(indirect), List.of()));
    }

    @Test
    void testReferencesRespectVisibilityWithoutCreatingProductionCycle() throws Exception {
        Path main = compile("main", null, Map.of(
                "alpha.api.Alpha", "public class Alpha { example.beta.api.Beta other; }",
                "alpha.domain.PrivateType", "public class PrivateType {}",
                "beta.api.Beta", "public class Beta {}"));
        Path test = compile("test", main, Map.of(
                "beta.application.Probe", """
                        public class Probe {
                            example.alpha.api.Alpha allowed;
                            example.alpha.domain.PrivateType denied;
                        }
                        """));
        var violations = ModuleCheck.check(POLICY, List.of(main), List.of(test));
        assertEquals(1, violations.size(), violations.toString());
        assertTrue(violations.getFirst().contains("alpha.domain.PrivateType"), violations.toString());
    }

    private Path compile(String stage, Path classpath, Map<String, String> types) throws Exception {
        Path output = Files.createDirectories(directory.resolve(stage + "-classes"));
        Path sources = directory.resolve(stage + "-src");
        var args = new ArrayList<>(List.of("-d", output.toString(), "-proc:none"));
        var files = new ArrayList<Path>();
        if (classpath != null) {
            args.addAll(List.of("-classpath", classpath.toString()));
        }
        for (var entry : types.entrySet()) {
            String name = entry.getKey();
            Path path = sources.resolve(name.replace('.', '/') + ".java");
            Files.createDirectories(path.getParent());
            int packageEnd = name.lastIndexOf('.');
            String packageName = packageEnd == -1 ? "example" : "example." + name.substring(0, packageEnd);
            String declaration = name.endsWith(".package-info") ? "" : "package " + packageName + ";\n";
            Files.writeString(path, declaration + entry.getValue());
            files.add(path);
        }
        var compiler = ToolProvider.getSystemJavaCompiler();
        try (var fileManager = compiler.getStandardFileManager(null, null, null)) {
            var task = (JavacTask) compiler.getTask(null, fileManager, null, args, null,
                    fileManager.getJavaFileObjectsFromPaths(files));
            SourceReferences.attach(task, directory.resolve(stage + ".refs"));
            assertTrue(task.call());
        }
        return output;
    }
}
