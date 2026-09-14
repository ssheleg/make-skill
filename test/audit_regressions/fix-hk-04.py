#!/usr/bin/env python3
"""FIX-HK-04 — the house auditor refuses a hooks.json key Claude Code does not evaluate.

The defect this closes shipped for six weeks in two family repositories at once:
`"if": "Bash(git commit *)"` written beside `"matcher"`, where Claude Code's hooks schema
has no such key. Nothing saw it — not nine member validators, not the pinned house
auditor, and not `claude plugin validate --strict`, which accepts the file. Claude Code
2.1.270 finally said so, once per session, as
`hooks.json: unknown key "if" in hooks.PreToolUse[1] ignored`.

The auditor is the one gate that covers all nine members at once, which is why the check
lives there. The key sets come from the 2.1.270 binary's schema (`Rt()` group,
`Td()` command handler), not from prose.

Standard library only.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AUDITOR = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill", "scripts",
                       "audit_skill.py")
REF = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill", "references",
                   "host-capabilities.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def _plugin(tmp, hooks):
    """A minimal plugin: one skill, and the hooks manifest under test."""
    skill = os.path.join(tmp, "plugins", "demo", "skills", "demo")
    os.makedirs(skill)
    open(os.path.join(skill, "SKILL.md"), "w", encoding="utf-8").write(
        "---\nname: demo\ndescription: \"Use when demonstrating the hooks manifest check "
        "in a fixture — triggers: 'demo hooks', 'демо хуки'. Not for real work.\"\n"
        "license: MIT\n---\n\n# Demo\n\nA fixture.\n")
    hooks_dir = os.path.join(tmp, "plugins", "demo", "hooks")
    os.makedirs(hooks_dir)
    if hooks is not None:
        json.dump(hooks, open(os.path.join(hooks_dir, "hooks.json"), "w", encoding="utf-8"))
    return skill


def _audit(skill):
    r = subprocess.run([sys.executable, AUDITOR, skill], capture_output=True, text=True,
                       timeout=300)
    return r.returncode, r.stdout + r.stderr


def _hooks(group_extra=None, handler_extra=None, handler_type="command"):
    group = {"matcher": "Bash", "hooks": [dict({
        "type": handler_type, "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/x.sh\"",
        "timeout": 20}, **(handler_extra or {}))]}
    group.update(group_extra or {})
    return {"description": "a fixture", "hooks": {"PreToolUse": [group]}}


def t_a_filter_beside_the_matcher_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, _hooks(group_extra={"if": "Bash(git commit *)"}))
        code, out = _audit(skill)
        assert code != 0, "the auditor accepted the exact shape that shipped for six weeks"
        assert "HOOKS_SCHEMA" in out, "refused, but not by this check"
        assert "sits beside `matcher`" in out, f"the message does not name the defect:\n{out}"


def t_the_same_filter_on_the_handler_passes():
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, _hooks(handler_extra={"if": "Bash(git commit *)"}))
        code, out = _audit(skill)
        assert code == 0, f"a handler-level `if` is where the schema puts it:\n{out}"
        assert "PASS HOOKS_SCHEMA" in out or "HOOKS_SCHEMA" in out


def t_an_unknown_handler_key_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, _hooks(handler_extra={"when": "always"}))
        code, out = _audit(skill)
        assert code != 0, "an invented handler key was accepted"
        assert "is not a key the command-hook schema knows" in out, out


def t_a_plugin_without_hooks_is_not_a_gap():
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, None)
        code, out = _audit(skill)
        assert code == 0, f"a plugin that ships no hooks was gapped:\n{out}"
        assert "nothing to read" in out, out


def t_an_unreadable_manifest_is_a_gap_not_a_silence():
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, _hooks())
        open(os.path.join(tmp, "plugins", "demo", "hooks", "hooks.json"), "w").write("{oops")
        code, out = _audit(skill)
        assert code != 0, "a manifest Claude Code cannot parse loads NO hooks; silence here "\
                          "would read as a plugin whose hooks work"
        assert "does not parse" in out, out


def t_a_non_command_handler_is_declared_unchecked():
    """The command handler's key set was measured; the other four were not. Saying
    nothing about them would be a verdict about something never looked at."""
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, _hooks(handler_type="prompt", handler_extra={"prompt": "hi"}))
        code, out = _audit(skill)
        assert code == 0, out
        assert "not checked" in out, f"the unchecked handler type is not disclosed:\n{out}"


def t_pycache_is_not_a_nested_bundle():
    with tempfile.TemporaryDirectory() as tmp:
        skill = _plugin(tmp, None)
        os.makedirs(os.path.join(skill, "scripts", "__pycache__"))
        open(os.path.join(skill, "scripts", "__pycache__", "x.pyc"), "wb").write(b"\x00")
        open(os.path.join(skill, "scripts", "tool.py"), "w").write("# tool\n")
        md = os.path.join(skill, "SKILL.md")
        open(md, "a", encoding="utf-8").write("\nRun [tool](scripts/tool.py).\n")
        code, out = _audit(skill)
        assert "BUNDLE_NESTED" not in out, \
            f"a byte-compile cache the tests create was reported as a shipped directory:\n{out}"


def t_the_reference_states_the_key_sets():
    t = " ".join(open(REF, encoding="utf-8").read().split())
    assert "a matcher group takes `matcher` and `hooks`" in t, \
        "host-capabilities.md does not state the group key set"
    assert "inside the handler object" in t, \
        "host-capabilities.md does not say where `if` lives"


def main():
    case("a filter beside the matcher is refused, by name", t_a_filter_beside_the_matcher_is_refused)
    case("the same filter on the handler passes", t_the_same_filter_on_the_handler_passes)
    case("an invented handler key is refused", t_an_unknown_handler_key_is_refused)
    case("a plugin that ships no hooks is not a gap", t_a_plugin_without_hooks_is_not_a_gap)
    case("a manifest that does not parse is a gap, not a silence",
         t_an_unreadable_manifest_is_a_gap_not_a_silence)
    case("a non-command handler type is declared unchecked", t_a_non_command_handler_is_declared_unchecked)
    case("__pycache__ is not reported as a nested bundle directory", t_pycache_is_not_a_nested_bundle)
    case("the reference states both key sets and where `if` lives", t_the_reference_states_the_key_sets)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
