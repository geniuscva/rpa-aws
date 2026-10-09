import Database from 'better-sqlite3';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import type { AssistantMessage, SkillSummary, TaskStatus, TaskSummary } from '../shared/contracts.js';

export class AppDatabase {
  readonly db: Database.Database;

  constructor(userData: string) {
    mkdirSync(userData, { recursive: true });
    this.db = new Database(join(userData, 'agentic-os.sqlite'));
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        role TEXT NOT NULL, text TEXT NOT NULL, created_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS skills (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 0, version TEXT NOT NULL DEFAULT 'unversioned',
        content_hash TEXT NOT NULL, imported_at TEXT NOT NULL, used_at TEXT,
        capabilities TEXT NOT NULL DEFAULT '[]', has_scripts INTEGER NOT NULL DEFAULT 0
      );
      CREATE TABLE IF NOT EXISTS task_skills (
        task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        skill_id TEXT NOT NULL, content_hash TEXT NOT NULL, name TEXT NOT NULL,
        PRIMARY KEY (task_id, skill_id, content_hash)
      );
      CREATE TABLE IF NOT EXISTS task_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        request_id TEXT NOT NULL UNIQUE, action_hash TEXT NOT NULL,
        state TEXT NOT NULL, created_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY, content TEXT NOT NULL, source TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS agent_sessions (
        task_id TEXT PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
        session_id TEXT NOT NULL
      );
      CREATE INDEX IF NOT EXISTS messages_task_created ON messages(task_id, created_at);
      CREATE INDEX IF NOT EXISTS tasks_updated ON tasks(updated_at DESC);
    `);
    const taskSkillColumns = this.db.pragma('table_info(task_skills)') as Array<{ name: string; pk: number }>;
    if (taskSkillColumns.filter((column) => column.pk > 0).length !== 3) {
      this.db.transaction(() => {
        this.db.exec(`ALTER TABLE task_skills RENAME TO task_skills_legacy;
          CREATE TABLE task_skills (
            task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            skill_id TEXT NOT NULL, content_hash TEXT NOT NULL, name TEXT NOT NULL,
            PRIMARY KEY (task_id, skill_id, content_hash)
          );
          INSERT OR IGNORE INTO task_skills(task_id,skill_id,content_hash,name)
            SELECT task_id,skill_id,content_hash,name FROM task_skills_legacy;
          DROP TABLE task_skills_legacy;`);
      })();
    }
  }

  listSkills(): SkillSummary[] {
    const rows = this.db.prepare('SELECT * FROM skills ORDER BY name COLLATE NOCASE').all() as Array<Record<string, unknown>>;
    return rows.map((row) => ({
      id: String(row.id), name: String(row.name), description: String(row.description),
      enabled: row.enabled === 1, version: String(row.version), contentHash: String(row.content_hash),
      importedAt: String(row.imported_at), usedAt: row.used_at ? String(row.used_at) : null,
      capabilities: JSON.parse(String(row.capabilities)) as string[], hasScripts: row.has_scripts === 1,
    }));
  }

  getSkill(id: string): SkillSummary | undefined { return this.listSkills().find((skill) => skill.id === id); }

  upsertSkill(skill: SkillSummary): void {
    this.db.prepare(`INSERT INTO skills (id,name,description,enabled,version,content_hash,imported_at,used_at,capabilities,has_scripts)
      VALUES (@id,@name,@description,@enabled,@version,@contentHash,@importedAt,@usedAt,@capabilities,@hasScripts)
      ON CONFLICT(id) DO UPDATE SET name=excluded.name,description=excluded.description,enabled=excluded.enabled,
      version=excluded.version,content_hash=excluded.content_hash,imported_at=excluded.imported_at,
      used_at=excluded.used_at,capabilities=excluded.capabilities,has_scripts=excluded.has_scripts`).run({
      ...skill, enabled: Number(skill.enabled), capabilities: JSON.stringify(skill.capabilities), hasScripts: Number(skill.hasScripts),
    });
  }

  setSkillEnabled(id: string, enabled: boolean): void { this.db.prepare('UPDATE skills SET enabled = ? WHERE id = ?').run(Number(enabled), id); }
  deleteSkill(id: string): void { this.db.prepare('DELETE FROM skills WHERE id = ?').run(id); }
  markSkillUsed(id: string): void { this.db.prepare('UPDATE skills SET used_at = ? WHERE id = ?').run(new Date().toISOString(), id); }
  interruptRunningTasks(): void { this.db.prepare("UPDATE tasks SET status = 'interrupted', updated_at = ? WHERE status = 'running'").run(new Date().toISOString()); }
  getSetting(key: string): string | undefined { return (this.db.prepare('SELECT value FROM app_settings WHERE key = ?').get(key) as { value: string } | undefined)?.value; }
  setSetting(key: string, value: string): void { this.db.prepare('INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value').run(key, value); }
  setAgentSession(taskId: string, sessionId: string): void { this.db.prepare('INSERT INTO agent_sessions(task_id,session_id) VALUES(?,?) ON CONFLICT(task_id) DO UPDATE SET session_id=excluded.session_id').run(taskId, sessionId); }
  getAgentSession(taskId: string): string | undefined { return (this.db.prepare('SELECT session_id FROM agent_sessions WHERE task_id=?').get(taskId) as { session_id: string } | undefined)?.session_id; }

  createTask(id: string, title: string, skill?: SkillSummary): TaskSummary {
    const now = new Date().toISOString();
    const transaction = this.db.transaction(() => {
      this.db.prepare('INSERT INTO tasks(id,title,status,created_at,updated_at) VALUES(?,?,?,?,?)').run(id, title, 'running', now, now);
      if (skill) {
        this.db.prepare('INSERT OR IGNORE INTO task_skills(task_id,skill_id,content_hash,name) VALUES(?,?,?,?)').run(id, skill.id, skill.contentHash, skill.name);
        this.db.prepare('UPDATE skills SET used_at = ? WHERE id = ?').run(now, skill.id);
      }
    });
    transaction();
    return { id, title, status: 'running', createdAt: now, skills: skill ? [skill.id] : [], skillVersions: skill ? [{ id: skill.id, name: skill.name, contentHash: skill.contentHash }] : [] };
  }

  setTaskStatus(id: string, status: TaskStatus): TaskSummary | undefined {
    const now = new Date().toISOString();
    this.db.prepare('UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?').run(status, now, id);
    return this.listTasks().find((task) => task.id === id);
  }

  addMessage(taskId: string, role: AssistantMessage['role'], text: string): AssistantMessage {
    const message = { id: crypto.randomUUID(), role, text, createdAt: new Date().toISOString() };
    this.db.prepare('INSERT INTO messages(id,task_id,role,text,created_at) VALUES(?,?,?,?,?)').run(message.id, taskId, role, text, message.createdAt);
    return message;
  }

  addTaskEvent(taskId: string, kind: string, payload: unknown): void {
    this.db.prepare('INSERT INTO task_events(task_id,kind,payload,created_at) VALUES(?,?,?,?)').run(taskId, kind, JSON.stringify(payload), new Date().toISOString());
  }

  listMessages(taskId: string): AssistantMessage[] {
    return (this.db.prepare('SELECT id,role,text,created_at as createdAt FROM messages WHERE task_id=? ORDER BY created_at').all(taskId) as AssistantMessage[]);
  }

  listTasks(): TaskSummary[] {
    return this.db.prepare(`SELECT t.id,t.title,t.status,t.created_at as createdAt,
      COALESCE(json_group_array(ts.skill_id) FILTER (WHERE ts.skill_id IS NOT NULL), '[]') as skills,
      COALESCE(json_group_array(json_object('id',ts.skill_id,'name',ts.name,'contentHash',ts.content_hash)) FILTER (WHERE ts.skill_id IS NOT NULL), '[]') as skillVersions
      FROM tasks t LEFT JOIN task_skills ts ON ts.task_id=t.id GROUP BY t.id ORDER BY t.updated_at DESC LIMIT 30`)
      .all().map((row) => {
        const item = row as Omit<TaskSummary, 'skills' | 'skillVersions'> & { skills: string; skillVersions: string };
        return { ...item, skills: JSON.parse(item.skills) as string[], skillVersions: JSON.parse(item.skillVersions) as TaskSummary['skillVersions'] };
      }) as TaskSummary[];
  }

  close(): void { this.db.close(); }
}
