#!/usr/bin/env python3
"""What did this run leave on disk? — one ledger, and it prints even when the answer is nothing.

A run produces more than a diff. `test/checker_parity_test.py` copied this whole
repository into `$TMPDIR` to plant a defect into the copy, and `test/plant_guard_test.py`
built a small tree per case; neither removed anything, and — the part that matters —
nothing said so. Measured with

    find "$TMPDIR" -maxdepth 4 -type f -path '*/copy/sub/b.sh' | wc -l
    find "$TMPDIR" -maxdepth 3 -type f -path '*/planted/SKILL.md' | wc -l
    find "$TMPDIR" -maxdepth 2 -type d -name repo | while read -r d; \
        do [ -d "$d/plugins/make-skill" ] && echo x; done | wc -l

**These are samples, and they carry their date.** On **2026-08-19**, before the fix: 1760
plant-guard trees, 60 planted skill dirs, 36 repository copytrees — 1856 directories, 47.3
MB, accumulated silently over ~220 gate runs. Re-run on **2026-08-20**: 2592 / 60 / 36 =
2688 directories, 83.6 MB.

**The two halves of that pile behave differently, and only one of them is this
repository's.** Split by the fix's own commit time, `-newermt "$(git log -1 --format=%cI
16a9682)"` — 2026-08-19T13:55:15+02:00: **0** planted dirs and **0** repository copytrees
were created after it, both frozen at 60 and 36, while **784** plant-guard trees were, from
the three siblings shipping the identical fixture. Running the whole gate on 2026-08-20
moved all three counts by exactly **0**. Quote the split, not the total: a total restated as
a current state is the defect this module exists to report on.

A `TemporaryDirectory` around each one closes the leak. It does not close the defect,
because the defect is that a completed run said nothing about what it left, so the next
leak is invisible in exactly the same way. So every temp tree in this suite is taken
through `workspace()`, and every run ends with one line naming its residue — `nothing`
included. That line is the check: the next leak shows up in the gate's own output rather
than in somebody's `du`.

**A failing case keeps its tree, deliberately.** A plant is debugged by reading the copy
it landed in, and a cleanup that runs only on the pass path deletes the evidence exactly
when it is wanted. So a case that fails — or raises anything at all, including an error
that is not an assertion — keeps its workspace; the report names the path, names the case
that owns it, and prints the `rm -rf` that ends it. A clean case's tree goes at exit.

The prefix is part of the mechanism: `make-skill-test-…` makes any future residue
attributable to this suite by name. The directories counted above are plain `tmpXXXXXXXX`
and indistinguishable from every other program's — which is why they have to be reported
and left alone rather than swept.

**What this ledger does NOT see.** It accounts for trees `workspace()` handed out. A bare
`tempfile.mkdtemp()` anywhere in this suite is invisible to it, and the report then prints
*left nothing* over a live leak — watched happening in `agent-stack`, which ported this
module and closed the hole with a source check over its own `test/*.py`. There is no such
check here: board row **MS-05**.

    import residue
    residue.open_case(name)
    d = residue.workspace("planted")      # removed iff the owning case passed
    residue.close_case(name)              # only on success — see above
    residue.report()                      # also wired to atexit, so it cannot be skipped

Zero dependencies, standard library only, like everything else here.
"""
# shared-mechanism: residue.py — 5 copies in this family, kept as one file
#   rather than 5 dialects. The umbrella's gate computes which module-level
#   constants actually differ between the copies and refuses a difference this line
#   does not name: on 2026-08-24 an undeclared success-vocabulary constant made a
#   ported runner report twenty healthy guards as broken, and nothing could see it.
# diverges: PREFIX
import atexit
import os
import shutil
import sys
import tempfile

PREFIX = "make-skill-test-"

# What makes residue attributable to ONE run rather than to a prefix every run shares.
# `$TMPDIR` belongs to the whole machine, so a scan by PREFIX alone reports two things that
# are not this run's leak: another session's trees, and a tree a FAILING case in an earlier
# run kept ON PURPOSE as its evidence. Both turned a green suite red here — 37,301 entries
# under the shared $TMPDIR from a concurrent session on 2026-08-24, and every later run of
# the gate after any kept tree. The process group is inherited by every suite `npm test`
# chains in one shell, and differs between two gate runs, which is exactly the line the scan
# needs. `getpgrp` is POSIX; the pid fallback is per-process rather than per-run and is only
# there so this module imports anywhere.
RUN_TAG = "%d-" % (os.getpgrp() if hasattr(os, "getpgrp") else os.getpid())


def strays_for_run(names, mine):
    """Split what a shared TMPDIR holds into (this run's leaks, everybody else's).

    Pure, so the split is a fixture rather than a scenario needing two sessions and a clock.
    `mine` is the set of basenames this run created and still accounts for.
    """
    ours, foreign = [], []
    for n in names:
        if not n.startswith(PREFIX):
            continue
        if n.startswith(PREFIX + RUN_TAG):
            if n not in mine:
                ours.append(n)
        else:
            foreign.append(n)
    return sorted(ours), sorted(foreign)

_created = []        # [(path, owner)] every workspace this run made, in order
_incomplete = set()  # cases that did not finish clean; their workspaces are kept
_owner = None
_reported = False


def open_case(name):
    """Everything created from here on belongs to `name` until it closes."""
    global _owner
    _owner = name
    _incomplete.add(name)


def close_case(name, ok=True):
    """Call with ok=True only when the case passed — a kept tree is the evidence."""
    global _owner
    if ok:
        _incomplete.discard(name)
    _owner = None


def workspace(tag="tree"):
    """A temp directory this run owns and will account for at exit."""
    path = tempfile.mkdtemp(prefix=PREFIX + RUN_TAG, suffix="-" + tag)
    _created.append((path, _owner))
    return path


def _keep(owner):
    # An unowned workspace — created outside any case — is kept only when the run as a
    # whole is red, because nobody can say which case would want to read it.
    return bool(_incomplete) if owner is None else owner in _incomplete


def report(stream=None):
    """Remove what may go, keep what a failure may need, and say which — on every path.

    Returns (kept, removed) so a fixture can assert on the decision rather than on the
    wording. Idempotent: registered with `atexit` and safe to call by hand as well.
    """
    global _reported
    if _reported:
        return [], []
    _reported = True
    stream = stream or sys.stdout
    kept, removed = [], []
    for path, owner in _created:
        if _keep(owner):
            kept.append((path, owner))
            continue
        shutil.rmtree(path, ignore_errors=True)
        if os.path.exists(path):
            # Honest degradation: a tree that refused to go is residue, not a pass.
            kept.append((path, owner))
        else:
            removed.append(path)
    total = len(_created)
    if not kept:
        print("residue: this run left nothing — %d temp tree(s) created, %d removed"
              % (total, len(removed)), file=stream)
    else:
        print("residue: %d of %d temp tree(s) KEPT — the case did not pass and the copy "
              "is the evidence:" % (len(kept), total), file=stream)
        for path, owner in kept:
            print("    %s  <- %s" % (path, owner or "no case"), file=stream)
        print("  %d removed. When you are done reading them: rm -rf %s"
              % (len(removed), " ".join(p for p, _ in kept)), file=stream)
    stream.flush()
    return kept, removed


atexit.register(report)
