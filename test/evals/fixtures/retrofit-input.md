<!--
EVALUATION FIXTURE — the input for scenario s02 (Retrofit audit).
This is the CONTENT a broken skills/invoices/SKILL.md would have. It is stored
under a different filename on purpose: the skills CLI discovers every SKILL.md
in a repo tree and would install this one as a real skill.

Nine planted defects, one per scored line in s02: reserved word in `name`;
`name` != directory; description not third person / no "Use when" / no Russian;
angle brackets in the description; a frontmatter key outside the spec; a
reference pointer with no load condition; a link escaping the skill directory;
a Windows-style path; a time-branching sentence. A correct audit finds all nine
with file:line evidence before proposing a fix.
-->

---
name: claude-invoice-helper
description: I can help you extract totals from <invoice> PDFs and post them to the ledger.
author: acme-team
---

# Invoice helper

## What this does

This skill helps you process invoices. Before October, use the v1 parser; after
that, use the v2 parser.

See references/ for more details.

Run scripts\parse.py to extract the totals.

The shared field contract lives in [../shared/contract.md](../shared/contract.md).
