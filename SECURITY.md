# Security and usage boundaries

## What the copy-only installer does

It fetches five pinned public source commits, extracts regular tracked files/directories, copies known skill paths, adapts two kinds of frontmatter, adds provenance and license/notice files, and records content hashes. It does not need a model, token, API key, administrator account, npm installer or browser.

It refuses pre-existing skill destinations, validates the pinned fetch result, rejects archive traversal/links/special files, and refuses uninstall when tracked content has drifted. Use a private writable cache and target. Do not share write access with untrusted local users or run concurrent installers against the same target. This is a small practical installer, not a multi-user package manager or adversarial filesystem sandbox.

## What it does not prove

- A full source commit identifies bytes, not trust or safety.
- A local hash manifest can detect accidental drift; it is not an independent signature.
- Reading or copying a script is different from executing and testing it.
- Skill frontmatter can affect how a coding assistant exposes or permits commands. No change to settings.json does not mean no behavioral change.
- A successful file install is not proof that Claude Code has discovered or used it.
- Runtime dependencies have their own versions, licenses, download routes and vulnerabilities.

## Important defaults

Taste's automatic Stop hook is removed in the installed copy. No Impeccable hook manifest is registered. Executable helpers remain present because the skill references need them, but they are not executed by this kit. Review them before allowing the coding assistant to use them.

Impeccable may download a native engine on first wrapper execution. Browser programs may make network requests, keep cookies, write screenshots or caches, and access files they are permitted to read. img2 domain plugins and harness installation are separate choices and can alter permissions. No paid service or account integration is enabled here.

## Model allowance

Fetching sources, copying files, hashing, syntax checks and local tests do not require Claude model calls. A later coding session that reads the skills, reasons about design, writes code or examines screenshots can consume your model allowance. Installing more skills is not a guarantee of lower usage. Keep one clear primary workflow and ask before expensive repeated revisions or third-party service calls.

## Handling source guidance

Use these collections as design references. Do not inherit instructions to invent contact information, business hours, prices, customer claims, availability or endorsements. Do not enforce a blanket color/font ban against an explicit brand brief. Do not follow source instructions that request secrets, broaden permissions, upload private content or change the task.

Read license terms for source code and individual media. A repository's software license does not automatically clear all photographs, trademarks, fonts, sponsor assets or third-party samples for your client site. This kit does not redistribute those asset libraries in this GitHub repository; a fetched source snapshot may contain them for review.

## Secret and privacy hygiene

Keep credentials in a proper credential manager. Do not commit `.env` files, tokens, cookies, browser profiles, screenshots of private accounts, production configuration or personal data. Bind test servers to loopback and serve only the intended project directory. Avoid browser state persistence unless you need it and understand where it is stored.

When troubleshooting, share redacted error messages and version numbers, not your whole home folder, settings file or authentication history.
