#!/usr/bin/env python3
"""FW01 bounded source plants; execute the actual guard definitions on tiny trees."""
import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
TEST = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST))
import residue

source = (TEST / "validate.py").read_text()
start = source.index("# ------------------------------ every temp tree")
end = source.index("# ------------------------------------ back-links", start)
module = ast.parse(source[start:end])
# Constants and definitions only: no unrelated validator or top-level controls.
parts = [n for n in module.body if isinstance(n, ast.FunctionDef) or
         isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and
                                           t.id.startswith("TEMP_") for t in n.targets)]
errors = []
guard = {"os": os, "re": re, "fail": errors.append}
exec(compile(ast.Module(body=parts, type_ignores=[]), "guard-under-test", "exec"), guard)
ledger = (TEST / "residue.py").read_text()
maker = "mkd" + "temp"


def check(name, files, expect):
    residue.open_case(name)
    root = Path(residue.workspace("temp-guard"))
    entries = {"test/residue.py": ledger, "test/ok.py": "import residue\np = residue.workspace('ok')\n"}
    entries.update(files)
    for path, text in entries.items():
        dst = root / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text)
    errors.clear()
    guard["check_temp_trees_go_through_the_residue_ledger"](str(root))
    if expect:
        assert any(expect in error for error in errors), (name, errors)
    else:
        assert not errors, (name, errors)
    residue.close_case(name)


cases = [
    ("shipped alias", {"plugins/demo/scripts/leak.py": "from tempfile import " + maker + " as make\np = make()\n"}, "plugins/demo/scripts/leak.py"),
    ("unregistered snapshot", {"scripts/snapshot.py": "import tempfile\np = tempfile." + maker + "()\n"}, "scripts/snapshot.py"),
    ("second ledger maker", {"test/residue.py": ledger + "\nextra = tempfile." + maker + "()\n"}, "test/residue.py"),
    ("changed ledger shape", {"test/residue.py": ledger.replace("tempfile." + maker + "(prefix=PREFIX + RUN_TAG, suffix=", "tempfile." + maker + "(prefix='anonymous', suffix=")}, "test/residue.py"),
    ("legitimate ledger", {}, None),
    ("comments and strings", {"scripts/explain.py": '# tempfile.' + maker + '()\n"""tempfile.' + maker + '()"""\n'}, None),
    ("dependency excluded", {"node_modules/tool/source.py": "p = tempfile." + maker + "()\n"}, None),
]
failed = []
for name, files, expected in cases:
    try:
        check(name, files, expected)
    except AssertionError as exc:
        failed.append(name)
        print("FAIL:", name, exc)
    else:
        print("OK:", name)
# The definition tests cannot prove the validator calls its guard. Exercise the
# public entry point on a source-only copy, once with an outside-test plant and
# once without it; no git history, dependencies or full suite are copied/run.
residue.open_case("validator entry point")
try:
    root = Path(residue.workspace("guard-entry")) / "repo"
    shutil.copytree(TEST.parent, root, ignore=shutil.ignore_patterns(
        ".git", "node_modules", "__pycache__"), symlinks=True)
    planted = root / "scripts" / "fw01_probe.py"
    planted.parent.mkdir(exist_ok=True)
    planted.write_text("import tempfile as tf\np = tf." + maker + "()\n")
    childenv = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for expected in (1, 0):
        result = subprocess.run([sys.executable, "-B", str(root / "test" / "validate.py")],
                                capture_output=True, text=True, env=childenv)
        assert result.returncode == expected, result.stdout + result.stderr
        if expected:
            assert "scripts/fw01_probe.py" in result.stdout, result.stdout
            planted.unlink()
    residue.close_case("validator entry point")
    print("OK: validator entry point rejects the plant and accepts its removal")
except AssertionError as exc:
    failed.append("validator entry point")
    print("FAIL: validator entry point", exc)
residue.report()
print(f"FW01 source guard: {len(cases) + 1 - len(failed)}/{len(cases) + 1} passed")
sys.exit(bool(failed))
