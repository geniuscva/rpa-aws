import { app, BrowserWindow, dialog, globalShortcut, ipcMain, Menu, nativeImage, protocol, shell, Tray } from 'electron';
import { access, copyFile, mkdir, readFile, realpath } from 'node:fs/promises';
import { constants } from 'node:fs';
import { extname, join, relative, resolve, sep } from 'node:path';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';
import type { AppEvent, AppStatus, ImportSkillResult } from '../shared/contracts.js';
import { AppDatabase } from './database.js';
import { BrowserExecutor } from './browser-executor.js';
import { FileExecutor } from './file-executor.js';
import { KiroBackend } from './kiro-backend.js';
import { McpGateway } from './mcp-gateway.js';
import { SkillRegistry } from './skill-registry.js';

const isDevelopment = process.env.NODE_ENV === 'development';
protocol.registerSchemesAsPrivileged([{ scheme: 'agenticos', privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true } }]);
let mainWindow: BrowserWindow | undefined;
let tray: Tray | undefined;
let database: AppDatabase;
let skills: SkillRegistry;
let files: FileExecutor;
let browser: BrowserExecutor;
let backend: KiroBackend;
let gateway: McpGateway;
let status: AppStatus = { kiro: 'checking', message: 'Checking Kiro CLI…' };
let appData = '';
const pendingSkillImports = new Map<string, string>();

function broadcast(event: AppEvent): void {
  if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send('app:event', event);
}

async function runVersionCheck(): Promise<void> {
  try {
    status = await backend.status();
    broadcast({ type: 'app:status', status });
  } catch (error) {
    status = { kiro: 'error', message: error instanceof Error ? error.message : 'Kiro CLI unavailable.' };
  }
}

function validSender(event: Electron.IpcMainInvokeEvent): boolean {
  if (!mainWindow || event.sender !== mainWindow.webContents || !event.senderFrame || event.senderFrame.parent !== null) return false;
  const url = event.senderFrame.url;
  if (isDevelopment) {
    try { return new URL(url).origin === 'http://127.0.0.1:5173'; } catch { return false; }
  }
  return url === 'agenticos://app/index.html';
}

function handle<T extends z.ZodType, R>(channel: string, schema: T, action: (input: z.output<T>) => R | Promise<R>): void {
  ipcMain.handle(channel, async (event, raw: unknown) => {
    if (!validSender(event)) throw new Error('IPC request rejected.');
    const input = schema.parse(raw ?? {});
    return await action(input);
  });
}

function registerIpc(): void {
  const empty = z.object({}).strict();
  handle('dashboard:get', empty, async () => ({ tasks: database.listTasks(), skills: database.listSkills(), status: await backend.status(), workspace: files.getWorkspace() }));
  handle('skills:list', empty, () => database.listSkills());
  handle('chat:messages', z.object({ taskId: z.string().uuid() }), ({ taskId }) => database.listMessages(taskId));
  handle('skills:read', z.object({ skillId: z.string().min(1).max(100) }), async ({ skillId }) => ({ skill: database.getSkill(skillId), instructions: await skills.previewInstructions(skillId) }));
  handle('skills:import', empty, async (): Promise<ImportSkillResult> => {
    const choice = await dialog.showOpenDialog(mainWindow!, { title: 'Import an Agent Skill', properties: ['openDirectory'], buttonLabel: 'Select Skill Folder' });
    if (choice.canceled || !choice.filePaths[0]) return { kind: 'cancelled' };
    const result = await skills.importFolder(choice.filePaths[0]);
    if ('kind' in result) {
      const importId = randomUUID();
      pendingSkillImports.set(importId, choice.filePaths[0]);
      return { ...result, importId };
    }
    broadcast({ type: 'skills:changed', skills: database.listSkills() });
    return { kind: 'imported', skill: result };
  });
  handle('skills:resolve-conflict', z.object({ skillId: z.string().min(1).max(100), importId: z.string().uuid(), action: z.enum(['replace', 'keep-both']) }), async ({ skillId, importId, action }) => {
    const sourcePath = pendingSkillImports.get(importId);
    if (!sourcePath) throw new Error('Skill import request expired; import the package again.');
    pendingSkillImports.delete(importId);
    const result = await skills.importFolder(sourcePath, { id: skillId, action });
    if ('kind' in result) throw new Error('Skill conflict changed; refresh the library.');
    broadcast({ type: 'skills:changed', skills: database.listSkills() });
    return result;
  });
  handle('skills:enabled', z.object({ skillId: z.string().min(1).max(100), enabled: z.boolean() }), async ({ skillId, enabled }) => {
    const skill = await skills.setEnabled(skillId, enabled);
    broadcast({ type: 'skills:changed', skills: database.listSkills() });
    return skill;
  });
  handle('skills:remove', z.object({ skillId: z.string().min(1).max(100) }), async ({ skillId }) => {
    await skills.remove(skillId);
    broadcast({ type: 'skills:changed', skills: database.listSkills() });
  });
  handle('chat:send', z.object({ text: z.string().min(1).max(12_000), skillId: z.string().max(100).optional() }), async ({ text, skillId }) => backend.send(text, skillId));
  handle('chat:new', empty, async () => backend.newConversation());
  handle('task:cancel', z.object({ taskId: z.string().uuid() }), async ({ taskId }) => backend.cancel(taskId));
  handle('workspace:choose', empty, async () => {
    const chosen = await dialog.showOpenDialog(mainWindow!, { title: 'Choose a workspace folder', properties: ['openDirectory', 'createDirectory'], buttonLabel: 'Use This Workspace' });
    if (chosen.canceled || !chosen.filePaths[0]) return null;
    const canonical = await realpath(chosen.filePaths[0]);
    database.setSetting('workspace', canonical);
    files.setWorkspace(canonical);
    return canonical;
  });
  handle('system:open-workspace', empty, async () => {
    const folder = files.getWorkspace();
    if (!folder) throw new Error('Choose a workspace first.');
    const error = await shell.openPath(folder);
    if (error) throw new Error(error);
  });
  handle('system:reveal-workspace', empty, async () => {
    const folder = files.getWorkspace();
    if (!folder) throw new Error('Choose a workspace first.');
    shell.showItemInFolder(folder);
  });
}

async function createWindow(): Promise<void> {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 980,
    minHeight: 680,
    title: 'Agentic OS',
    backgroundColor: '#111210',
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 18, y: 16 },
    webPreferences: {
      preload: join(app.getAppPath(), 'dist/main/preload.cjs'),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
      webSecurity: true,
      allowRunningInsecureContent: false,
    },
  });
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.webContents.on('will-navigate', (event, url) => {
    const allowed = isDevelopment ? (() => { try { return new URL(url).origin === 'http://127.0.0.1:5173'; } catch { return false; } })() : (() => { try { const parsed = new URL(url); return parsed.origin === 'agenticos://app' && parsed.pathname === '/index.html'; } catch { return false; } })();
    if (!allowed) event.preventDefault();
  });
  mainWindow.on('closed', () => { mainWindow = undefined; });
  if (isDevelopment) await mainWindow.loadURL(process.env.AGENTICOS_DEV_SERVER!);
  else await mainWindow.loadURL('agenticos://app/index.html');
}

function registerAppProtocol(): void {
  const rendererRoot = resolve(app.getAppPath(), 'dist/renderer');
  const mimeTypes: Record<string, string> = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
  protocol.handle('agenticos', async (request) => {
    try {
      const url = new URL(request.url);
      if (url.host !== 'app' || request.method !== 'GET') return new Response('Not found', { status: 404 });
      const path = resolve(rendererRoot, `.${decodeURIComponent(url.pathname)}`);
      const rel = relative(rendererRoot, path);
      if (rel === '..' || rel.startsWith(`..${sep}`) || rel.startsWith('/')) return new Response('Not found', { status: 404 });
      const content = await readFile(path);
      return new Response(content, { headers: { 'content-type': mimeTypes[extname(path).toLowerCase()] ?? 'application/octet-stream', 'x-content-type-options': 'nosniff' } });
    } catch { return new Response('Not found', { status: 404 }); }
  });
}

function setupMenu(): void {
  const menu = Menu.buildFromTemplate([
    { label: 'Agentic OS', submenu: [{ label: 'About Agentic OS', role: 'about' }, { type: 'separator' }, { label: 'Quit Agentic OS', accelerator: 'Cmd+Q', click: () => app.quit() }] },
    { label: 'Edit', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' }] },
    { label: 'View', submenu: isDevelopment ? [{ role: 'reload' }, { role: 'toggleDevTools' }, { type: 'separator' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }] : [{ role: 'reload' }] },
  ]);
  Menu.setApplicationMenu(menu);
}

function setupTray(): void {
  const image = nativeImage.createFromBuffer(Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j0h8AAAAASUVORK5CYII=', 'base64')).resize({ width: 16, height: 16 });
  tray = new Tray(image);
  tray.setToolTip('Agentic OS');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Open Agentic OS', click: () => { if (mainWindow) mainWindow.show(); else void createWindow(); } },
    { label: 'New conversation', click: () => { void backend.newConversation(); mainWindow?.show(); } },
    { type: 'separator' }, { label: 'Quit', click: () => app.quit() },
  ]));
  globalShortcut.register('CommandOrControl+Shift+Space', () => {
    if (mainWindow?.isVisible()) mainWindow.hide(); else if (mainWindow) mainWindow.show(); else void createWindow();
  });
}

async function bootstrap(): Promise<void> {
  registerAppProtocol();
  appData = app.getPath('userData');
  await mkdir(appData, { recursive: true });
  const agentHome = join(appData, '.agent-workspace');
  const agentConfigDir = join(agentHome, '.kiro', 'agents');
  await mkdir(agentConfigDir, { recursive: true });
  await copyFile(join(app.getAppPath(), '.kiro/agents/agenticos.json'), join(agentConfigDir, 'agenticos.json'));
  database = new AppDatabase(appData);
  database.interruptRunningTasks();
  const libraryPath = join(appData, 'skills');
  skills = new SkillRegistry(libraryPath, database);
  await skills.initialize();
  files = new FileExecutor();
  const workspace = database.getSetting('workspace');
  if (workspace) {
    try { await access(workspace, constants.R_OK); files.setWorkspace(workspace); }
    catch { database.setSetting('workspace', ''); }
  }
  browser = new BrowserExecutor(appData);
  gateway = new McpGateway({
    skills,
    files,
    browser,
    taskId: () => database.listTasks().find((task) => task.status === 'running')?.id,
    emit: broadcast,
    persistEvidence: (taskId, text) => { database.addMessage(taskId, 'tool', text); database.addTaskEvent(taskId, 'evidence', { text }); },
  });
  backend = new KiroBackend(database, skills, gateway, () => files.getWorkspace(), agentHome, broadcast);
  registerIpc();
  setupMenu();
  setupTray();
  await createWindow();
  await runVersionCheck();
}

app.whenReady().then(() => { void bootstrap().catch((error) => dialog.showErrorBox('Agentic OS could not start', error instanceof Error ? error.message : String(error))); });

app.on('activate', () => { if (!mainWindow) void createWindow(); else mainWindow.show(); });
app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  void browser?.close();
  void backend?.stop();
  void gateway?.stop();
  database?.close();
  tray?.destroy();
});
