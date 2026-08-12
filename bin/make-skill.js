#!/usr/bin/env node
/*
 * make-skill installer CLI.
 *
 * Installs the make-skill skill into ~/.claude/skills/make-skill, which is what
 * provides /make-skill (same layout as install.sh). No separate command file:
 * a command sharing a skill's name registers the same slash command twice.
 * Idempotent: existing installs are skipped unless --force. Zero dependencies.
 *
 * For other agents (Cursor, Codex, 70+) use: npx skills add ssheleg/make-skill
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const ROOT = path.resolve(__dirname, '..');
const REPO = 'ssheleg/make-skill';

function version() {
  try {
    return require(path.join(ROOT, 'package.json')).version;
  } catch {
    return 'unknown';
  }
}

function usage() {
  console.log(`make-skill installer v${version()}

Usage:
  npx @ssheleg/make-skill [--force]   install the make-skill skill into
                                      ~/.claude (skip existing unless --force)
  npx @ssheleg/make-skill --version
  npx @ssheleg/make-skill --help

Other install paths:
  Claude Code plugin:  /plugin marketplace add ${REPO}
                       /plugin install make-skill@make-skill
  Any agent (70+):     npx skills add ${REPO}`);
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

function installOne(label, src, dest, isDir, force) {
  if (fs.existsSync(dest) && !force) {
    console.log(`skip: ${label} already installed at ${dest} (rerun with --force to overwrite)`);
    return;
  }
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (isDir) copyDir(src, dest);
  else fs.copyFileSync(src, dest);
  console.log(`Installed ${label} -> ${dest}`);
}

/**
 * Ask the family launcher to write the routing block, for this member only.
 *
 * Delegated rather than reimplemented, for three reasons. The block describes
 * what the machine actually has, so a lone member rendering the whole thing
 * would produce a table for routers nobody installed. `--member` limits the
 * write to the `make-skill` section and leaves everyone else's alone, which is
 * what lets the bundle and a single installer both write. And the launcher is
 * the only writer that copies the operator's global instruction file before
 * touching it — that file has no version control behind it.
 *
 * `--no-install` keeps this from silently downloading a package nobody asked
 * for. When the launcher is absent, print the command rather than fail: ending
 * an install in an error because an OPTIONAL follow-up is missing reads as a
 * failed install.
 */
function offerRouters() {
  const { spawnSync } = require('child_process');
  const r = spawnSync(
    'npx',
    ['--no-install', 'sshlg-skills', 'routers', '--member', 'make-skill'],
    { stdio: 'inherit', shell: process.platform === 'win32' }
  );
  if (r.status !== 0) {
    console.log(
      '\nTo have this skill apply by default in every project, add the\n' +
      "family's routing block to your agent's global instructions:\n\n" +
      '  npx --yes sshlg-skills routers --member make-skill\n'
    );
  }
}

function main(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    usage();
    return 0;
  }
  if (args.includes('--version') || args.includes('-v')) {
    console.log(version());
    return 0;
  }
  const force = args.includes('--force');
  const unknown = args.filter((a) => a !== '--force');
  if (unknown.length) {
    console.error(`unknown argument(s): ${unknown.join(' ')}`);
    usage();
    return 2;
  }

  const skillSrc = path.join(ROOT, 'plugins/make-skill/skills/make-skill');
  if (!fs.existsSync(skillSrc)) {
    console.error(`error: skill sources missing at ${skillSrc} — corrupted package?`);
    return 1;
  }

  const home = os.homedir();

  // One channel per agent. A plain ~/.claude/skills/make-skill beside an
  // installed plugin is two listings of the same skill, and the stale copy wins
  // — the exact trap this canon documents. Refuse rather than create it.
  const marketplace = path.join(home, '.claude', 'plugins', 'marketplaces', 'make-skill');
  if (fs.existsSync(marketplace) && !force) {
    console.log(
      'skip: make-skill is already installed as a Claude Code plugin\n' +
      `       (${marketplace}).\n` +
      '       Installing a plain copy into ~/.claude/skills would shadow it, and the\n' +
      '       stale copy is the one that wins. Update the plugin instead:\n' +
      '         claude plugin marketplace update make-skill\n' +
      '         claude plugin update make-skill@make-skill\n' +
      '       Pass --force if you really want both.'
    );
    // Offered here too. The skill IS present on this machine — as the plugin —
    // so the routing block is exactly as wanted as on the install path. Two
    // doors into one install that behave differently is how a feature comes to
    // exist for half its users.
    offerRouters();
    return 0;
  }

  installOne(
    'make-skill skill',
    skillSrc,
    path.join(home, '.claude', 'skills', 'make-skill'),
    true,
    force
  );
  offerRouters();
  return 0;
}

process.exit(main(process.argv));
