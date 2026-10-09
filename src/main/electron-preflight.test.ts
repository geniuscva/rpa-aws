import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { resolveElectronBinary } from './electron-preflight.js';

const roots: string[] = [];
afterEach(async () => { for (const root of roots.splice(0)) await rm(root, { recursive: true, force: true }); });

async function makeNodeModules(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'agenticos-electron-'));
  roots.push(root);
  return join(root, 'node_modules');
}

describe('resolveElectronBinary', () => {
  it('returns the resolved binary path when the package and its binary are present', async () => {
    const nodeModules = await makeNodeModules();
    const packageDir = join(nodeModules, 'electron');
    const binaryRel = join('Electron.app', 'Contents', 'MacOS', 'Electron');
    await mkdir(join(packageDir, 'dist', 'Electron.app', 'Contents', 'MacOS'), { recursive: true });
    await writeFile(join(packageDir, 'cli.js'), '// stub');
    await writeFile(join(packageDir, 'path.txt'), binaryRel);
    await writeFile(join(packageDir, 'dist', binaryRel), 'stub-binary');

    const result = resolveElectronBinary(nodeModules);
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.binPath).toBe(join(packageDir, 'dist', binaryRel));
  });

  it('reports an actionable error when the electron package is absent', async () => {
    const nodeModules = await makeNodeModules();
    await mkdir(nodeModules, { recursive: true });

    const result = resolveElectronBinary(nodeModules);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.message).toContain('not installed');
      expect(result.message).toContain('pnpm install');
    }
  });

  it('reports an actionable error when cli.js is present but the binary is missing', async () => {
    const nodeModules = await makeNodeModules();
    const packageDir = join(nodeModules, 'electron');
    await mkdir(packageDir, { recursive: true });
    await writeFile(join(packageDir, 'cli.js'), '// stub');
    await writeFile(join(packageDir, 'path.txt'), join('Electron.app', 'Contents', 'MacOS', 'Electron'));

    const result = resolveElectronBinary(nodeModules);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.message).toContain('binary is missing');
      expect(result.message).toContain('pnpm install');
    }
  });
});
