"""Run unittest using only the standard library and emit a fresh JSON report."""

import argparse
import json
import os
from pathlib import Path
import sys
import unittest

from tdd_core import safe_path


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.names = []
        self.failed_names = []

    def startTest(self, test):
        self.names.append(test.id())
        super().startTest(test)

    def addFailure(self, test, err):
        self.failed_names.append(test.id())
        super().addFailure(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None and issubclass(err[0], test.failureException):
            self.failed_names.append(test.id())
        super().addSubTest(test, subtest, err)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    output = Path(args.report)
    if output.is_absolute():
        try:
            output = output.resolve().relative_to(root)
        except ValueError:
            parser.error("report must stay in this workspace's .tmp directory")
    try:
        path = safe_path(root, output.as_posix())
        if not path.is_relative_to(root / ".tmp"):
            parser.error("report must stay in this workspace's .tmp directory")
    except ValueError:
        parser.error("report path is outside the permitted temporary scope")
    command = args.args[1:] if args.args[:1] == ["--"] else args.args
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path.cwd()))
    program = unittest.TestProgram(module=None, argv=["unittest", *command], exit=False,
                                   testRunner=unittest.TextTestRunner(resultclass=Result, verbosity=2))
    result = program.result
    report = {"schema": 1, "runId": args.run_id, "tests": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors) + len(result.unexpectedSuccesses),
              "skipped": len(result.skipped) + len(result.expectedFailures),
              "names": result.names, "failedNames": list(dict.fromkeys(result.failed_names))}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
