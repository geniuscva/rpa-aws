import { mkdtemp, mkdir, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { FileExecutor } from './file-executor.js';

const roots: string[] = [];
afterEach(async () => { for (const root of roots.splice(0)) await rm(root, { recursive: true, force: true }); });

describe('FileExecutor', () => {
  it('searches granted files, reads UTF-8 text and creates new Markdown without overwriting', async () => {
    const root = await mkdtemp(join(tmpdir(), 'agenticos-files-'));
    roots.push(root);
    const workspace = join(root, 'workspace');
    await mkdir(workspace);
    await writeFile(join(workspace, 'notes.txt'), 'Xin chào, Jarvis');
    const files = new FileExecutor();
    files.setWorkspace(workspace);
    expect(await files.search('notes')).toEqual([{ path: 'notes.txt', name: 'notes.txt', type: 'file' }]);
    expect(await files.readText('notes.txt')).toBe('Xin chào, Jarvis');
    const created = await files.createMarkdown('research/result.md', '# Kết quả\n');
    expect(await readFile(created.path, 'utf8')).toBe('# Kết quả\n');
    await expect(files.createMarkdown('research/result.md', 'replace')).rejects.toThrow('never overwrites');
    await expect(files.resolvePath('../outside.txt')).rejects.toThrow('outside');
  });

  it('blocks symlinks that escape the selected workspace', async () => {
    const root = await mkdtemp(join(tmpdir(), 'agenticos-files-'));
    roots.push(root);
    const workspace = join(root, 'workspace');
    await mkdir(workspace);
    await writeFile(join(root, 'private.txt'), 'private');
    await symlink(join(root, 'private.txt'), join(workspace, 'shortcut.txt'));
    const files = new FileExecutor();
    files.setWorkspace(workspace);
    await expect(files.readText('shortcut.txt')).rejects.toThrow('outside');
    expect(await files.search('shortcut')).toEqual([]);
  });
});
