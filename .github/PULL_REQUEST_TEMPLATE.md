## What and why

<!-- What changes, and what problem it solves. Link the issue if there is one. -->

## Evidence

<!-- Paste what you ran and what it printed. Both are required for any change. -->

```
python3 test/validate.py
bash -n install.sh
claude plugin validate ./plugins/make-skill --strict   # if you have the CLI
claude plugin validate . --strict
```

## Checklist

- [ ] Every check above passes locally
- [ ] Behavior change is reflected in `README.md` and in the skill's own docs
- [ ] `CHANGELOG.md` has an entry for this change
- [ ] If versions moved: `marketplace.json`, `plugin.json`, `package.json` and the top `CHANGELOG.md` entry all agree
- [ ] No relative links added to `cursor/rules/*.mdc` (those files get copied standalone)
- [ ] New validator rule? It comes with a negative self-test in `.github/workflows/validate.yml`
- [ ] Touched the `description` or a reference file? Re-ran `test/evals/` and said what changed
