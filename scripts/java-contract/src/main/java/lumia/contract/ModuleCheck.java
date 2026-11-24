package lumia.contract;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaModifier;
import com.tngtech.archunit.core.domain.JavaType;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/** Compares resolved bytecode dependencies with the project module policy. */
public final class ModuleCheck {
    public record Policy(String basePackage, Map<String, Set<String>> modules, Set<String> commonTypes) {}

    private final Policy policy;
    private final Map<String, Set<String>> graph = new TreeMap<>();
    private final Set<String> violations = new TreeSet<>();

    private ModuleCheck(Policy policy) {
        this.policy = policy;
        policy.modules().keySet().forEach(module -> graph.put(module, new TreeSet<>()));
    }

    public static List<String> check(Policy policy, Collection<Path> production, Collection<Path> test) {
        var check = new ModuleCheck(policy);
        check.inspectCompiled(production, test);
        check.findCycles();
        return List.copyOf(check.violations);
    }

    public static List<String> check(Policy policy, Collection<Path> production, Collection<Path> test,
                                     Path productionReferences, Path testReferences) throws IOException {
        var check = new ModuleCheck(policy);
        check.inspectCompiled(production, test);
        check.inspectSources(productionReferences, true);
        check.inspectSources(testReferences, false);
        check.findCycles();
        return List.copyOf(check.violations);
    }

    private void inspectCompiled(Collection<Path> production, Collection<Path> test) {
        var importer = new ClassFileImporter();
        var productionNames = new TreeSet<String>();
        if (!production.isEmpty()) {
            var classes = importer.importPaths(production);
            classes.forEach(type -> productionNames.add(type.getName()));
            inspect(classes, true);
        }
        if (!test.isEmpty()) {
            var paths = new ArrayList<>(production);
            paths.addAll(test);
            inspect(importer.importPaths(paths).stream()
                    .filter(type -> !productionNames.contains(type.getName())).toList(), false);
        }
    }

    private void inspectSources(Path report, boolean production) throws IOException {
        if (report == null) {
            return;
        }
        for (String line : Files.readAllLines(report)) {
            String[] row = line.split("\t", -1);
            if (row.length != 5 || !Set.of("true", "false").contains(row[4])) {
                throw new IllegalArgumentException("Unrecognized Java compiler reference report: " + report);
            }
            String sourceOwner = owner(row[0]);
            String targetOwner = owner(row[2]);
            if (sourceOwner != null && targetOwner != null && !sourceOwner.equals(targetOwner)) {
                var target = new TypeName(row[2], row[3], Boolean.parseBoolean(row[4]));
                recordUse(sourceOwner, targetOwner, target, production, row[1] + " references " + row[3]);
            }
        }
    }

    private void inspect(Iterable<JavaClass> sources, boolean production) {
        for (var origin : sources) {
            String owner = owner(origin.getPackageName());
            if (owner == null) {
                continue;
            }
            TypeName sourceName = typeName(origin);
            boolean listed = policy.modules().getOrDefault(owner, Set.of()).contains(sourceName.name());
            boolean exported = isPublicType(owner, sourceName);
            if (listed && !exported) {
                violations.add("Registered Java contract is not publicly accessible: " + sourceName.name());
            }
            for (var dependency : origin.getDirectDependenciesFromSelf()) {
                var target = dependency.getTargetClass().getBaseComponentType();
                String targetOwner = owner(target.getPackageName());
                if (targetOwner == null) {
                    continue;
                }
                TypeName targetName = typeName(target);
                if (!owner.equals(targetOwner)) {
                    recordUse(owner, targetOwner, targetName, production, dependency.getDescription());
                }
                // A contract exposing an internal type has already made that type part of its API.
                if (exported && !isPublicType(targetOwner, targetName) && !isCommonContract(targetName)
                        && exposedInSignature(origin, target)) {
                    violations.add("Public Java contract " + sourceName.name()
                            + " exposes inaccessible type " + targetName.name());
                }
            }
        }
    }

    private void recordUse(String origin, String destination, TypeName target,
                           boolean production, String description) {
        if (!canUse(origin, destination, target, production)) {
            violations.add("Forbidden Java dependency: " + description);
        }
        if (production && graph.containsKey(origin) && graph.containsKey(destination)) {
            graph.get(origin).add(destination);
        }
    }

    private boolean exposedInSignature(JavaClass origin, JavaClass target) {
        return origin.getTypeParameters().stream().flatMap(type -> type.getUpperBounds().stream())
                        .anyMatch(type -> containsType(type, target))
                || origin.getFields().stream().filter(field -> isVisible(field.getModifiers()))
                        .anyMatch(field -> containsType(field.getType(), target))
                || origin.getMethods().stream().filter(method -> isVisible(method.getModifiers()))
                        .anyMatch(method -> containsType(method.getReturnType(), target)
                                || method.getTypeParameters().stream().flatMap(type -> type.getUpperBounds().stream())
                                        .anyMatch(type -> containsType(type, target))
                                || method.getParameterTypes().stream()
                                        .anyMatch(type -> containsType(type, target))
                                || method.getExceptionTypes().contains(target))
                || origin.getConstructors().stream().filter(ctor -> isVisible(ctor.getModifiers()))
                        .anyMatch(ctor -> ctor.getTypeParameters().stream().flatMap(type -> type.getUpperBounds().stream())
                                        .anyMatch(type -> containsType(type, target))
                                || ctor.getParameterTypes().stream().anyMatch(type -> containsType(type, target))
                                || ctor.getExceptionTypes().contains(target))
                || origin.getSuperclass().stream().anyMatch(type -> containsType(type, target))
                || origin.getInterfaces().stream().anyMatch(type -> containsType(type, target));
    }

    private static boolean containsType(JavaType signature, JavaClass target) {
        return signature.getAllInvolvedRawTypes().stream()
                .anyMatch(type -> type.getBaseComponentType().equals(target));
    }

    private static boolean isVisible(Set<JavaModifier> modifiers) {
        return modifiers.contains(JavaModifier.PUBLIC) || modifiers.contains(JavaModifier.PROTECTED);
    }

    private String owner(String packageName) {
        String prefix = policy.basePackage() + ".";
        if (packageName.equals(policy.basePackage())) {
            return "";
        }
        if (!packageName.startsWith(prefix)) {
            return null;
        }
        return packageName.substring(prefix.length()).split("\\.", 2)[0];
    }

    private record TypeName(String packageName, String name, boolean publicType) {}

    private static TypeName typeName(JavaClass type) {
        boolean publicType = type.getModifiers().contains(JavaModifier.PUBLIC);
        for (var enclosing = type.getEnclosingClass(); publicType && enclosing.isPresent();
                enclosing = enclosing.get().getEnclosingClass()) {
            publicType = enclosing.get().getModifiers().contains(JavaModifier.PUBLIC);
        }
        return new TypeName(type.getPackageName(), type.getName().replace('$', '.'), publicType);
    }

    private boolean isPublicType(String module, TypeName type) {
        String api = policy.basePackage() + "." + module + ".api";
        return type.publicType() && (type.packageName().equals(api) || type.packageName().startsWith(api + "."))
                && policy.modules().getOrDefault(module, Set.of()).contains(type.name());
    }

    private boolean isCommonContract(TypeName type) {
        return type.publicType() && policy.commonTypes().contains(type.name());
    }

    private boolean canUse(String owner, String destination, TypeName target, boolean production) {
        if (owner.equals("common") || destination.isEmpty()) {
            return false;
        }
        if (destination.equals("fixture")) {
            return !production;
        }
        if (destination.equals("dev")) {
            return !production && owner.isEmpty();
        }
        if (destination.equals("common")) {
            return (!production && owner.isEmpty()) || isCommonContract(target);
        }
        return isPublicType(destination, target);
    }

    private void findCycles() {
        var visited = new TreeSet<String>();
        var active = new LinkedHashMap<String, Integer>();
        for (String module : graph.keySet()) {
            visit(module, visited, active);
        }
    }

    private void visit(String module, Set<String> visited, LinkedHashMap<String, Integer> active) {
        Integer start = active.get(module);
        if (start != null) {
            var route = new ArrayList<>(active.keySet()).subList(start, active.size());
            violations.add("Java module cycle: " + String.join(" -> ", route) + " -> " + module);
            return;
        }
        if (!visited.add(module)) {
            return;
        }
        active.put(module, active.size());
        graph.get(module).forEach(target -> visit(target, visited, active));
        active.remove(module);
    }
}
