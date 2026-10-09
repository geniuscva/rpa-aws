export type SkillSummary = {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  version: string;
  contentHash: string;
  importedAt: string;
  usedAt: string | null;
  capabilities: string[];
  hasScripts: boolean;
};

export type TaskStatus = 'queued' | 'running' | 'awaiting_approval' | 'interrupted' | 'completed' | 'failed' | 'cancelled';

export type TaskSummary = {
  id: string;
  title: string;
  status: TaskStatus;
  createdAt: string;
  skills: string[];
  skillVersions: Array<{ id: string; name: string; contentHash: string }>;
};

export type AssistantMessage = {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  text: string;
  createdAt: string;
};

export type AppStatus = {
  kiro: 'ready' | 'missing' | 'checking' | 'error';
  version?: string;
  user?: string;
  message?: string;
};

export type DashboardData = { tasks: TaskSummary[]; skills: SkillSummary[]; status: AppStatus; workspace?: string };

export type ImportSkillResult =
  | { kind: 'imported'; skill: SkillSummary }
  | { kind: 'duplicate'; existing: SkillSummary; incoming: SkillSummary; importId: string }
  | { kind: 'cancelled' };

export interface DesktopBridge {
  getDashboard(): Promise<DashboardData>;
  getSkills(): Promise<SkillSummary[]>;
  getMessages(taskId: string): Promise<AssistantMessage[]>;
  importSkill(): Promise<ImportSkillResult>;
  resolveSkillConflict(skillId: string, importId: string, action: 'replace' | 'keep-both'): Promise<SkillSummary>;
  readSkill(skillId: string): Promise<{ skill: SkillSummary; instructions: string }>;
  setSkillEnabled(skillId: string, enabled: boolean): Promise<SkillSummary>;
  removeSkill(skillId: string): Promise<void>;
  sendMessage(text: string, skillId?: string): Promise<void>;
  newConversation(): Promise<void>;
  cancelTask(taskId: string): Promise<void>;
  chooseWorkspace(): Promise<string | null>;
  revealWorkspace(): Promise<void>;
  onEvent(callback: (event: AppEvent) => void): () => void;
}

export type AppEvent =
  | { type: 'agent:message'; taskId: string; text: string; role: 'assistant' | 'tool' }
  | { type: 'task:status'; task: TaskSummary }
  | { type: 'agent:tool'; taskId: string; toolId: string; title: string; status: string }
  | { type: 'agent:permission'; taskId: string; requestId: string; title: string; description: string; options: Array<{ optionId: string; name: string; kind: string }> }
  | { type: 'app:status'; status: AppStatus }
  | { type: 'skills:changed'; skills: SkillSummary[] };

declare global {
  interface Window {
    agenticOS: DesktopBridge;
  }
}
