#!/usr/bin/env python3
"""Fixtures for plugins/make-skill/hooks/skill-md-audit.sh, through the real script.

Hub B-211: Codex sends every edit as `apply_patch`, the patch text in
`tool_input.command`, with no `file_path`. The hook matched `Write|Edit|MultiEdit` and
pulled `file_path` out with `sed`, so a SKILL.md written by Codex was never audited.
The apply_patch cases below fail on 0.33.3's hook; the Claude-shaped cases are the ones
CI's "Hook is silent unless a SKILL.md was written" step has always run.

Run by `npm test`. Standard library only, like everything else here.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLUGIN = os.path.join(ROOT, "plugins", "make-skill")
HOOK = os.path.join(PLUGIN, "hooks", "skill-md-audit.sh")
CLEAN = os.path.join(PLUGIN, "skills", "make-skill", "SKILL.md")
FIXTURE = os.path.join(HERE, "evals", "fixtures", "retrofit-input.md")

sys.path.insert(0, HERE)
import residue  # noqa: E402

failures = []


def run(payload, env_extra=None, hook=HOOK):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=PLUGIN)
    env.update(env_extra or {})
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(["bash", hook], input=data, capture_output=True, text=True,
                          env=env, timeout=60)


def patch(*lines, key="command", cwd=None):
    body = "\n".join(["*** Begin Patch", *lines, "*** End Patch"]) + "\n"
    p = {"tool_name": "apply_patch", "tool_input": {key: body}}
    if cwd is not None:
        p["cwd"] = cwd
    return p


def advises(r, *needles):
    assert r.returncode == 0, f"exit {r.returncode} (PostToolUse must never block): {r.stderr[:200]}"
    assert r.stdout.strip(), "silent where a broken SKILL.md was written"
    msg = json.loads(r.stdout)["systemMessage"]
    for n in needles:
        assert n in msg, f"advice does not name {n!r}: {msg[:300]!r}"
    return msg


def silent(r):
    assert r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}"
    assert r.stdout.strip() == "", f"spoke where it should not: {r.stdout[:300]!r}"


def case(name, fn):
    residue.open_case(name)
    try:
        fn()
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")
    except Exception as e:  # noqa: BLE001 - a crash in a case is a failure, not a pass
        failures.append(f"{name}: {type(e).__name__}: {e}")
        print(f"FAIL  {name}: {type(e).__name__}: {e}")
    else:
        print(f"ok    {name}")
        residue.close_case(name)


def main(hook=HOOK):
    box = residue.workspace("skill-md-hook")
    broken_dir = os.path.join(box, "invoices")
    os.makedirs(broken_dir)
    src = open(FIXTURE, encoding="utf-8").read()
    with open(os.path.join(broken_dir, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(re.sub(r"^<!--.*?-->\s*", "", src, count=1, flags=re.S))
    broken = os.path.join(broken_dir, "SKILL.md")
    other_dir = os.path.join(box, "other")
    os.makedirs(other_dir)
    shutil.copy(broken, os.path.join(other_dir, "SKILL.md"))
    h = lambda p, **k: run(p, hook=hook, **k)  # noqa: E731

    # Claude Code shapes: unchanged.
    case("Write of a non-SKILL.md is silent",
         lambda: silent(h({"tool_name": "Write", "tool_input": {"file_path": os.path.join(box, "notes.md")}})))
    case("Write of a broken SKILL.md advises",
         lambda: advises(h({"tool_name": "Write", "tool_input": {"file_path": broken}})))
    case("Edit of a clean SKILL.md is silent",
         lambda: silent(h({"tool_name": "Edit", "tool_input": {"file_path": CLEAN}})))
    case("Write whose content mentions SKILL.md, of another file, is silent",
         lambda: silent(h({"tool_name": "Write", "tool_input": {
             "file_path": os.path.join(box, "notes.md"), "content": "see invoices/SKILL.md"}})))

    # Codex apply_patch.
    case("apply_patch updating a broken SKILL.md advises",
         lambda: advises(h(patch(f"*** Update File: {broken}", "@@", "-a", "+b"))))
    case("apply_patch adding a broken SKILL.md relative to the payload cwd advises",
         lambda: advises(h(patch("*** Add File: invoices/SKILL.md", "+x", cwd=box))))
    case("apply_patch with the patch in tool_input.input advises",
         lambda: advises(h(patch(f"*** Update File: {broken}", "@@", key="input"))))
    case("apply_patch moving a file onto a broken SKILL.md advises",
         lambda: advises(h(patch(f"*** Update File: {box}/draft.md", f"*** Move to: {broken}"))))
    case("apply_patch touching two broken skills names both in one message",
         lambda: advises(h(patch(f"*** Update File: {broken}", "@@",
                                 f"*** Update File: {other_dir}/SKILL.md", "@@")),
                         "invoices", "other"))
    case("apply_patch updating a clean SKILL.md is silent",
         lambda: silent(h(patch(f"*** Update File: {CLEAN}", "@@", "-a", "+b"))))
    case("apply_patch touching only unrelated files is silent",
         lambda: silent(h(patch(f"*** Add File: {box}/notes.md", "+see SKILL.md"))))
    case("apply_patch deleting a SKILL.md is silent (nothing left to audit)",
         lambda: silent(h(patch(f"*** Delete File: {box}/gone/SKILL.md"))))

    # Malformed payloads: hooks fail silent.
    case("malformed JSON naming SKILL.md is silent",
         lambda: silent(h('{"tool_name":"apply_patch","tool_input":{"command":"*** Update File: SKILL.md')))
    case("apply_patch with a non-string command is silent",
         lambda: silent(h('{"tool_name":"apply_patch","tool_input":{"command":42},"x":"SKILL.md"}')))
    case("apply_patch with no tool_input is silent",
         lambda: silent(h('{"tool_name":"apply_patch","x":"SKILL.md"}')))
    case("a JSON array naming SKILL.md is silent", lambda: silent(h('["SKILL.md"]')))

    # No python3 on PATH: silent, as the contract says.
    bash, cat = shutil.which("bash"), shutil.which("cat")
    shim = os.path.join(box, "bin")
    os.makedirs(shim)
    for tool in (bash, cat):
        os.symlink(tool, os.path.join(shim, os.path.basename(tool)))
    case("no python3 on PATH is silent",
         lambda: silent(subprocess.run([bash, hook], input=json.dumps(patch(f"*** Update File: {broken}")),
                                       capture_output=True, text=True, timeout=60,
                                       env=dict(os.environ, CLAUDE_PLUGIN_ROOT=PLUGIN, PATH=shim))))

    residue.report()                      # also wired to atexit; removes the tree on a green run
    if failures:
        print(f"\nFAIL: {len(failures)} hook case(s)")
        return 1
    print("\nPASS: skill-md-audit.sh hook cases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else HOOK))
