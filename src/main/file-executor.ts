import { mkdir, readFile, readdir, realpath, stat, writeFile } from 'node:fs/promises';
import { basename, extname, isAbsolute, join, relative, resolve, sep } from 'node:path';

const READABLE = new Set(['.md', '.txt', '.pdf', '.csv', '.json', '.html', '.htm', '.log']);

function isWithin(root: string, target: string): boolean {
  const rel = relative(root, target);
  return rel === '' || (!isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`));
}

export class FileExecutor {
  private workspace?: string;
  setWorkspace(workspace: string | undefined): void { this.workspace = workspace; }
  getWorkspace(): string | undefined { return this.workspace; }

  async resolvePath(path: string): Promise<string> {
    if (!this.workspace) throw new Error('Choose a workspace folder in Settings before accessing local files.');
    const root = await realpath(this.workspace);
    const candidate = resolve(root, path);
    if (!isWithin(root, candidate)) throw new Error('Path is outside the granted workspace.');
    let actual: string;
    try { actual = await realpath(candidate); }
    catch {
      let parentCandidate = resolve(candidate, '..');
      let parent: string;
      while (true) {
        try { parent = await realpath(parentCandidate); break; }
        catch {
          const next = resolve(parentCandidate, '..');
          if (next === parentCandidate || !isWithin(root, next)) throw new Error('Parent folder is not available inside the granted workspace.');
          parentCandidate = next;
        }
      }
      if (!isWithin(root, parent)) throw new Error('Path is outside the granted workspace.');
      return candidate;
    }
    if (!isWithin(root, actual)) throw new Error('A symbolic link points outside the granted workspace.');
    return actual;
  }

  async search(query: string, limit = 30): Promise<Array<{ path: string; name: string; type: 'file' | 'folder' }>> {
    if (!this.workspace) throw new Error('Choose a workspace folder in Settings before accessing local files.');
    if (!query.trim() || query.length > 200) throw new Error('Search text must be between 1 and 200 characters.');
    const root = await realpath(this.workspace);
    const results: Array<{ path: string; name: string; type: 'file' | 'folder' }> = [];
    const queue = [root];
    const needle = query.toLocaleLowerCase();
    let visited = 0;
    while (queue.length && results.length < Math.min(Math.max(limit, 1), 50) && visited < 12_000) {
      const directory = queue.shift()!;
      const entries = await readdir(directory, { withFileTypes: true }).catch(() => []);
      for (const entry of entries) {
        if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'Library') continue;
        const path = join(directory, entry.name);
        const relativePath = relative(root, path);
        visited += 1;
        if (entry.isSymbolicLink()) continue;
        if (entry.name.toLocaleLowerCase().includes(needle)) results.push({ path: relativePath, name: entry.name, type: entry.isDirectory() ? 'folder' : 'file' });
        if (entry.isDirectory() && results.length < limit) queue.push(path);
        if (results.length >= limit || visited >= 12_000) break;
      }
    }
    return results;
  }

  async readText(path: string): Promise<string> {
    const target = await this.resolvePath(path);
    if (!READABLE.has(extname(target).toLowerCase())) throw new Error('Only text-based files can be read in this version.');
    const info = await stat(target);
    if (!info.isFile() || info.size > 2 * 1024 * 1024) throw new Error('File must be a regular file smaller than 2 MB.');
    return await readFile(target, 'utf8');
  }

  async createMarkdown(path: string, content: string): Promise<{ path: string; name: string }> {
    const target = await this.resolvePath(path);
    if (extname(target).toLowerCase() !== '.md' || basename(target).startsWith('.')) throw new Error('Create a visible Markdown file ending in .md.');
    if (content.length > 500_000) throw new Error('The document exceeds the 500 KB limit.');
    await mkdir(resolve(target, '..'), { recursive: true });
    const parent = await realpath(resolve(target, '..'));
    if (!this.workspace || !isWithin(await realpath(this.workspace), parent)) throw new Error('Parent folder is outside the granted workspace.');
    try { await writeFile(target, content, { encoding: 'utf8', flag: 'wx', mode: 0o600 }); }
    catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'EEXIST') throw new Error('That file already exists; choose a new name. This version never overwrites.');
      throw error;
    }
    return { path: target, name: basename(target) };
  }
}
