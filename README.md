# Claude UI skills kit

A pinned, copy-only setup for five UI/design resource collections in Claude Code. Includes a detailed Markdown guide, a non-destructive installer, local verification, an uninstall path, source attribution and an index of all 67 design styles.

**Start with [INSTALLATION.md](INSTALLATION.md).** Review the code before running it. Nothing in this repository needs Claude model calls to download, install or verify the files.

## What is included

| Collection | Installed folder | Purpose |
| --- | --- | --- |
| Taste Skill | `design-taste-frontend` | Frontend design guidance and rendering helpers |
| Awesome Design Skills | `design-<style>` x 67 | Separate style choices, not one combined design recipe |
| Impeccable | `impeccable` | Design planning, critique, audit and refinement references |
| img2threejs | `img2threejs` | Reference-image to procedural Three.js workflow |
| Playwright CLI skill | `playwright-cli` | Browser testing instructions and command reference |

**71 skill folders total:** 67 styles plus four other skills. Five collections does not mean five folders.

The repository stores the kit, not copies of upstream repositories or their image libraries. `sources.lock.json` pins all five upstream commits. `fetch` retrieves those exact snapshots. Licenses and notices accompany installed copies.

## Quick start

Use Linux, macOS or a Linux environment in WSL. Python 3.10+ with the backported `tarfile` data filter, plus Git, are needed for the copy-only setup. Python 3.12+ is the simplest baseline. Runtime helpers need more dependencies, described in the guide.

```bash
git clone https://github.com/latharrr/claude-ui-skills-kit.git
cd claude-ui-skills-kit
python3 skills-kit.py --help
python3 skills-kit.py fetch
python3 skills-kit.py install
# The previous command is a preview and refuses existing destinations.
python3 skills-kit.py install --apply
python3 skills-kit.py verify
```

This repository is intended for public reference. No credentials are needed to clone a public copy. If you contribute through Git, use your normal credential manager or SSH setup, never put tokens in a command, URL, issue or committed file.

Already have these skills? Do not force an install. Existing destinations cause an early stop. See [UPDATING.md](UPDATING.md) for staging, migration and rollback.

## Safety choices

- No `sudo`, global npm install, upstream installer, model invocation or settings edit in the kit's installer.
- The install previews by default. Existing target folders and links are never overwritten.
- Every style gets a `design-` folder **and frontmatter name** prefix to reduce collisions.
- Taste's skill-local `Stop` hook block is removed from the installed `SKILL.md`. Its source stays unchanged in the cache. This prevents automatic hook registration through that file, but it does not remove its helper programs or the instructions that may ask a coding assistant to run them.
- No Impeccable hook manifest is registered. Its launcher remains an optional executable with a first-use native download. Review it before use.
- No img2 plugin harness, additional permissions, paid service or browser installation is enabled automatically.
- Source text is guidance, not permission. Your brief, real project facts, security requirements and approvals still win.

## Read next

- [INSTALLATION.md](INSTALLATION.md): complete installation, dependencies, manual layouts, browser setup and troubleshooting.
- [STYLES.md](STYLES.md): all 67 style names and invocation names.
- [UPDATING.md](UPDATING.md): update, migrate, uninstall and recover.
- [SECURITY.md](SECURITY.md): downloaded code, privacy, dependencies and model-usage boundaries.
- [SOURCES.md](SOURCES.md): exact commits, inspected files and license details.
- [TESTING.md](TESTING.md): tests performed and limits of verification.

## Status

Prepared on 23 November 2026. Pinned fetch and 71-folder install/verify/uninstall were tested in disposable local directories, including collision refusal and modified-file protection. No existing Claude installation or live service was changed to prepare this kit. No Claude or other paid model calls were made. Actual discovery and use inside a fresh Claude Code session remain unverified and are a separate opt-in step.
