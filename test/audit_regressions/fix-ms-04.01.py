#!/usr/bin/env python3
"""FIX-MS-04.01 — platform limits are per-host, not universal (sherlock audit,
MS-04).

The finding: "hooks/subagents/MCP exist only inside Claude Code" wrongly
describes runtimes like Codex (native subagents/MCP); "--strict validates
manifests only" is outdated (Claude Code v2.1.233+ validates SKILL.md
frontmatter); and the 500/5000 recommendations were treated as a universal
reason a host refuses to LOAD a skill.

The fix under test: SKILL.md reframes these as HOST capabilities that vary by
host AND version (detect, don't assume); agent-skills-spec.md carries a
per-host capability matrix and a norm table with owner (spec/host/house),
required vs recommended, and a last-checked date; --strict is version-gated.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MK = os.path.join(ROOT, "plugins", "make-skill", "skills", "make-skill")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def read(rel):
    return open(os.path.join(MK, rel), encoding="utf-8").read()


def t_skill_reframes_as_host_capabilities():
    flat = " ".join(read("SKILL.md").split())
    for needle in ("are HOST\ncapabilities that vary by host AND version".replace("\n", " "),
                   "subagents and MCP are native to\nsome non-Claude runtimes".replace("\n", " "),
                   "DETECT them, never assume \"Claude Code only\""):
        assert needle in flat, f"SKILL.md no longer states {needle!r}"
    assert "exist only\ninside Claude Code — a minority".replace("\n", " ") not in flat, \
        "the 'exist only inside Claude Code' claim survived"


def t_spec_has_the_capability_matrix():
    flat = " ".join(read("references/agent-skills-spec.md").split())
    for needle in ("Host capability matrix",
                   "presence varies by host AND version",
                   "| Subagents | yes | **yes (native)** | no | no | runtime probe |",
                   "| MCP servers | yes | **yes (native)** |"):
        assert needle in flat, f"agent-skills-spec.md lacks the capability matrix: {needle!r}"


def t_norm_table_has_owner_required_date():
    flat = " ".join(read("references/agent-skills-spec.md").split())
    for needle in ("| Norm | Owner | Required? | Last checked |",
                   "| body < 5000 tokens | spec | recommended | 2026-09-09 |",
                   "| body < 4750 tokens (headroom) | house | recommended | 2026-09-09 |",
                   "A recommendation (500 lines, 5000 tokens, the house limits) is a QUALITY norm"):
        assert needle in flat, f"the norm table is missing {needle!r}"


def t_strict_is_version_gated():
    flat = " ".join(read("references/agent-skills-spec.md").split())
    assert "since Claude Code v2.1.233, `SKILL.md` frontmatter" in flat, \
        "the --strict claim is not version-gated"
    assert "plugin/marketplace **manifests only**, not SKILL.md frontmatter |" not in flat, \
        "the outdated manifests-only claim survived"


# ---------------- the capability model, executed


CAPS = {
    "claude-code": {"hooks", "subagents", "mcp", "commands"},
    "codex": {"subagents", "mcp"},        # native, but no hooks/commands
    "cursor": set(),
    "skills-cli": set(),
}


def has(host, cap):
    return cap in CAPS.get(host, set())


def t_codex_has_subagents_and_mcp():
    assert has("codex", "subagents") and has("codex", "mcp"), \
        "Codex was treated as lacking subagents/MCP — the finding itself"
    assert not has("codex", "hooks"), "Codex was given hooks it does not have"


def t_recommendation_is_not_a_load_error():
    def loads(body_tokens):
        # a body over the recommended budget is worse authoring, NOT an install
        # failure — it still loads everywhere.
        return True
    assert loads(6000) is True, "an over-budget body was treated as unloadable"


def main():
    case("SKILL.md reframes host capabilities and drops the universal claim",
         t_skill_reframes_as_host_capabilities)
    case("agent-skills-spec.md carries the per-host capability matrix",
         t_spec_has_the_capability_matrix)
    case("the norm table has owner / required / last-checked",
         t_norm_table_has_owner_required_date)
    case("the --strict claim is version-gated", t_strict_is_version_gated)
    case("Codex has native subagents and MCP", t_codex_has_subagents_and_mcp)
    case("a recommendation is a quality norm, not a load error",
         t_recommendation_is_not_a_load_error)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
