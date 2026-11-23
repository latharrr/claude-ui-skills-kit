# Updates, migration and rollback

## Do not use blanket update commands

This kit is a manual-copy installation with its own state file. Do not mix it with upstream CLI-owned installations in the same target folders. Commands that use `latest`, plugin installers, `npx skills add`, `impeccable update`, or img2 managed-link updates can bypass the lockfile and ownership record.

## Stage an update

1. Keep the current kit revision and `sources.lock.json` in Git history.
2. Verify the current install and preserve any intentional local changes.
3. Review the new upstream revision, licenses, executable files, hooks, npm dependencies and source layout.
4. Update the full commit in `sources.lock.json` on a local branch. Short hashes and moving branch names are not sufficient pins.
5. Fetch into a new cache or let the full-commit folder name create a separate snapshot.
6. Test in a separate destination. Never point a test at your real home skills directory.

```bash
python3 skills-kit.py fetch --cache-dir "$HOME/ui-skills-next-cache"
python3 skills-kit.py install --cache-dir "$HOME/ui-skills-next-cache" --skills-dir "$HOME/ui-skills-next-review"
python3 skills-kit.py install --cache-dir "$HOME/ui-skills-next-cache" --skills-dir "$HOME/ui-skills-next-review" --apply
python3 skills-kit.py verify --skills-dir "$HOME/ui-skills-next-review"
python3 test-kit.py --source-cache "$HOME/ui-skills-next-cache"
```

The script assumes these pinned layouts and 67 style folders. A changed count/layout/frontmatter may require a reviewed code change before an update is safe. In particular, Taste hook removal assumes `hooks` is its final frontmatter property at the current pin. Review the transform against new source versions.

## Replace a kit-managed installation

After successful staging:

1. Back up the existing skills directory, its state file and the current lockfile using your normal backup method.
2. Run `verify` against the current target with the current kit.
3. Preview uninstall, then apply. It removes only tracked unmodified folders.
4. Install the staged new kit version, then verify it.
5. Keep the old kit revision, pins and cache until you have accepted the new session behavior.

No in-place force overwrite is provided. Do not run Claude with these skills while replacing them. If a later install fails, your backup and old cache remain the recovery route.

## Uninstall

```bash
python3 skills-kit.py verify
python3 skills-kit.py uninstall
python3 skills-kit.py uninstall --apply
```

For a custom target, pass the same `--skills-dir` every time. Preview does not delete anything. Apply checks all tracked folders before deleting any. If even one folder has changed or is missing, removal stops so you can inspect it. It does not remove the source cache, CLI runtimes, browser binaries, project output or unrelated skills.

The source cache is optional to retain. Only remove its dedicated directory after you have confirmed it contains no work you need. Browser and npm runtime cleanup is separate because those programs may be shared by other projects.

## Roll back

For an unmodified kit-managed install, uninstall the new version, restore the old kit revision and lockfile from Git, fetch its pins if necessary, install again and verify. Alternatively restore the complete target backup, including `.ui-skills-kit-state.json`, while no coding session is using it.

Do not restore only the state file over a different set of skill files. Hashes describe the exact installed bytes.

## Migrate an earlier manual installation

If a prior setup already has these skills, the kit will refuse those colliding folders. That is intentional.

Safest path:

1. Install the kit into a separate review directory.
2. Compare the old folders and names with the staged set. Check hook differences, supporting files and local edits.
3. Back up the old specific skill folders and settings file. Do not move unrelated skills.
4. With coding sessions closed, move only the reviewed old destinations into a dated backup outside the target.
5. Install the kit into the now-vacant target and verify.
6. Retain the backup until session discovery and actual work have been accepted.

This guide does not silently perform that migration. If the old installation used different frontmatter names, check prompts or automation relying on them before switching to `design-<style>`.

## Modified files or damaged state

Do not delete the state file to bypass a warning. Copy the affected folder and manifest to a backup, inspect the diff and decide what to keep. If you must remove a modified folder manually, operate on its exact reviewed path only. Never use a wildcard over the whole skills directory.

The state file is a local ownership record, not a tamper-proof security boundary. Do not accept a replacement state file from an unknown source.
