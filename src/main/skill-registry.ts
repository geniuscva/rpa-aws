import { copyFile, lstat, mkdir, readdir, readFile, realpath, rename, rm, stat } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { basename, dirname, extname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { parse } from 'yaml';
import type { SkillSummary } from '../shared/contracts.js';
import { AppDatabase } from './database.js';

const MAX_SKILL_BYTES = 20 * 1024 * 1024;
const SUPPORTED_TEXT = new Set(['.md', '.txt', '.json', '.csv', '.yaml', '.yml']);
const SAFE_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function contained(root: string, target: string): boolean {
  const rel = relative(root, target);
  return rel === '' || (!isAbsolute(rel) && !rel.startsWith(`..${sep}`) && rel !== '..');
}

function toId(name: string): string { return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'skill'; }

export class SkillRegistry {
  constructor(private readonly root: string, private readonly database: AppDatabase) {}

  async initialize(): Promise<void> {
    await mkdir(this.root, { recursive: true });
    for (const name of await readdir(this.root)) {
      const path = join(this.root, name);
      if (name.startsWith('.import-')) await rm(path, { recursive: true, force: true });
      else if (name.startsWith('.backup-')) {
        const destination = join(this.root, name.slice('.backup-'.length));
        try { await stat(destination); await rm(path, { recursive: true, force: true }); }
        catch { await rename(path, destination).catch(() => undefined); }
      }
    }
  }

  async inspect(sourcePath: string): Promise<SkillSummary> {
    const skillFile = await this.findSkillFile(sourcePath);
    const parsed = await this.parseSkill(skillFile);
    return this.summarize(parsed, 'preview', false);
  }

  listEnabled(): Array<Pick<SkillSummary, 'id' | 'name' | 'description'>> {
    return this.database.listSkills().filter((skill) => skill.enabled).map(({ id, name, description }) => ({ id, name, description }));
  }

  async importFolder(sourcePath: string, conflict?: { action: 'replace' | 'keep-both'; id: string }): Promise<SkillSummary | { kind: 'duplicate'; existing: SkillSummary; incoming: SkillSummary }> {
    const skillFile = await this.findSkillFile(sourcePath);
    const sourceRoot = dirname(skillFile);
    const parsed = await this.parseSkill(skillFile);
    const existing = this.database.listSkills().find((skill) => skill.name.toLowerCase() === parsed.name.toLowerCase());

    if (existing && !conflict) return { kind: 'duplicate', existing, incoming: this.summarize(parsed, 'preview', false) };
    if (existing && conflict?.action === 'replace' && conflict.id !== existing.id) throw new Error('Skills conflict changed; refresh the library and try again.');

    const id = existing && conflict?.action === 'replace' ? existing.id : `${toId(parsed.name)}-${randomUUID().slice(0, 6)}`;
    const destination = join(this.root, id);
    const temporary = join(this.root, `.import-${randomUUID()}`);
    const backup = join(this.root, `.backup-${id}`);
    let oldPackageMoved = false;
    let newPackageInstalled = false;

    try {
      await this.copySafeTree(sourceRoot, temporary);
      const finalSkillFile = await this.findSkillFile(temporary);
      const finalParsed = await this.parseSkill(finalSkillFile);
      const summary = this.summarize(finalParsed, id, false);
      if (existing && conflict?.action === 'replace') { await rename(destination, backup); oldPackageMoved = true; }
      await rename(temporary, destination);
      newPackageInstalled = true;
      this.database.upsertSkill(summary);
      if (oldPackageMoved) await rm(backup, { recursive: true, force: true });
      return summary;
    } catch (error) {
      await rm(temporary, { recursive: true, force: true });
      if (newPackageInstalled) await rm(destination, { recursive: true, force: true });
      if (oldPackageMoved) {
        await rename(backup, destination).catch(() => undefined);
      }
      throw error;
    }
  }

  async setEnabled(id: string, enabled: boolean): Promise<SkillSummary> {
    const skill = this.database.getSkill(id);
    if (!skill) throw new Error('Skill not found.');
    if (enabled) await this.previewInstructions(id);
    this.database.setSkillEnabled(id, enabled);
    return this.database.getSkill(id)!;
  }

  async remove(id: string): Promise<void> {
    if (!this.database.getSkill(id)) throw new Error('Skill not found.');
    await rm(join(this.root, id), { recursive: true, force: true });
    this.database.deleteSkill(id);
  }

  async readInstructions(id: string): Promise<string> {
    this.requireSkill(id);
    const content = await this.instructionsFor(id);
    this.database.markSkillUsed(id);
    return content;
  }

  async previewInstructions(id: string): Promise<string> {
    const skill = this.database.getSkill(id);
    if (!skill) throw new Error('Skill not found.');
    return this.instructionsFor(id, skill.name);
  }

  private async instructionsFor(id: string, name = this.requireSkill(id).name): Promise<string> {
    const path = await this.skillFileFor(id);
    const content = await readFile(path, 'utf8');
    const delimiter = content.indexOf('---', 3);
    if (!content.startsWith('---') || delimiter < 0) throw new Error(`Skill “${name}” has invalid frontmatter.`);
    return content.slice(delimiter + 3).trim();
  }

  async readResource(id: string, relativePath: string): Promise<{ name: string; mimeType: string; text: string }> {
    const skill = this.requireSkill(id);
    const base = await realpath(join(this.root, id));
    const candidate = resolve(base, relativePath);
    if (!contained(base, candidate)) throw new Error('Resource path escapes the skill package.');
    const actual = await realpath(candidate);
    if (!contained(base, actual)) throw new Error('Resource symlink escapes the skill package.');
    const info = await stat(actual);
    if (!info.isFile() || info.size > MAX_SKILL_BYTES) throw new Error('Resource must be a small, regular file.');
    const ext = extname(actual).toLowerCase();
    if (!SUPPORTED_TEXT.has(ext)) throw new Error('Only text references and assets can be loaded in this version.');
    this.database.markSkillUsed(id);
    return { name: `${skill.name}/${relative(base, actual)}`, mimeType: ext === '.md' ? 'text/markdown' : 'text/plain', text: await readFile(actual, 'utf8') };
  }

  resolveName(name: string): SkillSummary | undefined {
    return this.database.listSkills().find((skill) => skill.enabled && skill.name.toLowerCase() === name.toLowerCase());
  }

  private requireSkill(id: string): SkillSummary {
    const skill = this.database.getSkill(id);
    if (!skill || !skill.enabled) throw new Error('Skill is missing or disabled.');
    return skill;
  }

  private async skillFileFor(id: string): Promise<string> {
    const root = await realpath(join(this.root, id));
    const result = join(root, 'SKILL.md');
    const actual = await realpath(result);
    if (!contained(root, actual)) throw new Error('SKILL.md escapes its package.');
    return actual;
  }

  private async findSkillFile(sourcePath: string): Promise<string> {
    const root = await realpath(sourcePath);
    const info = await lstat(sourcePath);
    if (info.isSymbolicLink()) throw new Error('Skill folders cannot be symlinks.');
    const candidate = info.isDirectory() ? join(root, 'SKILL.md') : root;
    if (basename(candidate) !== 'SKILL.md') throw new Error('Choose a skill folder containing SKILL.md.');
    const skill = await realpath(candidate);
    if (!contained(root, skill)) throw new Error('SKILL.md escapes the selected folder.');
    if (!(await stat(skill)).isFile()) throw new Error('SKILL.md must be a regular file.');
    return skill;
  }

  private async parseSkill(path: string): Promise<{ name: string; description: string; version: string; contentHash: string; hasScripts: boolean }> {
    const content = await readFile(path, 'utf8');
    const match = content.match(/^---\s*\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
    if (!match) throw new Error('SKILL.md must start with YAML frontmatter.');
    let metadata: unknown;
    try { metadata = parse(match[1]); } catch (error) { throw new Error(`Invalid skill YAML: ${error instanceof Error ? error.message : 'parse error'}`); }
    if (!metadata || typeof metadata !== 'object') throw new Error('Skill frontmatter must be a YAML mapping.');
    const fields = metadata as Record<string, unknown>;
    const name = typeof fields.name === 'string' ? fields.name.trim() : '';
    const description = typeof fields.description === 'string' ? fields.description.trim() : '';
    if (!SAFE_NAME.test(name) || name.length > 64) throw new Error('Skill name must use lowercase letters, numbers, and hyphens (max 64 characters).');
    if (!description || description.length > 1024) throw new Error('Skill description is required and must be 1024 characters or fewer.');
    const packageRoot = dirname(path);
    const entries = await this.collectFiles(packageRoot);
    const hasScripts = entries.some((item) => item.startsWith('scripts/'));
    const digest = createHash('sha256');
    let totalBytes = 0;
    for (const file of entries.sort()) {
      const bytes = await readFile(join(packageRoot, file));
      totalBytes += bytes.byteLength;
      if (totalBytes > MAX_SKILL_BYTES) throw new Error('Skill package exceeds the 20 MB size limit.');
      digest.update(file).update('\0').update(bytes).update('\0');
    }
    return { name, description, version: typeof fields.metadata === 'object' && fields.metadata && 'version' in fields.metadata ? String((fields.metadata as Record<string, unknown>).version) : 'unversioned', contentHash: digest.digest('hex'), hasScripts };
  }

  private async collectFiles(root: string, relativePath = ''): Promise<string[]> {
    const dir = relativePath ? join(root, relativePath) : root;
    const entries = await readdir(dir, { withFileTypes: true });
    const files: string[] = [];
    for (const entry of entries) {
      if (entry.name === '.DS_Store') continue;
      const child = relativePath ? join(relativePath, entry.name) : entry.name;
      const full = join(root, child);
      const info = await lstat(full);
      if (info.isSymbolicLink()) throw new Error('Skill packages cannot contain symbolic links.');
      if (info.isDirectory()) files.push(...await this.collectFiles(root, child));
      else if (info.isFile()) files.push(child);
      else throw new Error('Skill packages may only contain regular files and folders.');
      if (files.length > 1000) throw new Error('Skill package contains too many files.');
    }
    return files;
  }

  private async copySafeTree(source: string, destination: string): Promise<void> {
    const root = await realpath(source);
    await mkdir(destination, { recursive: true });
    for (const entry of await readdir(root, { withFileTypes: true })) {
      if (entry.name === '.DS_Store') continue;
      const from = join(root, entry.name);
      const to = join(destination, entry.name);
      const info = await lstat(from);
      if (info.isSymbolicLink()) throw new Error('Skill packages cannot contain symbolic links.');
      if (info.isDirectory()) await this.copySafeTree(from, to);
      else if (info.isFile()) await copyFile(from, to);
      else throw new Error('Skill packages may only contain regular files and folders.');
    }
  }

  private summarize(parsed: { name: string; description: string; version: string; contentHash: string; hasScripts: boolean }, id: string, enabled: boolean): SkillSummary {
    return { id, name: parsed.name, description: parsed.description, enabled, version: parsed.version,
      contentHash: parsed.contentHash, importedAt: new Date().toISOString(), usedAt: null,
      capabilities: [], hasScripts: parsed.hasScripts };
  }
}
