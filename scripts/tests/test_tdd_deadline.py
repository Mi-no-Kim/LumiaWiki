import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tdd_core as core


class DeadlineTests(unittest.TestCase):
    def test_slow_inspection_explicitly_denies_before_outer_timeout(self):
        path = Path(__file__).resolve().parents[1] / "tdd-check.py"
        spec = importlib.util.spec_from_file_location("tdd_check_deadline_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def slow_repository():
            time.sleep(4)
            raise ValueError("synthetic slow inspection")

        output = io.StringIO()
        previous = core.DEADLINE
        try:
            with patch.object(core, "repository", slow_repository), patch.object(sys, "argv", [str(path), "--hook"]), patch.object(sys, "stdin", io.StringIO("{}")), contextlib.redirect_stdout(output):
                started = time.monotonic()
                self.assertEqual(0, module.main())
                elapsed = time.monotonic() - started
            self.assertLess(elapsed, 3.5)
            self.assertEqual("deny", json.loads(output.getvalue())["hookSpecificOutput"]["permissionDecision"])
        finally:
            core.DEADLINE = previous
