# Repository Guidelines

## Project Structure

- `src/main/` contains Electron main-process services and tool executors; keep filesystem, process, database, and browser access here.
- `src/renderer/` contains the React interface. Use the typed, validated bridge in `src/main/preload.cts` for renderer-to-host communication.
- `src/shared/` holds contracts shared across the process boundary.
- Tests live beside their implementation as `*.test.ts`. `research/` stores sourced architecture notes, `plan/` the product plan, and `.kiro/agents/` the Kiro custom agent configuration.
- `dist/` and `release/` are generated outputs; do not edit them by hand.

## Development and Verification

- `pnpm install` installs dependencies; `pnpm dev` starts Vite, TypeScript watch, and Electron together.
- `pnpm typecheck` runs strict TypeScript checking. `pnpm test` runs the Vitest suite; `pnpm test:watch` runs it interactively.
- `pnpm build` creates an unpacked app. `pnpm package:mac` creates a DMG and ZIP for the current Mac architecture.
- Browser tests and workflows require the pinned Playwright Chromium build; install it with `pnpm exec playwright install chromium` when absent.

## Code and Test Conventions

Use TypeScript with strict checks, ES modules, and two-space indentation. Use `camelCase` for values and functions, `PascalCase` for React components and types, and descriptive kebab-case IDs for skills. Keep IPC payloads validated and narrow; put privileged operations in main-process modules. Name tests after the behavior they protect and place them beside the module. Cover permission boundaries, invalid inputs, and failure paths when changing executors, skills, or IPC.

## Security and Local Data

Preserve renderer sandboxing, context isolation, sender validation, and filesystem confinement. Skills are untrusted instructions: importing or loading one must never grant a tool capability, and bundled scripts remain data rather than executable code. Local state belongs under `~/Library/Application Support/AgenticOS`; never commit credentials, user data, or generated packages.

## Commits and Pull Requests

This checkout has no Git history to establish a commit convention. Use concise imperative subjects (for example, `Add skill package validation`). PRs should explain behavior and security impact, link related work when available, and include UI screenshots for visible changes. Report `pnpm typecheck` and `pnpm test` results.
