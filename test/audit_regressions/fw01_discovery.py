#!/usr/bin/env python3
"""FW01 discovery admission: real permissions plus public-validator controls."""
import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
TEST = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST))
import residue

source = ast.parse((TEST / 'validate.py').read_text())
scanner = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'temp_scan_files')
skip = next(ast.literal_eval(n.value) for n in source.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'TEMP_SCAN_SKIP_DIRS' for t in n.targets))
errors = []
guard = {'os': os, 'fail': errors.append, 'TEMP_SCAN_SKIP_DIRS': skip}
exec(compile(ast.Module(body=[scanner], type_ignores=[]), 'actual-scanner', 'exec'), guard)
scan = guard['temp_scan_files']
COUNT = 0


def check(value, label):
    global COUNT
    COUNT += 1
    assert value, label


def deny(path):
    path.chmod(0)
    try:
        list(path.iterdir())
    except PermissionError:
        return
    raise AssertionError('permission plant ineffective; cannot claim this control under current privileges')


residue.open_case('source discovery admission')
root = Path(residue.workspace('discovery'))
hidden = root / 'scripts/hidden'; hidden.mkdir(parents=True)
source_file = hidden / 'plain.py'; source_file.write_text('answer = 1\n')
check(scan(root) == [str(source_file)] and not errors, 'healthy discovery sees source')
try:
    deny(hidden)
    errors.clear(); scan(root)
    check(any('scripts/hidden' in e and 'PermissionError' in e for e in errors), 'unreadable directory records discovery failure')
finally:
    hidden.chmod(0o700)
errors.clear(); check(scan(root) == [str(source_file)] and not errors, 'restored directory is readable')
excluded = root / 'node_modules'; excluded.mkdir(); (excluded / 'excluded.py').write_text('answer=1\n')
try:
    deny(excluded)
    errors.clear(); check(scan(root) == [str(source_file)] and not errors, 'declared dependency exclusion is unchanged')
finally:
    excluded.chmod(0o700)
errors.clear(); scan(root / 'missing')
check(any('FileNotFoundError' in e for e in errors), 'absent discovery root refuses')
residue.close_case('source discovery admission')

# An owned isolated source checkout, excluding Git/dependencies/cache; no full suite.
residue.open_case('whole validator discovery')
root = Path(residue.workspace('public-discovery')) / 'repo'
shutil.copytree(TEST.parent, root, ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__'), symlinks=True)
hidden = root / 'scripts/fw01_hidden'; hidden.mkdir(parents=True)
plant = hidden / 'leak.py'

def run():
    return subprocess.run([sys.executable, '-B', str(root / 'test/validate.py')], cwd=root,
                          capture_output=True, text=True, timeout=90,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))

r = run(); check(r.returncode == 0, 'healthy whole validator: ' + r.stdout + r.stderr)
plant.write_text('import tempfile\np = tempfile.' + 'mkd' + 'temp()\n')
r = run(); check(r.returncode != 0 and 'fw01_hidden/leak.py' in r.stdout + r.stderr, 'readable unauthorized maker still refused')
try:
    deny(hidden)
    r = run()
    check(r.returncode != 0 and 'fw01_hidden: temp tree scan cannot read directory (PermissionError)' in r.stdout + r.stderr,
          'actual whole validator refuses incomplete discovery with intended diagnostic')
finally:
    hidden.chmod(0o700)
plant.unlink()
r = run(); check(r.returncode == 0, 'restoration whole validator passes: ' + r.stdout + r.stderr)
residue.close_case('whole validator discovery')
residue.report()
print(f'PASS: FW01 discovery admission — {COUNT} controls')
