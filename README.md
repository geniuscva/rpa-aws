# Agentic OS

Agentic OS is a macOS desktop workspace for assigning personal tasks to Kiro CLI. Its first workflows are public-web research, searching a user-selected folder, and creating new UTF-8 Markdown files. A separate Playwright Chromium profile is used for browser tasks. The app also maintains its own local Agent Skills library; it does not scan Kiro, Codex, or `.agents` skill folders.

## Run locally

Requirements: Apple Silicon macOS, Node.js, pnpm, and Kiro CLI. Sign in to Kiro once with `kiro-cli login`; the app reuses the CLI's existing account and does not store a separate model API key. The app uses `kiro-cli acp --agent-engine=v2` and checks the installed executable when it starts a chat.

```sh
pnpm install
pnpm dev
```

Select a workspace folder in the app before asking Jarvis to search files or create documents. Browser research opens a separate visible Chromium window. Its profile is isolated from the default browser and persists under the app's local data directory.

## Skills

Import a folder containing `SKILL.md` from the Agent Skills page. A skill must have YAML frontmatter with `name` and `description`; new imports start disabled. Review the preview, enable the skill, then choose it from the Skills page or type `/skill-name` in chat. Instructions are loaded for the task, and references are read only when requested. Bundled scripts are preserved for inspection but are never executed.

## Build and verify

```sh
pnpm typecheck
pnpm test
pnpm build
```

`pnpm build` creates an unpacked macOS app in `release/`. `pnpm package:mac` creates a DMG and ZIP for the current Mac architecture. The first browser task also requires the Playwright Chromium build for this pinned Playwright version; install it with `pnpm exec playwright install chromium` if it is missing.

Task state, skill packages, and settings are stored in `~/Library/Application Support/AgenticOS`. Browser data and local artifacts stay on the Mac. Prompts and any selected context are sent to Kiro's cloud service. Do not import secrets into a skill package or ask the agent to handle credentials.

## References

- [Kiro ACP](https://kiro.dev/docs/acp/) — agent and client lifecycle, session updates, cancellation, and permissions.
- [Kiro CLI ACP](https://kiro.dev/docs/cli/acp/) — launch Kiro as an ACP JSON-RPC process.
- [Kiro Agent Skills](https://kiro.dev/docs/skills/) — skill package format and progressive loading.
- [Electron security](https://www.electronjs.org/docs/latest/tutorial/security/) — renderer isolation, IPC validation, CSP, and navigation controls.
- [Playwright BrowserContext](https://playwright.dev/docs/browser-contexts) — isolated browser state.

The architecture notes and source review are in [research/agentic-os-sources.md](research/agentic-os-sources.md); the agreed scope is in [plan/PLAN.md](plan/PLAN.md).
