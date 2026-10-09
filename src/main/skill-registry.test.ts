import { mkdtemp, mkdir, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import type { AppDatabase } from './database.js';
import { SkillRegistry } from './skill-registry.js';

const roots: string[] = [];

function memoryDatabase() {
  const skills = new Map<string, import('../shared/contracts.js').SkillSummary>();
  return {
    listSkills: () => [...skills.values()],
    getSkill: (id: string) => skills.get(id),
    upsertSkill: (skill: import('../shared/contracts.js').SkillSummary) => skills.set(skill.id, skill),
    setSkillEnabled: (id: string, enabled: boolean) => { const skill = skills.get(id); if (skill) skills.set(id, { ...skill, enabled }); },
    deleteSkill: (id: string) => { skills.delete(id); },
    markSkillUsed: (id: string) => { const skill = skills.get(id); if (skill) skills.set(id, { ...skill, usedAt: new Date().toISOString() }); },
  };
}

async function setup() {
  const root = await mkdtemp(join(tmpdir(), 'agenticos-skills-'));
  roots.push(root);
  const database = memoryDatabase();
  const registry = new SkillRegistry(join(root, 'library'), database as unknown as AppDatabase);
  await registry.initialize();
  return { root, database, registry };
}

afterEach(async () => { for (const root of roots.splice(0)) await rm(root, { recursive: true, force: true }); });

describe('SkillRegistry', () => {
  it('imports a package disabled, preserves resources and records use only after loading', async () => {
    const { root, database, registry } = await setup();
    const source = join(root, 'source');
    await mkdir(join(source, 'references'), { recursive: true });
    await writeFile(join(source, 'SKILL.md'), '---\nname: web-research\ndescription: Research with careful citations\n---\nUse primary sources.\n');
    await writeFile(join(source, 'references', 'guide.md'), 'Prefer official documentation.');

    const skill = await registry.importFolder(source);
    expect('kind' in skill).toBe(false);
    if ('kind' in skill) return;
    expect(skill.enabled).toBe(false);
    expect(registry.listEnabled()).toEqual([]);
    expect(await registry.previewInstructions(skill.id)).toContain('Use primary sources.');
    await registry.setEnabled(skill.id, true);
    expect(database.getSkill(skill.id)?.usedAt).toBeNull();
    expect(await registry.readInstructions(skill.id)).toContain('Use primary sources.');
    expect((await registry.readResource(skill.id, 'references/guide.md')).text).toContain('official documentation');
    expect(database.getSkill(skill.id)?.usedAt).not.toBeNull();
  });

  it('allows previewing disabled skills without marking them as used', async () => {
    const { root, database, registry } = await setup();
    const source = join(root, 'source');
    await mkdir(source);
    await writeFile(join(source, 'SKILL.md'), '---\nname: note-writer\ndescription: Draft clear notes\n---\nWrite concise notes.');
    const imported = await registry.importFolder(source);
    if ('kind' in imported) throw new Error('Expected a new skill.');
    expect(await registry.previewInstructions(imported.id)).toContain('Write concise notes.');
    expect(database.getSkill(imported.id)?.usedAt).toBeNull();
  });

  it('reports duplicate names without overwriting and rejects invalid frontmatter and symlinks', async () => {
    const { root, registry } = await setup();
    const first = join(root, 'first');
    const second = join(root, 'second');
    await mkdir(first); await mkdir(second);
    await writeFile(join(first, 'SKILL.md'), '---\nname: same-skill\ndescription: First package\n---\nFirst.');
    await writeFile(join(second, 'SKILL.md'), '---\nname: same-skill\ndescription: Second package\n---\nSecond.');
    const original = await registry.importFolder(first);
    if ('kind' in original) throw new Error('Expected a new skill.');
    const duplicate = await registry.importFolder(second);
    expect('kind' in duplicate && duplicate.kind).toBe('duplicate');
    await expect(registry.importFolder(join(root, 'invalid'))).rejects.toThrow();

    await writeFile(join(second, 'SKILL.md'), '---\nname: bad name\ndescription: Invalid\n---\nBody');
    await expect(registry.importFolder(second)).rejects.toThrow('lowercase letters');
    await symlink(first, join(root, 'linked-skill'));
    await expect(registry.importFolder(join(root, 'linked-skill'))).rejects.toThrow('cannot be symlinks');
  });

  it('keeps both duplicate packages under separate internal IDs', async () => {
    const { root, registry, database } = await setup();
    const first = join(root, 'first'); const second = join(root, 'second');
    await mkdir(first); await mkdir(second);
    await writeFile(join(first, 'SKILL.md'), '---\nname: same-skill\ndescription: First package\n---\nFirst.');
    await writeFile(join(second, 'SKILL.md'), '---\nname: same-skill\ndescription: Second package\n---\nSecond.');
    const original = await registry.importFolder(first);
    if ('kind' in original) throw new Error('Expected a new skill.');
    const conflict = await registry.importFolder(second);
    if (!('kind' in conflict)) throw new Error('Expected a duplicate.');
    const copied = await registry.importFolder(second, { action: 'keep-both', id: original.id });
    if ('kind' in copied) throw new Error('Expected the second package to import.');
    expect(copied.id).not.toBe(original.id);
    expect(database.listSkills()).toHaveLength(2);
    expect(await readFile(join(root, 'library', copied.id, 'SKILL.md'), 'utf8')).toContain('Second.');
  });
});
