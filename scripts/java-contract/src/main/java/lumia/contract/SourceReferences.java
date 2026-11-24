package lumia.contract;

import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MemberReferenceTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.Plugin;
import com.sun.source.util.TaskEvent;
import com.sun.source.util.TaskListener;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.TreeSet;
import javax.lang.model.element.Element;
import javax.lang.model.element.Modifier;
import javax.lang.model.element.TypeElement;
import javax.lang.model.util.Elements;

/** Collects references that the JVM compiler may erase, such as constant reads. */
public final class SourceReferences implements Plugin {
    @Override
    public String getName() {
        return "LumiaModuleReferences";
    }

    @Override
    public void init(JavacTask task, String... args) {
        if (args.length != 1) {
            throw new IllegalArgumentException("LumiaModuleReferences requires a report URI");
        }
        attach(task, Path.of(URI.create(args[0])));
    }

    static void attach(JavacTask task, Path report) {
        var trees = Trees.instance(task);
        var elements = task.getElements();
        var references = new TreeSet<String>();
        task.addTaskListener(new TaskListener() {
            @Override
            public void finished(TaskEvent event) {
                if (event.getKind() == TaskEvent.Kind.ANALYZE
                        && event.getSourceFile().getName().endsWith("package-info.java")) {
                    var unit = event.getCompilationUnit();
                    String sourcePackage = unit.getPackageName().toString();
                    for (var annotation : unit.getPackageAnnotations()) {
                        new Scan(trees, sourcePackage + ".package-info", sourcePackage, elements, references)
                                .scan(TreePath.getPath(unit, annotation), null);
                    }
                    return;
                }
                if (event.getKind() == TaskEvent.Kind.ANALYZE && event.getTypeElement() != null) {
                    TypeElement origin = event.getTypeElement();
                    var path = trees.getPath(origin);
                    if (path != null) {
                        new Scan(trees, origin.getQualifiedName().toString(),
                                elements.getPackageOf(origin).getQualifiedName().toString(),
                                elements, references).scan(path, null);
                    }
                }
                if (event.getKind() == TaskEvent.Kind.COMPILATION) {
                    try {
                        Files.write(report, references);
                    } catch (IOException e) {
                        throw new UncheckedIOException(e);
                    }
                }
            }
        });
    }

    private static final class Scan extends TreePathScanner<Void, Void> {
        private final Trees trees;
        private final String origin;
        private final String sourcePackage;
        private final Elements elements;
        private final Set<String> references;

        private Scan(Trees trees, String origin, String sourcePackage,
                     Elements elements, Set<String> references) {
            this.trees = trees;
            this.origin = origin;
            this.sourcePackage = sourcePackage;
            this.elements = elements;
            this.references = references;
        }

        @Override
        public Void visitIdentifier(IdentifierTree node, Void unused) {
            record();
            return super.visitIdentifier(node, unused);
        }

        @Override
        public Void visitMemberSelect(MemberSelectTree node, Void unused) {
            record();
            return super.visitMemberSelect(node, unused);
        }

        @Override
        public Void visitMemberReference(MemberReferenceTree node, Void unused) {
            record();
            return super.visitMemberReference(node, unused);
        }

        private void record() {
            Element element = trees.getElement(getCurrentPath());
            while (element != null && !(element instanceof TypeElement)) {
                element = element.getEnclosingElement();
            }
            if (element instanceof TypeElement target) {
                String qualifiedName = target.getQualifiedName().toString();
                if (!qualifiedName.isEmpty() && !qualifiedName.equals(origin) && !isTypeQualifier()) {
                    String targetPackage = elements.getPackageOf(target).getQualifiedName().toString();
                    references.add(String.join("\t", sourcePackage, origin,
                            targetPackage, qualifiedName, Boolean.toString(isPublic(target))));
                }
            }
        }

        private boolean isTypeQualifier() {
            var current = getCurrentPath();
            var parent = current.getParentPath();
            return parent != null && parent.getLeaf() instanceof MemberSelectTree selection
                    && selection.getExpression() == current.getLeaf()
                    && trees.getElement(parent) instanceof TypeElement;
        }

        private static boolean isPublic(TypeElement target) {
            for (Element element = target; element instanceof TypeElement; element = element.getEnclosingElement()) {
                if (!element.getModifiers().contains(Modifier.PUBLIC)) {
                    return false;
                }
            }
            return true;
        }
    }
}
