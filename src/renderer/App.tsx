import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react';
import {
  Activity, ArrowUp, ArrowUpRight, Check, CheckCircle2, ChevronDown, ChevronRight,
  CircleAlert, Clock3, Command, FileText, Folder, FolderOpen, Globe2, LayoutDashboard, Loader2,
  MoreHorizontal, PanelRightClose, Plus, Search, Settings2, Shield, Sparkles, Square, Trash2,
  Upload, WandSparkles, X, BookOpen,
} from 'lucide-react';
import type { AppStatus, AssistantMessage, DashboardData, ImportSkillResult, SkillSummary, TaskSummary } from '../shared/contracts.js';

type View = 'chat' | 'tasks' | 'skills' | 'settings';
type FeedItem = { id: string; kind: 'message' | 'tool'; role: 'user' | 'assistant' | 'tool'; text: string; time: string };

function timeLabel(iso: string): string {
  return new Intl.DateTimeFormat('vi-VN', { hour: '2-digit', minute: '2-digit' }).format(new Date(iso));
}

function statusLabel(status: AppStatus['kiro']): string {
  if (status === 'ready') return 'Kiro đang kết nối';
  if (status === 'missing') return 'Chưa tìm thấy Kiro';
  if (status === 'error') return 'Kiro cần kiểm tra';
  return 'Đã tìm thấy Kiro CLI';
}

function App() {
  const [view, setView] = useState<View>('chat');
  const [data, setData] = useState<DashboardData>({ tasks: [], skills: [], status: { kiro: 'checking' } });
  const [messages, setMessages] = useState<FeedItem[]>([]);
  const [tools, setTools] = useState<Array<{ id: string; title: string; status: string }>>([]);
  const [selectedSkill, setSelectedSkill] = useState<SkillSummary | undefined>();
  const [inspectedSkill, setInspectedSkill] = useState<SkillSummary | undefined>();
  const [conflict, setConflict] = useState<Extract<ImportSkillResult, { kind: 'duplicate' }> | undefined>();
  const [query, setQuery] = useState('');
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState('');
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [workspace, setWorkspace] = useState<string | undefined>();
  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const refresh = useCallback(async () => {
    const next = await window.agenticOS.getDashboard();
    setData(next);
    setWorkspace(next.workspace);
    const active = next.tasks[0];
    if (active) {
      const persisted = await window.agenticOS.getMessages(active.id);
      setMessages(persisted.map((message: AssistantMessage) => ({ id: message.id, kind: message.role === 'tool' ? 'tool' : 'message', role: message.role, text: message.text, time: message.createdAt })));
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    return window.agenticOS.onEvent((event) => {
      if (event.type === 'agent:message') {
        setMessages((items) => [...items, { id: crypto.randomUUID(), kind: event.role === 'tool' ? 'tool' : 'message', role: event.role, text: event.text, time: new Date().toISOString() }]);
      } else if (event.type === 'agent:tool') {
        setTools((items) => {
          const without = items.filter((item) => item.id !== event.toolId);
          return [...without, { id: event.toolId, title: event.title, status: event.status }].slice(-8);
        });
      } else if (event.type === 'task:status') {
        setData((current) => ({ ...current, tasks: [event.task, ...current.tasks.filter((task) => task.id !== event.task.id)].slice(0, 30) }));
      } else if (event.type === 'app:status') {
        setData((current) => ({ ...current, status: event.status }));
      } else if (event.type === 'skills:changed') {
        setData((current) => ({ ...current, skills: event.skills }));
      }
    });
  }, []);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, tools]);
  useEffect(() => { if (!toast) return; const id = window.setTimeout(() => setToast(''), 3200); return () => window.clearTimeout(id); }, [toast]);

  const enabledSkills = useMemo(() => data.skills.filter((skill) => skill.enabled), [data.skills]);
  const busyTask = data.tasks.find((task) => task.status === 'running' || task.status === 'awaiting_approval');

  const updateSkill = async (skill: SkillSummary, enabled: boolean) => {
    try {
      const updated = await window.agenticOS.setSkillEnabled(skill.id, enabled);
      if (inspectedSkill?.id === skill.id) setInspectedSkill(updated);
      setToast(enabled ? `${skill.name} đã bật` : `${skill.name} đã tắt`);
    }
    catch (error) { setToast(error instanceof Error ? error.message : 'Không thể cập nhật skill.'); }
  };

  const removeSkill = async (skill: SkillSummary) => {
    if (!window.confirm(`Xóa “${skill.name}” khỏi thư viện Agentic OS?`)) return;
    try {
      await window.agenticOS.removeSkill(skill.id);
      if (inspectedSkill?.id === skill.id) setInspectedSkill(undefined);
      if (selectedSkill?.id === skill.id) setSelectedSkill(undefined);
      setToast(`Đã xóa ${skill.name} khỏi thư viện.`);
    } catch (error) { setToast(error instanceof Error ? error.message : 'Không thể xóa skill.'); }
  };

  const importSkill = async () => {
    setBusy(true);
    try {
      const result = await window.agenticOS.importSkill();
      if (result.kind === 'imported') setToast(`Đã thêm ${result.skill.name}. Kiểm tra hướng dẫn rồi bật để sử dụng.`);
      if (result.kind === 'duplicate') setConflict(result);
    } catch (error) { setToast(error instanceof Error ? error.message : 'Không thể import skill.'); }
    finally { setBusy(false); }
  };

  const inspectSkill = async (skill: SkillSummary) => {
    try {
      const detail = await window.agenticOS.readSkill(skill.id);
      setInspectedSkill({ ...detail.skill, description: detail.instructions ? skill.description : skill.description, contentHash: skill.contentHash, importedAt: skill.importedAt, usedAt: skill.usedAt, capabilities: skill.capabilities, hasScripts: skill.hasScripts });
      setSkillInstructions(detail.instructions);
    } catch (error) { setToast(error instanceof Error ? error.message : 'Không đọc được skill.'); }
  };

  const [skillInstructions, setSkillInstructions] = useState('');

  const submit = async (event?: FormEvent) => {
    event?.preventDefault();
    if (sending || !draft.trim()) return;
    let text = draft.trim();
    let skill = selectedSkill;
    const skillCommand = text.match(/^\/skill(?:\s+([^\s]+))?(?:\s+([\s\S]*))?$/i);
    const directCommand = text.match(/^\/([a-z0-9]+(?:-[a-z0-9]+)*)(?:\s+([\s\S]*))?$/i);
    if (skillCommand) {
      if (!skillCommand[1]) { setView('skills'); return; }
      const found = enabledSkills.find((item) => item.name.toLowerCase() === skillCommand[1].toLowerCase());
      if (!found) { setToast(`Không tìm thấy skill đang bật: ${skillCommand[1]}`); return; }
      skill = found;
      text = skillCommand[2]?.trim() || `Use the ${found.name} skill for my next request.`;
    } else if (directCommand) {
      const found = enabledSkills.find((item) => item.name.toLowerCase() === directCommand[1].toLowerCase());
      if (found) {
        skill = found;
        text = directCommand[2]?.trim() || `Use the ${found.name} skill for my next request.`;
      }
    }
    setDraft('');
    setSending(true);
    if (!data.tasks.length || data.tasks[0]?.status === 'cancelled' || data.tasks[0]?.status === 'failed') {
      setMessages([]);
      setTools([]);
    }
    setMessages((items) => [...items, { id: crypto.randomUUID(), kind: 'message', role: 'user', text, time: new Date().toISOString() }]);
    try {
      await window.agenticOS.sendMessage(text, skill?.id);
      setSelectedSkill(undefined);
      await refresh();
    } catch (error) {
      setToast(error instanceof Error ? error.message : 'Tác vụ không thể hoàn thành.');
      setMessages((items) => [...items, { id: crypto.randomUUID(), kind: 'tool', role: 'tool', text: error instanceof Error ? error.message : 'Kiro chưa thể chạy tác vụ.', time: new Date().toISOString() }]);
      await refresh();
    } finally { setSending(false); }
  };

  const startNewChat = async () => {
    await window.agenticOS.newConversation();
    setMessages([]);
    setTools([]);
    setDraft('');
    setSelectedSkill(undefined);
    setView('chat');
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const useSkill = (skill: SkillSummary) => {
    setSelectedSkill(skill);
    setInspectedSkill(undefined);
    setView('chat');
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const chooseWorkspace = async () => {
    const path = await window.agenticOS.chooseWorkspace();
    if (path) { setWorkspace(path); setToast('Workspace đã sẵn sàng.'); }
  };

  const stopTask = async () => {
    if (!busyTask) return;
    await window.agenticOS.cancelTask(busyTask.id);
  };

  const filteredSkills = data.skills.filter((skill) => `${skill.name} ${skill.description}`.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-row">
          <div className="brand-mark"><span /></div>
          <div className="brand-copy"><strong>AGENTIC OS</strong><span>PERSONAL WORKSPACE</span></div>
          <button className="icon-button sidebar-more" aria-label="More options"><MoreHorizontal size={17} /></button>
        </div>

        <button className="new-chat-button" onClick={() => void startNewChat()}><Plus size={16} strokeWidth={2.2} />New conversation<span className="shortcut"><Command size={11} />K</span></button>
        <div className="nav-group-label">WORKSPACE</div>
        <nav className="primary-nav" aria-label="Main navigation">
          <NavButton active={view === 'chat'} onClick={() => setView('chat')} icon={<LayoutDashboard size={17} />} label="Overview" />
          <NavButton active={view === 'tasks'} onClick={() => setView('tasks')} icon={<Activity size={17} />} label="Tasks" count={data.tasks.length} />
          <NavButton active={view === 'skills'} onClick={() => setView('skills')} icon={<WandSparkles size={17} />} label="Agent Skills" count={data.skills.length} />
        </nav>

        <div className="sidebar-section-heading"><span>Recent</span><button className="icon-button" aria-label="New conversation" onClick={() => void startNewChat()}><Plus size={15} /></button></div>
        <div className="recent-list">
          {data.tasks.slice(0, 5).map((task) => <button className="recent-item" key={task.id} onClick={() => setView('chat')}><span className={`task-dot ${task.status}`} /><span className="recent-title">{task.title}</span></button>)}
          {!data.tasks.length && <p className="sidebar-empty">Your tasks will appear here.</p>}
        </div>

        <div className="sidebar-bottom">
          <div className="sidebar-skill-summary"><div className="skill-stack-icon"><WandSparkles size={15} /></div><div><strong>{enabledSkills.length} skills active</strong><span>{data.skills.length} in your library</span></div><button onClick={() => setView('skills')} aria-label="Open Agent Skills"><ChevronRight size={15} /></button></div>
          <button className={`nav-item settings-link ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}><Settings2 size={17} /><span>Settings</span></button>
          <div className="profile-row"><div className="profile-avatar">H</div><div className="profile-name"><strong>Local workspace</strong><span>On this Mac</span></div><span className="privacy-dot" title="Local app data" /></div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>Agentic OS</span><ChevronRight size={14} /><strong>{view === 'chat' ? 'Overview' : view === 'tasks' ? 'Tasks' : view === 'skills' ? 'Agent Skills' : 'Settings'}</strong></div>
          <div className="topbar-actions">
            <button className="workspace-select" onClick={() => void chooseWorkspace()} title={workspace ?? 'Choose a workspace'}><FolderOpen size={15} /><span>{workspace ? workspace.split('/').filter(Boolean).slice(-2).join('/') : 'Choose workspace'}</span><ChevronDown size={13} /></button>
            <span className={`connection-status ${data.status.kiro}`}><span className="status-dot" />{statusLabel(data.status.kiro)}</span>
            <button className="icon-button" onClick={() => setShowRightPanel((value) => !value)} aria-label="Toggle context panel"><PanelRightClose size={17} /></button>
          </div>
        </header>

        {view === 'chat' && <div className={`workspace-layout ${showRightPanel ? '' : 'context-hidden'}`}>
          <section className="conversation-pane">
            <div className="conversation-scroll">
              {messages.length === 0 ? <div className="welcome-state">
                <div className="welcome-emblem"><div className="emblem-orbit orbit-a" /><div className="emblem-orbit orbit-b" /><div className="emblem-core"><Sparkles size={22} /></div></div>
                <p className="welcome-overline">YOUR PERSONAL AGENT</p>
                <h1>What can I take care of?</h1>
                <p className="welcome-subtitle">Ask Jarvis to research, find a file, or create a document. You’ll see each step as it happens.</p>
                <div className="suggestion-list">
                  <Suggestion icon={<Globe2 size={16} />} title="Research a topic" detail="Find trusted sources and save a summary" onClick={() => setDraft('Research recent approaches to personal AI assistants, cite three primary sources, and save a summary.')} />
                  <Suggestion icon={<Search size={16} />} title="Find a file" detail="Search inside your granted workspace" onClick={() => setDraft('Find the most recently edited Markdown files in my workspace.')} />
                  <Suggestion icon={<FileText size={16} />} title="Create a document" detail="Draft a new file without overwriting" onClick={() => setDraft('Create a short Markdown document for my next project notes.')} />
                </div>
              </div> : <div className="message-list">
                <div className="conversation-heading"><div><p className="welcome-overline">CURRENT CONVERSATION</p><h1>{data.tasks[0]?.title ?? 'Jarvis'}</h1></div><button className="quiet-button" onClick={() => void startNewChat()}><Plus size={15} />New chat</button></div>
                {messages.map((message) => <MessageView key={message.id} message={message} />)}
                {sending && <div className="agent-thinking"><div className="thinking-avatar"><Sparkles size={14} /></div><span>{tools.at(-1)?.title ?? 'Jarvis is working'}</span><Loader2 size={14} className="spin" /></div>}
                <div ref={endRef} />
              </div>}
            </div>

            <div className="composer-wrap">
              {selectedSkill && <div className="selected-skill"><WandSparkles size={13} /><span>Using {selectedSkill.name}</span><button aria-label="Remove selected skill" onClick={() => setSelectedSkill(undefined)}><X size={13} /></button></div>}
              {draft.startsWith('/') && enabledSkills.length > 0 && <div className="slash-menu" role="listbox" aria-label="Choose an Agent Skill">{enabledSkills.filter((skill) => { const query = draft.slice(1).split(/\s/, 1)[0]!.toLowerCase(); return !query || query === 'skill' || skill.name.toLowerCase().startsWith(query); }).slice(0, 7).map((skill) => <button key={skill.id} type="button" role="option" onClick={() => { setSelectedSkill(skill); setDraft(`/${skill.name} `); textareaRef.current?.focus(); }}><WandSparkles size={14} /><span><strong>{skill.name}</strong><small>{skill.description}</small></span><ArrowUpRight size={13} /></button>)}</div>}
              <form className="composer" onSubmit={(event) => void submit(event)}>
                <textarea ref={textareaRef} aria-label="Message Jarvis" placeholder={selectedSkill ? `Ask about ${selectedSkill.name}…` : 'Message Jarvis… type /skill-name'} value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void submit(); } }} rows={2} />
                <div className="composer-footer">
                  <div className="composer-tools"><button type="button" className="composer-tool" onClick={() => setView('skills')}><WandSparkles size={14} /><span>Skills</span></button><span className="composer-divider" /><span className="tool-scope"><Shield size={12} />Read freely · ask before changes</span></div>
                  <div className="composer-actions"><span className="keyboard-hint">↵ send <span>·</span> ⇧↵ new line</span>{sending ? <button type="button" className="send-button stop-button" onClick={() => void stopTask()} aria-label="Stop task"><Square size={14} fill="currentColor" /></button> : <button type="submit" className="send-button" disabled={!draft.trim()} aria-label="Send message"><ArrowUp size={17} /></button>}</div>
                </div>
              </form>
              <p className="composer-disclaimer">Kiro runs on its cloud service. Local files stay inside the folders you choose.</p>
            </div>
          </section>

          {showRightPanel && <aside className="context-panel">
            <div className="context-panel-head"><div><span className="panel-label">LIVE CONTEXT</span><h2>Task details</h2></div><button className="icon-button" onClick={() => setShowRightPanel(false)} aria-label="Close context panel"><X size={16} /></button></div>
            <div className="context-block"><div className="context-row-title"><span className="context-icon"><Activity size={14} /></span><strong>Activity</strong><span className="context-count">{tools.length || 0}</span></div>
              {tools.length ? <div className="activity-list">{tools.slice(-5).map((tool) => <div className="activity-item" key={tool.id}><span className={`activity-state ${tool.status}`} /> <div><p>{tool.title}</p><span>{tool.status}</span></div></div>)}</div> : <p className="context-empty">Tool activity will appear when Jarvis starts a task.</p>}
            </div>
            <div className="context-divider" />
            <div className="context-block"><div className="context-row-title"><span className="context-icon"><WandSparkles size={14} /></span><strong>Enabled skills</strong><button className="text-action" onClick={() => setView('skills')}>Manage</button></div>
              {enabledSkills.length ? <div className="enabled-list">{enabledSkills.slice(0, 6).map((skill) => <button key={skill.id} className={`enabled-skill-row ${selectedSkill?.id === skill.id ? 'selected' : ''}`} onClick={() => useSkill(skill)}><span className="skill-file-icon"><BookOpen size={13} /></span><span><strong>{skill.name}</strong><small>{skill.description}</small></span><ArrowUpRight size={13} /></button>)}</div> : <button className="empty-skills" onClick={() => setView('skills')}><span className="empty-skill-symbol"><Plus size={16} /></span><span><strong>Add your first skill</strong><small>Import a SKILL.md package</small></span><ChevronRight size={14} /></button>}
            </div>
            <div className="context-divider" />
            <div className="context-block"><div className="context-row-title"><span className="context-icon"><Folder size={14} /></span><strong>Workspace access</strong></div>
              {workspace ? <button className="workspace-path" onClick={() => void chooseWorkspace()}><FolderOpen size={15} /><span>{workspace}</span><ChevronRight size={13} /></button> : <button className="grant-folder" onClick={() => void chooseWorkspace()}><Plus size={14} />Choose a folder</button>}
              <p className="panel-helper">Jarvis can read and create new files here. Existing files are never overwritten.</p>
            </div>
            <div className="context-footnote"><Shield size={13} /><span>Actions stay within the permissions you grant.</span></div>
          </aside>}
        </div>}

        {view === 'skills' && <SkillsView skills={filteredSkills} query={query} setQuery={setQuery} onImport={() => void importSkill()} busy={busy} onToggle={updateSkill} onInspect={(skill) => void inspectSkill(skill)} onUse={useSkill} onRemove={(skill) => void removeSkill(skill)} />}
        {view === 'tasks' && <TasksView tasks={data.tasks} onNew={() => void startNewChat()} />}
        {view === 'settings' && <SettingsView status={data.status} workspace={workspace} onChoose={() => void chooseWorkspace()} onOpen={() => void window.agenticOS.revealWorkspace()} />}
      </main>

      {inspectedSkill && <div className="drawer-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setInspectedSkill(undefined); }}><aside className="skill-drawer" aria-label={`${inspectedSkill.name} skill details`}>
        <div className="drawer-top"><div><span className="panel-label">AGENT SKILL</span><h2>{inspectedSkill.name}</h2></div><button className="icon-button" onClick={() => setInspectedSkill(undefined)} aria-label="Close skill details"><X size={17} /></button></div>
        <p className="drawer-description">{inspectedSkill.description}</p>
        <div className="drawer-meta"><span>SHA-256</span><code>{inspectedSkill.contentHash.slice(0, 16)}…</code></div>
        <div className="drawer-meta"><span>Imported</span><span>{new Date(inspectedSkill.importedAt).toLocaleDateString('vi-VN')}</span></div>
        <div className="drawer-meta"><span>Bundled scripts</span><span>{inspectedSkill.hasScripts ? 'Present · not executed' : 'None'}</span></div>
        <div className="drawer-content-heading">Instructions preview</div>
        <pre className="skill-markdown">{skillInstructions || 'This skill has no instruction body.'}</pre>
        <div className="drawer-actions"><button className="button-secondary" onClick={() => void updateSkill(inspectedSkill, !inspectedSkill.enabled)}>{inspectedSkill.enabled ? 'Turn off' : 'Enable skill'}</button><button className="button-primary" onClick={() => useSkill(inspectedSkill)}><WandSparkles size={14} />Use in chat</button></div>
      </aside></div>}

      {conflict && <div className="modal-backdrop" role="presentation"><section className="conflict-dialog" role="dialog" aria-modal="true" aria-labelledby="duplicate-heading"><div className="dialog-icon"><CircleAlert size={19} /></div><button className="icon-button dialog-close" aria-label="Close dialog" onClick={() => setConflict(undefined)}><X size={16} /></button><h2 id="duplicate-heading">Skill name already in use</h2><p>“{conflict.incoming.name}” is already in your library. Replace the existing package or keep both copies?</p><div className="dialog-compare"><div><span>EXISTING</span><strong>{conflict.existing.name}</strong><code>{conflict.existing.contentHash.slice(0, 12)}</code></div><ChevronRight size={15} /><div><span>IMPORTED</span><strong>{conflict.incoming.name}</strong><code>{conflict.incoming.contentHash.slice(0, 12)}</code></div></div><div className="dialog-actions"><button className="button-secondary" onClick={() => setConflict(undefined)}>Cancel</button><button className="button-secondary" onClick={() => void resolveConflict('keep-both')}>Keep both</button><button className="button-primary" onClick={() => void resolveConflict('replace')}>Replace</button></div></section></div>}

      {toast && <div className="toast" role="status"><CheckCircle2 size={16} />{toast}<button onClick={() => setToast('')} aria-label="Dismiss"><X size={14} /></button></div>}
    </div>
  );

  async function resolveConflict(action: 'replace' | 'keep-both') {
    if (!conflict) return;
    try {
      await window.agenticOS.resolveSkillConflict(conflict.existing.id, conflict.importId, action);
      setConflict(undefined);
      setToast(action === 'replace' ? 'Skill đã được thay thế.' : 'Đã giữ cả hai phiên bản skill.');
    } catch (error) { setToast(error instanceof Error ? error.message : 'Không thể xử lý skill trùng tên.'); }
  }
}

function NavButton({ active, onClick, icon, label, count }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string; count?: number }) {
  return <button className={`nav-item ${active ? 'active' : ''}`} onClick={onClick}>{icon}<span>{label}</span>{count !== undefined && count > 0 && <small>{count}</small>}</button>;
}

function Suggestion({ icon, title, detail, onClick }: { icon: React.ReactNode; title: string; detail: string; onClick: () => void }) {
  return <button className="suggestion-row" onClick={onClick}><span className="suggestion-icon">{icon}</span><span className="suggestion-copy"><strong>{title}</strong><small>{detail}</small></span><ArrowUpRight size={15} className="suggestion-arrow" /></button>;
}

function MessageView({ message }: { message: FeedItem }) {
  if (message.role === 'user') return <article className="user-message"><div className="user-message-bubble">{message.text}</div><time>{timeLabel(message.time)}</time></article>;
  if (message.role === 'tool') return <div className="tool-evidence"><span className="evidence-icon"><Check size={12} /></span><span>{message.text}</span></div>;
  return <article className="assistant-message"><div className="assistant-avatar"><Sparkles size={14} /></div><div className="assistant-body"><div className="assistant-label">JARVIS <span>·</span> {timeLabel(message.time)}</div><div className="assistant-copy">{message.text}</div></div></article>;
}

function SkillsView({ skills, query, setQuery, onImport, busy, onToggle, onInspect, onUse, onRemove }: { skills: SkillSummary[]; query: string; setQuery: (value: string) => void; onImport: () => void; busy: boolean; onToggle: (skill: SkillSummary, enabled: boolean) => void; onInspect: (skill: SkillSummary) => void; onUse: (skill: SkillSummary) => void; onRemove: (skill: SkillSummary) => void }) {
  return <div className="content-view skills-view">
    <div className="view-heading"><div><p className="welcome-overline">PERSONAL LIBRARY</p><h1>Agent Skills</h1><p className="view-description">Import reusable instructions. Jarvis can discover enabled skills and load their details when needed.</p></div><button className="button-primary import-button" onClick={onImport} disabled={busy}>{busy ? <Loader2 size={15} className="spin" /> : <Upload size={15} />}Import skill</button></div>
    <div className="skill-library-toolbar"><div className="skill-count"><strong>{skills.length}</strong><span>skills</span></div><label className="search-field"><Search size={15} /><input placeholder="Search skills…" value={query} onChange={(event) => setQuery(event.target.value)} /><kbd>⌘ F</kbd></label><button className="filter-button"><span className="privacy-dot" />App library<ChevronDown size={13} /></button></div>
    {skills.length ? <div className="skill-table"><div className="skill-table-head"><span>SKILL</span><span>STATUS</span><span>LAST USED</span><span>ACTIONS</span></div>{skills.map((skill) => <article key={skill.id} className="skill-row"><button className="skill-ident" onClick={() => onInspect(skill)}><span className="skill-doc-icon"><BookOpen size={17} /></span><span><strong>{skill.name}</strong><small>{skill.description}</small></span></button><div><button className={`status-pill ${skill.enabled ? 'enabled' : 'disabled'}`} onClick={() => onToggle(skill, !skill.enabled)}><span />{skill.enabled ? 'Enabled' : 'Off'}</button></div><span className="last-used">{skill.usedAt ? new Date(skill.usedAt).toLocaleDateString('vi-VN') : 'Never'}</span><div className="skill-row-actions"><button className="button-text" onClick={() => onInspect(skill)}>Details</button><button className="icon-button" onClick={() => onUse(skill)} aria-label={`Use ${skill.name} in chat`} disabled={!skill.enabled}><ArrowUpRight size={15} /></button><button className="icon-button danger-icon" onClick={() => onRemove(skill)} aria-label={`Remove ${skill.name}`}><Trash2 size={14} /></button></div></article>)}</div> : <div className="empty-library"><div className="empty-library-symbol"><WandSparkles size={19} /></div><h2>{query ? 'No matching skills' : 'Your skill library is empty'}</h2><p>{query ? 'Try a different name or description.' : 'Import a folder with a SKILL.md file to give Jarvis a new workflow.'}</p>{!query && <button className="button-secondary" onClick={onImport} disabled={busy}><Upload size={14} />Import your first skill</button>}</div>}
    <div className="skills-note"><Shield size={14} /><span>Skills guide how Jarvis works. They don’t grant access to files, apps, or accounts.</span></div>
  </div>;
}

function TasksView({ tasks, onNew }: { tasks: TaskSummary[]; onNew: () => void }) {
  return <div className="content-view tasks-view"><div className="view-heading"><div><p className="welcome-overline">ACTIVITY LOG</p><h1>Tasks</h1><p className="view-description">Review recent work and the files or sources it touched.</p></div><button className="button-primary" onClick={onNew}><Plus size={15} />New conversation</button></div>{tasks.length ? <div className="task-table"><div className="task-table-head"><span>TASK</span><span>STATUS</span><span>STARTED</span><span>SKILLS</span></div>{tasks.map((task) => <article className="task-row" key={task.id}><span className="task-name"><span className={`task-dot ${task.status}`} /><span><strong>{task.title}</strong><small>{task.skillVersions.length ? `${task.skillVersions.length} skill version${task.skillVersions.length > 1 ? 's' : ''} used` : 'No skills used'}</small></span></span><span className={`task-state ${task.status}`}><span />{task.status.replaceAll('_', ' ')}</span><time>{new Date(task.createdAt).toLocaleString('vi-VN')}</time><span className="task-skills" title={task.skillVersions.map((skill) => `${skill.name} · ${skill.contentHash}`).join('\n')}>{task.skillVersions.length ? task.skillVersions.map((skill) => `${skill.name} (${skill.contentHash.slice(0, 8)})`).join(', ') : '—'}</span></article>)}</div> : <div className="empty-library"><div className="empty-library-symbol"><Clock3 size={19} /></div><h2>No tasks yet</h2><p>When Jarvis starts work, the task and its status appear here.</p><button className="button-secondary" onClick={onNew}>Start a conversation</button></div>}</div>;
}

function SettingsView({ status, workspace, onChoose, onOpen }: { status: AppStatus; workspace?: string; onChoose: () => void; onOpen: () => void }) {
  return <div className="content-view settings-view"><div className="view-heading"><div><p className="welcome-overline">LOCAL CONFIGURATION</p><h1>Settings</h1><p className="view-description">Manage the parts of your Mac that Jarvis can work with.</p></div></div><section className="settings-section"><div className="settings-section-heading"><h2>Agent connection</h2><p>Kiro CLI runs the agent and manages cloud authentication.</p></div><div className="settings-row"><span className="settings-row-icon"><Command size={16} /></span><span><strong>Kiro CLI</strong><small>{status.message ?? 'Detected on this Mac'}</small></span><span className={`status-pill ${status.kiro === 'missing' || status.kiro === 'error' ? 'disabled' : 'enabled'}`}><span />{statusLabel(status.kiro)}</span></div><div className="settings-note"><CircleAlert size={14} /><span>Agentic OS will not change your Kiro account, global agent settings, or global skills.</span></div></section><section className="settings-section"><div className="settings-section-heading"><h2>Workspace folder</h2><p>Jarvis can search and read files, then create new documents inside this folder.</p></div><div className="settings-row"><span className="settings-row-icon"><FolderOpen size={16} /></span><span className="settings-folder-path"><strong>{workspace ? workspace.split('/').filter(Boolean).slice(-2).join('/') : 'No folder selected'}</strong><small>{workspace ?? 'Choose a folder to enable local file tools.'}</small></span><button className="button-secondary" onClick={onChoose}>{workspace ? 'Change folder' : 'Choose folder'}</button>{workspace && <button className="button-text" onClick={onOpen}>Reveal</button>}</div><div className="settings-note"><Shield size={14} /><span>Reads stay inside the selected folder. New files use unique names; existing files are never overwritten.</span></div></section><section className="settings-section"><div className="settings-section-heading"><h2>Agent Skills</h2><p>Imported skills are stored in the app library under Application Support.</p></div><div className="settings-row"><span className="settings-row-icon"><WandSparkles size={16} /></span><span><strong>Application-managed library</strong><small>Local imports · scripts are preserved but never run</small></span><span className="privacy-dot" /></div></section></div>;
}

export default App;
