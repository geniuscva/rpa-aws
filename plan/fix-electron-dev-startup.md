# Bugfix Plan — Fix Electron dev launch failure when the Electron binary is missing

Status: Implemented and verified (2026-10-09)

## Problem Statement

`pnpm dev` fails with a raw, confusing error when the Electron binary isn't
present in `node_modules` (postinstall download skipped or failed). The
`dev` script also bypasses the intended launcher `scripts/dev-electron.ts`, so
the environment variables `main.ts` depends on (`NODE_ENV=development`,
`AGENTICOS_DEV_SERVER`) are never set — meaning dev startup is broken on two
fronts that resolve together. Scope: the dev launch path only. No
production/build changes.

## Requirements

- **R1**: When the Electron binary is missing, dev startup prints a clear,
  actionable diagnostic (how to fix) and exits non-zero instead of surfacing a
  raw resolution/spawn error.
- **R2**: The `dev` npm script routes Electron startup through
  `scripts/dev-electron.ts` so `NODE_ENV` and `AGENTICOS_DEV_SERVER` are set,
  matching what `main.ts` reads.
- **R3**: The binary-presence check is covered by a targeted Vitest regression
  (present → ok; missing → actionable error), per the bugfix scope's regression
  requirement.
- **R4**: Vite and the TypeScript watch continue running under `concurrently`
  even when the Electron preflight fails, so the rest of the dev loop stays up.
- **R5**: Existing test suite stays green; `pnpm typecheck` passes.

## Background (findings)

- `package.json` `dev` previously ended with `wait-on ... && electron .` — a
  direct launch that bypassed `scripts/dev-electron.ts`.
- `scripts/dev-electron.ts` spawns `node_modules/.bin/electron` and sets
  `NODE_ENV=development` + `AGENTICOS_DEV_SERVER=http://127.0.0.1:5173`.
- `src/main/main.ts`: `isDevelopment = process.env.NODE_ENV === 'development'`;
  in dev it calls `mainWindow.loadURL(process.env.AGENTICOS_DEV_SERVER!)`. Both
  only come from `dev-electron.ts`.
- The `.bin/electron` shim defers to `node_modules/electron/cli.js`, which
  resolves the real binary via `electron/path.txt` → `dist/`. In this checkout
  `node_modules/electron/path.txt` is absent, so the binary genuinely is
  missing — the live repro.
- `tsconfig.main.json` includes `src/main/**` + `src/shared/**` and excludes
  `*.test.ts`; `scripts/` is covered by the base `tsconfig.json` and run via
  `tsx` (devDependency). Vitest runs beside-module `*.test.ts` (see
  `src/main/*.test.ts`, e.g. the `file-executor.test.ts` fixture/cleanup pattern
  with `mkdtemp`/`rm`).

## Solution

Add a small, testable preflight helper under `src/main/` that resolves and
verifies the Electron binary, returning either the resolved path or a structured
"missing" result with an actionable message. Have `scripts/dev-electron.ts`
call it before spawning: on missing, print the message and exit non-zero; on ok,
spawn as today. Rewire the `dev` script to invoke `dev-electron.ts` (via `tsx`)
instead of `electron .`. Cover the helper with a Vitest regression.

Dataflow:

```
pnpm dev
  └─ concurrently -k
       ├─ vite --host 127.0.0.1
       ├─ tsc -p tsconfig.main.json --watch
       └─ wait-on http://127.0.0.1:5173 dist/main/main.js
            └─ tsx scripts/dev-electron.ts
                 └─ resolveElectronBinary()
                      ├─ missing → console.error(message); process.exit(1)
                      └─ present → spawn .bin/electron
                                   (NODE_ENV=development,
                                    AGENTICOS_DEV_SERVER=http://127.0.0.1:5173)
```

## Task Breakdown

- [x] **Task 1 — Testable preflight helper.** `src/main/electron-preflight.ts`
  exports `resolveElectronBinary(nodeModulesDir?)` returning
  `{ ok: true, binPath }` or `{ ok: false, message }`. Mirrors how the
  `electron` package resolves its binary (`cli.js` → `path.txt` → `dist/<rel>`)
  and detects every missing-state. Dependency-free (`node:fs`, `node:path`), no
  spawning; accepts the `node_modules` root so tests can point at fixtures.
- [x] **Task 2 — Regression test.** `src/main/electron-preflight.test.ts`
  (Vitest, beside-module). Cases: (a) binary present → `ok`; (b) `electron/`
  package absent → actionable error; (c) `cli.js` present but binary missing →
  actionable error. Uses the `mkdtemp`/`rm` fixture pattern; asserts on message
  substrings, not exact copy.
- [x] **Task 3 — Wire preflight into the launcher.** `scripts/dev-electron.ts`
  runs the preflight first; on `ok: false` prints the message and exits 1,
  otherwise spawns as before (preserves `stdio: 'inherit'`, `NODE_ENV`,
  `AGENTICOS_DEV_SERVER`, SIGINT/SIGTERM forwarding, and child-exit
  propagation).
- [x] **Task 4 — Rewire the `dev` script.** `package.json` `dev` Electron leg
  changed from `electron .` to `tsx scripts/dev-electron.ts`, keeping the
  `concurrently -k` structure and the `wait-on` guard.

## Verification

- `pnpm typecheck` — clean (exit 0).
- `pnpm test` — 4 files / 11 tests pass, including the new 3-case
  `electron-preflight` suite.
- `tsx scripts/dev-electron.ts` standalone — prints the diagnostic, exits 1.
- `pnpm dev` live — Vite and tsc watch start; the Electron leg prints the
  actionable message and exits non-zero instead of a raw crash.

### Notes / limitations

- With `concurrently -k`, a preflight exit tears down the sibling legs
  (Vite, tsc). This is the pre-existing `-k` contract, unchanged by the fix;
  the fix makes the failure legible rather than altering teardown semantics.
  Keeping Vite/tsc up after a preflight failure would mean dropping `-k` — a
  behavior change beyond this bugfix's scope.
- A real end-to-end window launch requires the Electron binary actually present
  (a networked `pnpm install`), which isn't reproducible in this missing-binary
  checkout — called out rather than asserted.

## Files changed

- `src/main/electron-preflight.ts` (new)
- `src/main/electron-preflight.test.ts` (new)
- `scripts/dev-electron.ts` (modified)
- `package.json` (modified — `dev` script only)
