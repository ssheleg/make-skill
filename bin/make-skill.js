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

// Exit codes are the contract: 0 installed or skipped, 1 corrupted package,
// 2 usage error, 3 refused — the plugin channel owns this agent (--force overrides).
const EXIT_PLUGIN_PRESENT = 3;

/**
 * The plugin spec (`<name>@<marketplace>`) installed for `name` in this home,
 * or null.
 *
 * `installed_plugins.json` is the record of what is actually installed. The
 * `plugins/marketplaces/<name>` directory — the only thing this installer read
 * until v0.25.0 — under-reports: a marketplace added from a local `directory`
 * source has no dir there at all, and plugin names differ from marketplace
 * names, so a check keyed on it stays green while the shadow lands. Absence
 * and corruption both read as "no plugin": the fresh HOME is the common case,
 * and an installer that crashes on a parse error refuses the machines that
 * need it most.
 */
function installedPluginSpec(home, name) {
  try {
    const raw = fs.readFileSync(
      path.join(home, '.claude', 'plugins', 'installed_plugins.json'), 'utf8');
    const parsed = JSON.parse(raw);
    const plugins =
      parsed && typeof parsed === 'object' &&
      parsed.plugins && typeof parsed.plugins === 'object'
        ? parsed.plugins
        : parsed;
    if (!plugins || typeof plugins !== 'object') return null;
    for (const spec of Object.keys(plugins)) {
      if (spec === name) return `${name}@${name}`;
      if (spec.startsWith(name + '@')) return spec;
    }
  } catch {
    // missing or corrupt = no plugin — fail open on absence, never crash
  }
  return null;
}

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

Exit codes:
  0 installed or skipped   2 usage error
  1 corrupted package      3 refused: the make-skill PLUGIN is installed in
                             this home — a plain copy would shadow it (pass
                             --force to write it anyway)

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
  // — the exact shadow this canon forbids. Refuse rather than create it, and
  // refuse LOUDLY: until v0.25.0 this check keyed on the marketplaces/ dir
  // alone and exited 0 — the fail-open class. A directory-sourced marketplace
  // has no dir there, plugin names differ from marketplace names, and a refusal
  // that exits 0 reads as success to every script above it. Reproduced live
  // 2026-08-29: a bare `npx @ssheleg/telegram-dev` shipped three shadows past
  // exactly this hole while the plugin was enabled.
  const spec = installedPluginSpec(home, 'make-skill');
  const marketplace = path.join(home, '.claude', 'plugins', 'marketplaces', 'make-skill');
  const viaMarketplaceDir = !spec && fs.existsSync(marketplace);
  if ((spec || viaMarketplaceDir) && !force) {
    const found = spec
      ? `installed as the Claude Code plugin ${spec}\n` +
        '         (declared in ~/.claude/plugins/installed_plugins.json)'
      : `registered as a Claude Code marketplace\n         (${marketplace})`;
    console.error(
      `refused: make-skill is already ${found}.\n` +
      '         A plain copy in ~/.claude/skills/make-skill would shadow the plugin\n' +
      '         and serve this frozen version forever. Update the plugin channel\n' +
      '         instead:\n' +
      '           claude plugin marketplace update make-skill\n' +
      `           claude plugin update ${spec || 'make-skill@make-skill'}\n` +
      '         Family launcher (updates every member, prunes shadow copies):\n' +
      '           npx --yes sshlg-skills@latest update\n' +
      '         Pass --force to write the plain copy anyway — a deliberate choice\n' +
      '         to run two channels, where the stale one wins.'
    );
    // Offered here too. The skill IS present on this machine — as the plugin —
    // so the routing block is exactly as wanted as on the install path. Two
    // doors into one install that behave differently is how a feature comes to
    // exist for half its users.
    offerRouters();
    return EXIT_PLUGIN_PRESENT;
  }

  installOne(
    'make-skill skill',
    skillSrc,
    path.join(home, '.claude', 'skills', 'make-skill'),
    true,
    force
  );
  offerRouters();
  // The last line says how the next version arrives — "Installed" is not a
  // complete sentence. Auto-update is off on purpose: this member composes
  // with its family, and per-marketplace autoUpdate moves each member on its
  // own clock, into combinations nobody tested together.
  console.log(
    '\nUpdates: rerun `npx @ssheleg/make-skill@latest --force`, or refresh the\n' +
    'whole family with `npx --yes sshlg-skills@latest update` (every channel,\n' +
    'and it prunes plain copies that would shadow a plugin).'
  );
  return 0;
}

process.exit(main(process.argv));
