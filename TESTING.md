# Verification record

Prepared on 23 November 2026.

## Performed without model calls

- Resolved all five short revision references to full Git commits and checked out their source.
- Inspected actual skill locations, frontmatter, support directories, package metadata and root license files.
- Confirmed the style collection has 67 skill folders.
- Confirmed Taste has a skill-local Stop hook and Impeccable's shell launcher has a native-engine path and checksum manifest.
- Ran the kit's own pinned `fetch` path against all five GitHub sources. Each fetched `FETCH_HEAD` matched the full commit in the lockfile.
- Ran five offline test methods, including a complete 71-folder install, verification and uninstall in a disposable temporary target.
- Checked install preview makes no target changes, collision refusal, preservation of an unrelated existing skill, style name transformation, Taste hook removal and refusal to uninstall a modified skill.
- Ran Python syntax compilation and internal Markdown link/file checks before upload.

## Reproduce locally

```bash
python3 -m py_compile skills-kit.py test-kit.py
python3 test-kit.py
python3 skills-kit.py fetch
python3 test-kit.py --source-cache "$HOME/.cache/claude-ui-skills-kit"
```

The first test command runs small unit tests and skips the source-backed lifecycle test. Passing the cache enables the 71-folder lifecycle test. All install/remove operations inside that test use a temporary directory, not your real skill directory. Fetch still needs network access.

## Not performed

- No model-based Claude Code discovery or invocation test.
- No weekly subscription usage check or usage attribution.
- No existing-user installation, migration or live-service change for this kit.
- No execution of the upstream Taste hook/helpers, Impeccable engine or img2threejs CLI/harness.
- No new npm dependency installation or Chromium launch for this kit.
- No paid model, image, 3D or other API calls.
- No claim that every specialized source script, asset or appendix has been audited.

The optional runtime/browser commands are grounded in the pinned source layout and documented CLI behavior, but are not a fresh runtime acceptance test on your machine. If registry artifacts, host libraries or platform support differ, stop and inspect the specific error rather than changing pins blindly.
