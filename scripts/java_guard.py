"""Check Java placement and trusted change scope against Git candidates."""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re

from harness_inventory import Candidate, path_name


POLICY = "docs/details/development/java-policy.json"
SOURCES = {"production": "backend/src/main/java", "test": "backend/src/test/java"}
INPUTS = (*SOURCES.values(), POLICY)
INDEX_PATHS = (".", ":(exclude)harness-design", ":(exclude).harness-state")
MAX_INPUT = 2_000_000


class Violation(ValueError):
    """The applicable rule and actual mismatch were both verified."""


def parse_json(raw):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    if raw is None or len(raw) > MAX_INPUT:
        raise ValueError("Required JSON input is absent or too large")
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=object_pairs)


def git_commit(view, ref):
    return view.git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()


def source_kind(path):
    if path.endswith(".java"):
        return next((key for key, root in SOURCES.items() if path.startswith(root + "/")), None)
    return None


@dataclass(frozen=True)
class Change:
    operation: str
    path: str
    from_path: str | None = None
    behavior: bool = False

    def description(self):
        result = {"operation": self.operation, "path": self.path}
        if self.from_path is not None:
            result["fromPath"] = self.from_path
        return result

    def production_targets(self):
        if not self.behavior:
            return []
        return [path for path in (self.from_path, self.path)
                if path and source_kind(path) == "production"]


def changes_between(view, base):
    args = ("--cached", *([base] if base else [])) if view.kind == "index" else (base, view.commit)
    names = view.git("diff", "--name-status", "-z", "--find-renames", *args, "--", *INPUTS)
    fields = iter(names.decode("utf-8").rstrip("\0").split("\0"))
    changes = []
    for status in fields:
        if not status:
            break
        path = path_name(next(fields))
        if status.startswith("R"):
            destination = path_name(next(fields))
            changes.append(Change("move", destination, path, True))
        elif status in ("A", "M", "D"):
            operation = {"A": "create", "M": "modify", "D": "delete"}[status]
            changes.append(Change(operation, path, behavior=True))
        else:
            raise ValueError(f"Unsupported or unresolved Git change at {path}")
    return [change for change in changes
            if change.path == POLICY or change.from_path == POLICY
            or source_kind(change.path) or (change.from_path and source_kind(change.from_path))]


def index_identity(view):
    entries = view.git("ls-files", "--stage", "-z", "--", *INDEX_PATHS)
    return "index:" + hashlib.sha256(entries).hexdigest()


def edit_identity(changes):
    operations = json.dumps([change.description() for change in changes], sort_keys=True).encode()
    return "edit:" + hashlib.sha256(operations).hexdigest()


def json_changes(before, after, pointer=""):
    if type(before) is not type(after):
        yield {"op": "replace", "path": pointer, "before": before, "after": after}
    elif isinstance(before, dict):
        for key in sorted(before.keys() | after.keys()):
            nested = pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in before:
                yield {"op": "add", "path": nested, "after": after[key]}
            elif key not in after:
                yield {"op": "remove", "path": nested, "before": before[key]}
            else:
                yield from json_changes(before[key], after[key], nested)
    elif before != after:
        yield {"op": "replace", "path": pointer, "before": before, "after": after}


def names(value):
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("Policy name arrays must contain only strings")
    if len(set(value)) != len(value):
        raise ValueError("Duplicate policy name")
    return value


class Policy:
    def __init__(self, raw):
        self.data = parse_json(raw)
        if type(self.data["version"]) is not int or self.data["version"] != 1:
            raise ValueError("Unsupported Java policy version")
        self.java = self.data["java"]
        if self.java["sourceRoots"] != SOURCES:
            raise ValueError("Unsupported Java source roots")
        self.base_package = self.java["basePackage"]
        self.segment = re.compile(self.java["packageSegmentPattern"], re.ASCII)
        self.type_name = re.compile(self.java["typeNamePattern"], re.ASCII)
        if not self.base_package or any(not self.segment.fullmatch(part) for part in self.base_package.split(".")):
            raise ValueError("Invalid Java base package")
        for mapping in ("rootTypes", "reservedPackages"):
            for source in SOURCES:
                names(self.java[mapping][source])
        names(self.java["modulePackages"])
        names(self.java["commonContractTypes"])
        names(self.data["http"]["developmentProfiles"])
        self.modules = self.java["modules"]
        for module, settings in self.modules.items():
            if module in ("common", "dev", "fixture") or not self.segment.fullmatch(module):
                raise ValueError(f"Invalid or reserved Java module: {module}")
            if not all(isinstance(settings[key], str) and settings[key].strip()
                       for key in ("owner", "responsibility")):
                raise ValueError(f"Java module ownership is missing: {module}")
            public_types = names(settings["publicTypes"])
            if any(not name.startswith(f"{self.base_package}.{module}.api.") for name in public_types):
                raise ValueError(f"Public types must be in the module api package: {module}")
            for source in SOURCES:
                names(settings["extraPackages"][source])

    def allows(self, source, package, class_name):
        if package == self.base_package:
            return class_name in self.java["rootTypes"][source]
        base = self.base_package + "."
        if not package.startswith(base):
            return False
        relative = package.removeprefix(base)
        if relative in self.java["reservedPackages"][source]:
            return True
        module, _, role = relative.partition(".")
        return module in self.modules and (
            role in self.java["modulePackages"] or role in self.modules[module]["extraPackages"][source]
        )


# Discard comments and literals before examining package and top-level type tokens.
JAVA_TOKENS = re.compile(
    r'(?P<ignored>//[^\r\n]*|/\*.*?\*/|""".*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
    r'|(?P<token>[\w$]+|[^\s])', re.DOTALL
)
PACKAGE = re.compile(r"\bpackage ([\w$]+(?: \. [\w$]+)*) ;")
UNICODE_ESCAPE = re.compile(r"\\u+([0-9a-fA-F]{4})")


def translate_java_unicode(text):
    # Java translates eligible raw Unicode escapes before tokenization (JLS 3.3).
    if "\\u" not in text:
        return text
    translated = []
    offset = 0
    backslashes = 0
    previous_escape = False
    while offset < len(text):
        char = text[offset]
        eligible = char == "\\" and (previous_escape or backslashes % 2 == 0)
        previous_escape = eligible and text.startswith("u", offset + 1)
        if previous_escape:
            match = UNICODE_ESCAPE.match(text, offset)
            if not match:
                raise ValueError("Malformed Java Unicode escape")
            char = chr(int(match[1], 16))
            offset = match.end()
        else:
            offset += 1
        backslashes = backslashes + 1 if char == "\\" else 0
        translated.append(char)
    return "".join(translated)


def placement(view, policy, path):
    source = source_kind(path)
    relative = path.removeprefix(SOURCES[source] + "/")
    directory, _, filename = relative.rpartition("/")
    package = directory.replace("/", ".")
    class_name = filename.removesuffix(".java")
    if not package or any(not policy.segment.fullmatch(part) for part in package.split(".")):
        raise Violation(f"{path}: directory does not form an allowed package name")
    if filename != "package-info.java" and not policy.type_name.fullmatch(class_name):
        raise Violation(f"{path}: Java file name does not match the type naming rule")
    raw = view.read(path)
    if raw is None or len(raw) > MAX_INPUT:
        raise ValueError(f"{path}: candidate Java source is absent or too large")
    text = translate_java_unicode(raw.decode("utf-8-sig"))
    tokens = [match["token"] for match in JAVA_TOKENS.finditer(text) if match["token"]]
    declared = PACKAGE.findall(" ".join(tokens))
    if declared != [package.replace(".", " . ")]:
        raise Violation(f"{path}: package declaration must be {package}")
    depth = 0
    types = set()
    for index, token in enumerate(tokens[:-1]):
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1
        elif depth == 0 and token in ("class", "interface", "enum", "record"):
            if index == 0 or tokens[index - 1] != ".":
                types.add(tokens[index + 1])
    if filename == "package-info.java":
        if types:
            raise Violation(f"{path}: package-info must not declare top-level types")
    elif class_name not in types:
        raise Violation(f"{path}: top-level type {class_name} is missing")
    return source, package, class_name


class Authorization:
    def __init__(self, view, base, candidate_id, context_path=None):
        self.base = base
        self.candidate = candidate_id
        self.view = view
        self.data = {}
        if context_path:
            path = Path(context_path)
            resolved = path.resolve(strict=True)
            if not path.is_absolute() or path.is_symlink() or path.is_junction() or resolved.is_relative_to(view.root):
                raise ValueError("Approval context must be supplied by a trusted caller outside the candidate worktree")
            if not resolved.is_file() or resolved.stat().st_size > MAX_INPUT:
                raise ValueError("Approval context is not a bounded regular file")
            self.data = parse_json(resolved.read_bytes())
            if self.data["candidateId"] != candidate_id or self.data["baseRevision"] != base:
                raise ValueError("Approval context belongs to a different candidate or base")

    def source(self, reference):
        ref = reference["ref"]
        path = path_name(reference["path"])
        anchor = reference["anchor"]
        if not path.startswith("work/records/") or not re.fullmatch(r"[\w-]+", anchor):
            raise ValueError("Approval does not cite a valid project work record and anchor")
        # An event is an attestation from the externally provisioned trusted caller.
        if re.fullmatch(r"event:[\w.-]+", ref):
            return
        if not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", ref):
            raise ValueError("Approval source must name a pinned Git revision or verified event")
        # Use merge-base output instead of trusting a branch or ref supplied by the candidate.
        ancestor = self.view.git("merge-base", ref, self.base).decode().strip()
        if ancestor != ref:
            raise Violation("Approval source is only present outside the verified base history")
        raw = Candidate(ref, cwd=self.view.root, seconds=5).read(path)
        if raw is None or f'id="{anchor}"' not in raw.decode("utf-8-sig"):
            raise ValueError("Approval source record or anchor is unreadable")

    def scopes(self, changes):
        record = self.data.get("taskScope")
        if record is None:
            raise ValueError(f"{changes[0].path}: verified Task scope is required for the actual changes")
        if record["status"] in ("confirmed-absent", "expired"):
            raise Violation("The candidate has no effective Task scope")
        if record["status"] != "verified":
            raise ValueError("Task scope could not be verified")
        self.source(record["source"])
        scopes = {}
        for change in changes:
            match = next((item for item in record["changes"]
                          if item["path"] == change.path
                          and item["operation"] == change.operation
                          and item.get("fromPath") == change.from_path
                          and item.get("scope")), None)
            if match is None:
                raise Violation(f"{change.path}: {change.operation} is outside the approved Task scope")
            for target in change.production_targets():
                scopes[target] = names(match.get("tddExceptions", []))
        return scopes

    def approval(self, predicate, description):
        unresolved = False
        for identity, entry in self.data.get("approvals", {}).items():
            status = entry["status"]
            record = entry.get("record")
            if status not in ("verified", "confirmed-absent", "expired", "unconfirmed"):
                raise ValueError("Approval status is unreadable")
            if status == "unconfirmed" and (record is None or predicate(record)):
                unresolved = True
            if status != "verified" or record is None or not predicate(record):
                continue
            if (record["id"] != identity or not record["approver"]["id"]
                    or not record["approver"]["authority"] or not record["reason"] or not record["limits"]):
                raise ValueError("Approval authority or application limits are unreadable")
            if record["kind"] == "exception" and (not record["endsWhen"] or not record["cleanupOwner"]):
                raise ValueError("Exception expiration or cleanup responsibility is unreadable")
            self.source(record["source"])
            return
        if not self.data or unresolved or self.data.get("approvalsComplete") is not True:
            raise ValueError(f"{description}: approval record or effect is unverified")
        raise Violation(f"{description}: no effective approval covers the change")


def delegate_covers(record, delta, old_policy):
    match = re.fullmatch(r"/java/modules/(\w+)/extraPackages/(production|test)", delta["path"])
    if (not match or delta["op"] != "replace" or match[1] not in old_policy.modules
            or not set(delta["before"]) < set(delta["after"])):
        return False
    module, source = match.groups()
    added = set(delta["after"]) - set(delta["before"])
    return all(any(
        item["source"] == source and item["owner"] == old_policy.modules[module]["owner"]
        and item["package"] == f"{old_policy.base_package}.{module}.{role}" and item["visibility"] == "internal"
        for item in record["scope"]["packages"]
    ) for role in added)


def check_policy(authorization, before, after):
    for delta in json_changes(before.data, after.data):
        authorization.approval(
            lambda record: delta in record["scope"]["policy"] and (
                record["kind"] == "policy" or (record["kind"] == "delegation" and delegate_covers(record, delta, before))
            ),
            "Policy " + delta["path"],
        )


def check_place(authorization, previous, candidate, change, properties):
    source, package, class_name = properties
    allowed = candidate.allows(source, package, class_name)
    if allowed and previous.allows(source, package, class_name):
        return

    relative = package.removeprefix(candidate.base_package + ".")
    module = candidate.modules.get(relative.split(".")[0])
    authority_kinds = ("delegation", "policy") if allowed else ("exception",)
    authorization.approval(
        lambda record: record["kind"] in authority_kinds and any(
            scope["source"] == source and scope["package"] == package and change.operation in scope["operations"]
            and (module is None or module["owner"] == scope["owner"])
            and (record["kind"] != "delegation" or scope["visibility"] == "internal")
            for scope in record["scope"]["packages"]
        ),
        change.path,
    )


def configured_context(path, *, edit=False):
    variable = "LUMIA_JAVA_EDIT_APPROVAL_CONTEXT" if edit else "LUMIA_JAVA_APPROVAL_CONTEXT"
    return path or os.environ.get(variable)
