#!/usr/bin/env node
/*
 * Installer functional tests — both installers, against throwaway HOMEs.
 *
 * The case that earns this file its place is PLUGIN-PRESENT: an installer that
 * writes ~/.claude/skills/<name> while the same skill is installed as a Claude
 * Code plugin creates a plain copy that shadows the plugin and serves its
 * frozen version forever. Until v0.25.0 both installers keyed that check on
 * the plugins/marketplaces/<name> directory alone and exited 0 on refusal —
 * the fail-open class: a directory-sourced marketplace has no dir there,
 * plugin names differ from marketplace names, and exit 0 reads as success to
 * every script above. Every member's CI tested a fresh HOME only, so the
 * plugin-present case had never run anywhere; reproduced live 2026-08-29 with
 * a bare `npx @ssheleg/telegram-dev` shipping three shadows past it.
 *
 * House residue rule: a passing case loses its temp HOME at exit, a failing
 * case KEEPS it (a defect is debugged by reading the tree it landed in), and
 * the run ends with one line saying what it left, `nothing` included.
 */
'use strict';

const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const BIN = path.join(ROOT, 'bin', 'make-skill.js');
const SH = path.join(ROOT, 'install.sh');
const POSIX = process.platform !== 'win32';

const REFS = ['agent-skills-spec', 'authoring', 'surfaces', 'enterprise', 'retrofit',
  'host-capabilities', 'claude-code-plugin', 'distribution', 'mcp', 'a2a'];
const ASSETS = ['SKILL.template.md', 'plugin.template.json', 'marketplace.template.json',
  'hooks.template.json', 'agent.template.md', 'command.template.md'];

let failures = 0;
const homes = []; // { dir, label, failed }

function freshHome(label) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'make-skill-test-home-'));
  homes.push({ dir, label, failed: false });
  return dir;
}

function run(cmd, args, home) {
  const r = spawnSync(cmd, args, {
    cwd: home, // never the repo: npx inside the package's own repo resolves locally
    env: Object.assign({}, process.env, { HOME: home, USERPROFILE: home }),
    encoding: 'utf8',
    timeout: 120000,
  });
  return { status: r.status, out: (r.stdout || '') + (r.stderr || '') };
}

const installer = (home, ...args) => run(process.execPath, [BIN, ...args], home);
const shInstaller = (home, ...args) => run('bash', [SH, ...args], home);

function skillDir(home) {
  return path.join(home, '.claude', 'skills', 'make-skill');
}

function declarePlugin(home, spec) {
  const dir = path.join(home, '.claude', 'plugins');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'installed_plugins.json'), JSON.stringify({
    version: 2,
    plugins: { [spec]: [{ scope: 'user', installPath: '/nonexistent', version: '0.24.0' }] },
  }, null, 2));
}

function caseRun(label, fn) {
  const home = freshHome(label);
  const rec = homes[homes.length - 1];
  try {
    fn(home);
    console.log(`ok: ${label}`);
  } catch (e) {
    rec.failed = true;
    failures++;
    console.error(`FAIL: ${label}\n  ${e.message}`);
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

// ---------------------------------------------------------------- node CLI --

caseRun('fresh HOME installs the whole skill, and says how updates arrive', (home) => {
  const r = installer(home);
  assert(r.status === 0, `exit ${r.status}, expected 0\n${r.out}`);
  assert(/^Installed/m.test(r.out), `no "Installed" line:\n${r.out}`);
  assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'SKILL.md missing');
  // no ~/.claude/commands/make-skill.md: a command sharing the skill's name
  // registers /make-skill twice
  assert(!fs.existsSync(path.join(home, '.claude', 'commands', 'make-skill.md')),
    'a same-named command file was installed');
  for (const ref of REFS) {
    assert(fs.existsSync(path.join(skillDir(home), 'references', `${ref}.md`)),
      `references/${ref}.md did not travel`);
  }
  const audit = path.join(skillDir(home), 'scripts', 'audit_skill.py');
  assert(fs.existsSync(audit), 'scripts/audit_skill.py did not travel');
  if (POSIX) assert(!!(fs.statSync(audit).mode & 0o111), 'audit_skill.py not executable');
  for (const t of ASSETS) {
    assert(fs.existsSync(path.join(skillDir(home), 'assets', t)), `assets/${t} did not travel`);
  }
  // the last thing an installer states is how the next version arrives
  assert(r.out.includes('sshlg-skills@latest update'), `no update path named:\n${r.out}`);
});

caseRun('rerun skips, --force overwrites, unknown arg exits 2', (home) => {
  assert(installer(home).status === 0, 'first install failed');
  const skip = installer(home);
  assert(skip.status === 0 && /^skip:/m.test(skip.out), `rerun: ${skip.status}\n${skip.out}`);
  const forced = installer(home, '--force');
  assert(forced.status === 0 && /^Installed/m.test(forced.out),
    `--force: ${forced.status}\n${forced.out}`);
  const bad = installer(home, '--wat');
  assert(bad.status === 2, `unknown arg exit ${bad.status}, expected 2`);
});

caseRun('plugin present in installed_plugins.json: refuse, exit 3, remedy, nothing written', (home) => {
  declarePlugin(home, 'make-skill@make-skill');
  const r = installer(home);
  assert(r.status === 3, `exit ${r.status}, expected 3\n${r.out}`);
  assert(r.out.includes('refused'), `no "refused" in output:\n${r.out}`);
  assert(r.out.includes('claude plugin update make-skill@make-skill'),
    `remedy does not name the plugin spec:\n${r.out}`);
  assert(r.out.includes('--force'), `override flag not offered:\n${r.out}`);
  assert(!fs.existsSync(skillDir(home)), 'the plain copy was written despite the refusal');
});

caseRun('plugin under a differently-named marketplace: remedy names the real spec', (home) => {
  declarePlugin(home, 'make-skill@sshlg-skills');
  const r = installer(home);
  assert(r.status === 3, `exit ${r.status}, expected 3\n${r.out}`);
  assert(r.out.includes('claude plugin update make-skill@sshlg-skills'),
    `remedy does not carry the spec from the JSON:\n${r.out}`);
  assert(!fs.existsSync(skillDir(home)), 'the plain copy was written despite the refusal');
});

caseRun('--force overrides the refusal, deliberately', (home) => {
  declarePlugin(home, 'make-skill@make-skill');
  const r = installer(home, '--force');
  assert(r.status === 0, `exit ${r.status}, expected 0\n${r.out}`);
  assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'forced install wrote nothing');
});

caseRun('corrupt installed_plugins.json reads as "no plugin" — install, never crash', (home) => {
  const dir = path.join(home, '.claude', 'plugins');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'installed_plugins.json'), '{ this is not json');
  const r = installer(home);
  assert(r.status === 0, `exit ${r.status}, expected 0 (fail open)\n${r.out}`);
  assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'install did not happen');
});

caseRun('other plugins, and a prefix-collider, do not trigger a false refusal', (home) => {
  const dir = path.join(home, '.claude', 'plugins');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'installed_plugins.json'), JSON.stringify({
    version: 2,
    plugins: {
      'telegram-dev@telegram-dev': [{ scope: 'user', installPath: '/x', version: '1.0.0' }],
      'make-skill-extra@somewhere': [{ scope: 'user', installPath: '/y', version: '1.0.0' }],
    },
  }));
  const r = installer(home);
  assert(r.status === 0, `exit ${r.status}, expected 0\n${r.out}`);
  assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'install did not happen');
});

caseRun('marketplaces/<name> dir alone still refuses (fallback signal, exit 3)', (home) => {
  fs.mkdirSync(path.join(home, '.claude', 'plugins', 'marketplaces', 'make-skill'),
    { recursive: true });
  const r = installer(home);
  assert(r.status === 3, `exit ${r.status}, expected 3\n${r.out}`);
  assert(r.out.includes('claude plugin update make-skill@make-skill'),
    `no default remedy spec:\n${r.out}`);
  assert(!fs.existsSync(skillDir(home)), 'the plain copy was written despite the refusal');
});

// --------------------------------------------------------------- install.sh --

if (POSIX) {
  caseRun('install.sh: fresh install, rerun-skip', (home) => {
    const r = shInstaller(home);
    assert(r.status === 0, `exit ${r.status}, expected 0\n${r.out}`);
    assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'SKILL.md missing');
    const skip = shInstaller(home);
    assert(skip.status === 0 && /^skip:/m.test(skip.out),
      `rerun: ${skip.status}\n${skip.out}`);
  });

  caseRun('install.sh: plugin present — refuse, exit 3, nothing written; --force installs', (home) => {
    declarePlugin(home, 'make-skill@make-skill');
    const r = shInstaller(home);
    assert(r.status === 3, `exit ${r.status}, expected 3\n${r.out}`);
    assert(r.out.includes('claude plugin update make-skill@make-skill'),
      `remedy does not name the plugin spec:\n${r.out}`);
    assert(!fs.existsSync(skillDir(home)), 'the plain copy was written despite the refusal');
    const forced = shInstaller(home, '--force');
    assert(forced.status === 0, `--force exit ${forced.status}\n${forced.out}`);
    assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'forced install wrote nothing');
  });

  caseRun('install.sh: marketplaces dir alone refuses; corrupt JSON fails open', (home) => {
    fs.mkdirSync(path.join(home, '.claude', 'plugins', 'marketplaces', 'make-skill'),
      { recursive: true });
    const r = shInstaller(home);
    assert(r.status === 3, `marketplace-dir exit ${r.status}, expected 3\n${r.out}`);
    fs.rmSync(path.join(home, '.claude', 'plugins', 'marketplaces'), { recursive: true });
    fs.writeFileSync(path.join(home, '.claude', 'plugins', 'installed_plugins.json'),
      '{ this is not json');
    const ok = shInstaller(home);
    assert(ok.status === 0, `corrupt-JSON exit ${ok.status}, expected 0 (fail open)\n${ok.out}`);
    assert(fs.existsSync(path.join(skillDir(home), 'SKILL.md')), 'install did not happen');
  });
} else {
  console.log('skip: install.sh cases (POSIX only — use npx, the plugin, or the skills CLI on Windows)');
}

// ----------------------------------------------------------------- residue --

let removed = 0;
const kept = [];
for (const h of homes) {
  if (h.failed) {
    kept.push(h);
  } else {
    fs.rmSync(h.dir, { recursive: true, force: true });
    removed++;
  }
}
if (kept.length === 0) {
  console.log(`residue: this run left nothing — ${homes.length} temp home(s) created, ${removed} removed`);
} else {
  console.log(`residue: ${kept.length} of ${homes.length} temp home(s) KEPT`);
  for (const h of kept) {
    console.log(`  ${h.dir}  (case: ${h.label})  — rm -rf '${h.dir}' when done`);
  }
}

if (failures) {
  console.error(`FAIL: installer — ${failures} case(s) red`);
  process.exit(1);
}
console.log(`PASS: installer — ${homes.length} case(s)${POSIX ? '' : ' (install.sh skipped on win32)'}`);
