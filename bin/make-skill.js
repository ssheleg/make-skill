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
  installOne(
    'make-skill skill',
    skillSrc,
    path.join(home, '.claude', 'skills', 'make-skill'),
    true,
    force
  );
  return 0;
}

process.exit(main(process.argv));
