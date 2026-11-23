# Detailed installation guide

Prepared: 23 November 2026. Target: Claude Code on Linux, macOS or WSL Linux. The commands below are instructions for you to run, not a claim that dependencies have already been installed on every machine.

## Contents

1. Scope and account choice
2. Prerequisites
3. Download and review the kit
4. Fetch exact source revisions
5. Choose installation scope
6. Preview, install and verify
7. What happens for each collection
8. Optional runtime and browser setup
9. Session discovery and example prompts
10. Manual installation mapping
11. Troubleshooting and acceptance checks

## 1. Scope and account choice

Skills are local files. A user-wide install under `~/.claude/skills` belongs to the operating-system user running the commands. It is not tied to a named Claude subscription account just because it is in that user's home directory. Another Linux user has a different home and will not automatically see those files.

Claude Code sign-in determines the account used for model work. This kit neither reads nor changes Claude credentials. It does not run `claude`, log in, switch accounts or query subscription usage. Copying skills is separate from using those skills in a model session.

Default target:

```text
~/.claude/skills/
```

Project-only alternative:

```text
/path/to/your-project/.claude/skills/
```

Choose one scope. Installing the same skills in both can create confusing duplicates or precedence behavior. This guide does not assume the behavior of a specific Claude Code release when duplicates exist.

## 2. Prerequisites

### Copy-only setup

- Git with HTTPS access to GitHub.
- Python 3.12+ recommended. Python 3.10/3.11 also work when the security-backported `tarfile` data filter is available. The tested preparation environment used Python 3.10.12 with that filter.
- A writable target and enough disk space. The fetched source snapshots total about 160 MiB at these pins, excluding transient downloads, installed copies, package caches and browsers. Leave additional space. Git clone histories can be much larger; this kit uses depth-one fetches and archives.
- Network access for `fetch`. Install and verification work locally after fetching.

Check versions without using a model:

```bash
git --version
python3 --version
python3 -c 'import tarfile; assert hasattr(tarfile, "data_filter"), "Use a Python build with tarfile data_filter support"'
```

If your system lacks the filter, update Python through a trusted package source rather than weakening archive checks. Do not run the kit as root.

### Optional runtime helpers

| Tool | Needed for |
| --- | --- |
| Node.js 22+ and npm | Common baseline for Taste helpers, Playwright CLI and optional npm launchers |
| Python 3.10+ | img2threejs helper workflows |
| Chrome, Chromium or Edge | Browser screenshots/rendering used by Taste and Impeccable |
| Playwright-managed Chromium plus Linux libraries | Playwright CLI headless testing |
| ffmpeg | Optional Taste image/video processing paths |
| A Three.js project and its own dependencies | Building and viewing img2threejs output |

Node 22+ satisfies the documented Node minimums across these pins: Taste 22+, Playwright CLI 20+, img2threejs 18+, Impeccable npm launcher 18.19+. The Impeccable shell launcher itself uses a native binary rather than Node.

Do not install all optional packages until you need them. Ubuntu/Debian package names and Chromium packaging vary by release; macOS uses different system packages. Native Windows is not the supported path for this kit's instructions, especially img2threejs. Use WSL Linux instead.

## 3. Download and review the kit

```bash
git clone https://github.com/latharrr/claude-ui-skills-kit.git
cd claude-ui-skills-kit
less README.md
less skills-kit.py
cat sources.lock.json
python3 skills-kit.py --help
```

A public clone needs no authentication. If you use a private fork or contribute, use normal authorized GitHub authentication. Do not paste a personal access token into the URL or save one in this repository.

The script uses only Python's standard library and Git. It does not need `pip install`. It does not execute commands from upstream README files, run npm lifecycle scripts, invoke a coding assistant or change shell startup files.

## 4. Fetch exact source revisions

```bash
python3 skills-kit.py fetch
```

`fetch` is a download operation, not a preview. It always writes the source cache. Default cache:

```text
~/.cache/claude-ui-skills-kit/<collection>-<full-commit>/
```

For each source it creates a temporary Git repository, fetches the full pinned commit at depth one, checks `FETCH_HEAD`, archives tracked files, rejects links/traversal/special files, and extracts a source snapshot. No upstream Git hook or installer runs. An adjacent JSON file records SHA-256 values for later local drift checks.

Git commit pinning makes the chosen source version repeatable. It does not prove the author is trustworthy, validate every dependency or provide a signed release attestation. The adjacent local hash file is an integrity record, not an independent upstream signature.

You can choose another cache location:

```bash
python3 skills-kit.py fetch --cache-dir "$HOME/ui-skill-sources"
python3 skills-kit.py install --cache-dir "$HOME/ui-skill-sources"
```

Use the same cache argument for subsequent install commands. Keep the source cache for review and reproducibility.

## 5. Choose installation scope

### User-wide, under the current operating-system user

```bash
python3 skills-kit.py install
```

This previews a user-wide install. The normal destination is `~/.claude/skills`.

### Project-only

From the kit directory, point to the actual project:

```bash
python3 skills-kit.py install --skills-dir /absolute/path/to/project/.claude/skills
```

Replace the example path first. The script refuses a target that is itself a symlink. Existing unrelated skill folders are left alone. It does not stage or commit files in your project. If project-local skills should not be committed, decide your project's ignore policy before adding them.

## 6. Preview, install and verify

The preview should report 71 folders and no collisions:

```bash
python3 skills-kit.py install
python3 skills-kit.py install --apply
python3 skills-kit.py verify
```

For project-only scope, repeat the exact `--skills-dir` argument on install, verify and uninstall.

On a collision the install stops before copying. This includes a destination that is an existing symlink. It never merges with an old skill or silently replaces it. If an earlier installation is still present, a stop is expected. Use a separate staging target, not force flags:

```bash
python3 skills-kit.py install --skills-dir "$HOME/ui-skills-review" --apply
python3 skills-kit.py verify --skills-dir "$HOME/ui-skills-review"
```

The installed state file is `.ui-skills-kit-state.json` in the target. It records hashes of installed content and the exact source versions. Preserve it. `verify` compares support files as well as `SKILL.md`; it does not run hooks, launch browsers, download native binaries or start a Claude session.

The original source frontmatter is retained except for two explicit adaptations:

1. The 67 design style names become `design-<style>` in frontmatter and folder names, such as `design-minimal`.
2. Taste's frontmatter `hooks` block is removed in the installed copy. Its helper scripts remain, but automatic registration of its skill-local Stop hook is disabled.

No user-level or project-level `settings.json` file is opened or changed. Impeccable hook manifests are not installed. The extra `KIT-PROVENANCE.json`, `UPSTREAM-LICENSE.txt` and, when present, `UPSTREAM-NOTICE.txt` identify source and rights.

## 7. What happens for each collection

### Taste Skill

Source folder: `skills/taste-skill`. Install name: `design-taste-frontend`.

Copy the whole folder, not only `SKILL.md`: its `assets`, `library`, `references` and `scripts` are used by the guidance. The source has a skill-local Stop hook. The kit disables that frontmatter block, but keeps the pristine pinned source in the cache. It does not turn every instruction in the source into a rule for your project.

Runtime helper requirements are Node 22+ and an installed Chrome, Chromium or Edge. `CHROME_PATH` is the documented override for nonstandard browser paths. ffmpeg is optional for relevant media operations. Some image/icon paths fetch online content; check rights and network access before using them.

### Awesome Design Skills

Source: `skills/<style>`, 67 folders. Each ships a `SKILL.md` and `DESIGN.md`; copy the full style folder and retain its extra files. See [STYLES.md](STYLES.md) for the complete list.

These are alternatives. Do not load all 67 as a single prompt or combine their color/font/layout mandates. Pick a style matching the current brief, then adapt it to real content and accessibility requirements. Installing 67 descriptions can still add discoverable metadata to your coding assistant; more installed skills is not guaranteed to mean lower token usage.

### Impeccable

Claude-specific source: `.claude/skills/impeccable`. Copy its `reference` and `scripts` directories too. Do not copy every provider folder, generated distribution or plugin pack.

The shell wrapper `scripts/impeccable` finds a suitable native engine or downloads the pinned engine on first use. At this commit the skill/npm metadata version is `4.10.0`, while `scripts/VERSION` names engine `0.1.27`. They are different version tracks, not an instruction to substitute one for the other.

The wrapper includes an engine-checksum manifest. Review the wrapper, checksums and release provenance before first execution. The kit does not invoke it, register its edit hooks or grant extra permissions. URL scanning needs an installed supported browser; `IMPECCABLE_BROWSER` is the documented browser-path override.

### img2threejs

This skill's base is the repository root. Its relative references point to `forge`, `scripts`, `grimoire`, `docs`, assets and other root content. The kit copies the tracked source root, without `.git`, into the skill folder. Copying only `SKILL.md` would break it.

This is a manual single-host copy, not the upstream CLI's managed symlink installation. Do not use upstream `doctor`, update or uninstall commands as proof of this kit's ownership. Use this kit's state and commands. Domain plugins and the separate `img2` harness are not included. Some upstream harness install routes alter Claude permission settings; those are deliberately not used here.

A Three.js project still needs its own dependency setup and local preview. This guide does not enable paid image/3D services, API keys, plugins or account access. Reconstruction work performed later by Claude can consume model allowance.

### Playwright CLI

Source skill: `skills/playwright-cli`. Copy its reference directory as well. The kit does **not** install the executable or browser binary just by installing the skill text. Its source `allowed-tools` field names shell commands; review local approval behavior before invocation, and do not assume this guide overrides your Claude Code security settings.

The pinned repository package version is `@playwright/cli` `0.1.25`; the package requires Node 20+ and pins its Playwright dependencies. Optional executable setup follows next.

## 8. Optional runtime and browser setup

Do this only after reviewing the downloaded code and npm dependency plan. These commands do not need a language model but do download and execute third-party package code. They are not part of the copy-only installer.

### A. Playwright CLI from the exact source checkout

Use a dedicated user-writable runtime folder. Do not reuse an existing directory. Copy the URL and full commit from the lock file if you change versions later.

```bash
mkdir -p "$HOME/.local/share"
git clone --no-checkout https://github.com/microsoft/playwright-cli.git "$HOME/.local/share/playwright-cli-pinned"
git -C "$HOME/.local/share/playwright-cli-pinned" checkout --detach c872a33cec77fa03c28fa7c6d1ad99d15d04ce42
cd "$HOME/.local/share/playwright-cli-pinned"
git rev-parse HEAD
# Review package.json and package-lock.json before executing npm lifecycle code.
npm ci
node ./playwright-cli.js --help
./node_modules/.bin/playwright install chromium
```

The expected `git rev-parse` value is the full commit above. `npm ci` uses the checked-in lockfile. It still executes permitted package lifecycle scripts; review them and dependency risks first. For an initial inspection-only download use `npm ci --ignore-scripts`, but that is not a promise that every runtime feature will work without any setup scripts. Do not replace missing exact package versions with `latest` silently.

On a minimal Linux host, missing shared libraries may require OS packages. After reviewing the changes and using an administrator account only for that OS step, Playwright's dependency helper is:

```bash
./node_modules/.bin/playwright install-deps chromium
```

It may request elevated privileges and change system packages. Do not run it on a production VPS without considering the package changes and available memory. The copy-only setup does not require it.

Use the executable by full path, or create a shell-local alias after checking it:

```bash
alias playwright-cli='node "$HOME/.local/share/playwright-cli-pinned/playwright-cli.js"'
playwright-cli --help
```

That alias lasts for the current interactive shell. Do not assume a non-interactive coding assistant inherits it. You can instead supply the full `node` command in your prompt or create a reviewed launcher in your own PATH. No shell dotfile is changed by this kit.

### B. Serve a local test page

In a separate terminal, from the directory you intentionally want to expose:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Do not serve your home directory or a directory containing secrets. Binding to loopback keeps the preview local to the host. Use an SSH tunnel for your own remote viewing rather than exposing the port publicly without review.

In the runtime terminal:

```bash
node "$HOME/.local/share/playwright-cli-pinned/playwright-cli.js" open http://127.0.0.1:8765 --browser=chromium
node "$HOME/.local/share/playwright-cli-pinned/playwright-cli.js" screenshot
node "$HOME/.local/share/playwright-cli-pinned/playwright-cli.js" close
```

If the default Chrome installation is missing, installing Chromium alone does not make a Chrome default work: pass `--browser=chromium`. Prefer localhost HTTP to `file://` for module imports and rendering. Headless is the normal server path; `--headed` needs a usable desktop/display environment.

A browser process can use much more memory than a collection of Markdown files. Run only the sessions needed, close them afterward and do not claim a fixed RAM cost from this guide.

### C. Taste / Impeccable browser paths

A browser installed by Playwright is not necessarily auto-discovered by other tools. Point each tool to the actual executable if needed:

```bash
# Replace the example paths with the actual browser executable on your machine.
export CHROME_PATH=/actual/path/to/chromium
export IMPECCABLE_BROWSER=/actual/path/to/chromium
```

Never paste a guessed path and call the installation verified. Read each tool's error and confirm the executable exists. No command in this section is evidence that it has been run on your current machine.

## 9. Session discovery and example prompts

File verification is not session proof. When you choose to resume model use, start a fresh Claude Code session under the correct operating-system user and the intended signed-in Claude account. Check the skill list or slash-command suggestions available in that release.

Examples for that later, allowance-consuming step:

```text
Use /design-minimal for this page. Preserve the existing business facts and contact details. Do not run downloads, install packages, change permissions or publish anything without asking.
```

```text
/impeccable critique the existing dashboard. Give findings first. Do not run the engine or change files yet.
```

```text
/design-taste-frontend improve this landing page within the approved brand. No invented claims, contact details, prices or hours. Keep the hook disabled.
```

```text
/img2threejs plan a procedural Three.js reconstruction of ./reference.png. Explain hidden-side uncertainty. Do not install plugins or call paid services.
```

```text
Use the playwright-cli skill to test the local app with Chromium. Ask before running package installation or accessing external accounts.
```

Not every skill needs to run on every task. Start with one primary direction, use other references only when needed, and cap repeated screenshots or revisions. No install option can guarantee a percentage reduction in weekly Claude usage.

## 10. Manual installation mapping

The scripted route is recommended because it tracks ownership and refuses collisions. For manual review, the exact mapping is:

| Source-relative path | Destination-relative folder |
| --- | --- |
| `taste: skills/taste-skill/` | `design-taste-frontend/` |
| `design: skills/<style>/` | `design-<style>/` |
| `impeccable: .claude/skills/impeccable/` | `impeccable/` |
| `img2threejs: repository root, without .git/` | `img2threejs/` |
| `playwright: skills/playwright-cli/` | `playwright-cli/` |

For parity, retain support files and licenses/notices, rename style frontmatter names as well as folders, remove only Taste's frontmatter hook block, and record every copied path. Manual copying is not tracked by `verify`/`uninstall` unless this kit created its state. Avoid `cp` over existing destinations, `ln -sfn` over unknown links, blanket `rm -rf`, and piping online installer scripts into a shell.

## 11. Troubleshooting and acceptance checks

| Symptom | Check and next step |
| --- | --- |
| Existing destination | Stop. Back it up or use a separate review target. No force/merge mode is provided. |
| Fetch cannot find commit | Check network and upstream repository accessibility. Keep the pin; do not silently use a branch head. |
| Cache hash mismatch | Preserve the changed cache for inspection. Move it aside, then fetch clean sources. Never overwrite a local edit without reviewing it. |
| Missing `tarfile` filter | Use an updated Python build with data-filter support. Do not remove traversal/link checks. |
| Permission denied | Confirm current OS user and ownership. Do not fix a home install by running everything as root. |
| Skills copied, not listed in Claude | Confirm target scope, exact `SKILL.md` filename and frontmatter, correct OS user, then a fresh session when model use is approved. |
| Duplicate names | Check project and user scope and existing plugins. Keep one intended source per invocation name. |
| Default Chrome missing | Install the intended browser and explicitly choose Chromium for Playwright. |
| Browser fails on Linux | Read missing-library errors, review system dependency installation and ensure sufficient memory. |
| Blank local Three.js rendering | Use localhost HTTP, check JS console/import paths and project dependencies, then inspect pixels. |
| Impeccable first use downloads | Expected native-engine route. Stop if offline or not approved; read existing project context without running it. |
| `verify` fails after editing skill files | Expected drift detection. Back up your edits. Do not delete the state to force removal. Follow the manual recovery section. |

Acceptance checklist:

- [ ] Exact five source commits present in cache.
- [ ] 67 style folders plus four other skill folders installed in the chosen scope.
- [ ] Existing unrelated skills retained.
- [ ] `settings.json` unchanged.
- [ ] Taste automatic Stop hook removed from the installed frontmatter.
- [ ] License and notice files retained.
- [ ] `python3 skills-kit.py verify` passes.
- [ ] Optional runtime/browser check performed only if desired, with real screenshots inspected.
- [ ] Claude session discovery checked separately only when you approve model usage.
