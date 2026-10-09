import { contextBridge, ipcRenderer } from 'electron';
import type { AppEvent, DesktopBridge } from '../shared/contracts.js';

const api: DesktopBridge = {
  getDashboard: () => ipcRenderer.invoke('dashboard:get', {}),
  getSkills: () => ipcRenderer.invoke('skills:list', {}),
  getMessages: (taskId) => ipcRenderer.invoke('chat:messages', { taskId }),
  importSkill: () => ipcRenderer.invoke('skills:import', {}),
  resolveSkillConflict: (skillId, importId, action) => ipcRenderer.invoke('skills:resolve-conflict', { skillId, importId, action }),
  readSkill: (skillId) => ipcRenderer.invoke('skills:read', { skillId }),
  setSkillEnabled: (skillId, enabled) => ipcRenderer.invoke('skills:enabled', { skillId, enabled }),
  removeSkill: (skillId) => ipcRenderer.invoke('skills:remove', { skillId }),
  sendMessage: (text, skillId) => ipcRenderer.invoke('chat:send', { text, skillId }),
  newConversation: () => ipcRenderer.invoke('chat:new', {}),
  cancelTask: (taskId) => ipcRenderer.invoke('task:cancel', { taskId }),
  chooseWorkspace: () => ipcRenderer.invoke('workspace:choose', {}),
  revealWorkspace: () => ipcRenderer.invoke('system:reveal-workspace', {}),
  onEvent(callback) {
    const listener = (_event: Electron.IpcRendererEvent, payload: AppEvent) => callback(payload);
    ipcRenderer.on('app:event', listener);
    return () => ipcRenderer.removeListener('app:event', listener);
  },
};

contextBridge.exposeInMainWorld('agenticOS', api);
