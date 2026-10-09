import { readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';

export type ElectronPreflightResult =
  | { ok: true; binPath: string }
  | { ok: false; message: string };

function exists(path: string): boolean {
  try {
    statSync(path);
    return true;
  } catch {
    return false;
  }
}

/**
 * Resolve the Electron binary the same way the `electron` package does: the
 * package exposes `cli.js`, and `path.txt` records the platform binary's path
 * relative to the package root (populated by Electron's postinstall download).
 *
 * Returns the resolved binary path when everything is present, or an actionable
 * message naming the missing piece and how to fix it. Does not spawn anything.
 */
export function resolveElectronBinary(nodeModulesDir: string = resolve(process.cwd(), 'node_modules')): ElectronPreflightResult {
  const packageDir = resolve(nodeModulesDir, 'electron');
  const cliPath = resolve(packageDir, 'cli.js');
  const fix = 'Run `pnpm install` to materialize it, or `node node_modules/electron/install.js` to re-download the binary.';

  if (!exists(cliPath)) {
    return {
      ok: false,
      message: `Electron is not installed: ${cliPath} is missing. ${fix}`,
    };
  }

  const pathTxt = resolve(packageDir, 'path.txt');
  if (!exists(pathTxt)) {
    return {
      ok: false,
      message: `Electron binary metadata is missing: ${pathTxt} not found — the postinstall download did not complete. ${fix}`,
    };
  }

  const relativeBinary = readFileSync(pathTxt, 'utf8').trim();
  if (!relativeBinary) {
    return {
      ok: false,
      message: `Electron binary metadata is empty: ${pathTxt} records no path — the postinstall download did not complete. ${fix}`,
    };
  }

  const binPath = resolve(packageDir, 'dist', relativeBinary);
  if (!exists(binPath)) {
    return {
      ok: false,
      message: `Electron binary is missing: ${binPath} not found — the postinstall download did not complete. ${fix}`,
    };
  }

  return { ok: true, binPath };
}
