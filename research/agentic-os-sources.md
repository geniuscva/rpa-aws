# Agentic OS research notes

Research date: 2026-10-08. Primary/first-party sources used to select the MVP integration approach.

## Kiro CLI and skills

- ACP is the client-to-agent boundary; MCP connects the agent to external tools. Kiro describes ACP session lifecycle, streaming updates, permission requests, and capability negotiation: <https://kiro.dev/docs/acp/>.
- Kiro CLI ACP uses JSON-RPC over stdin/stdout and supports initialize, session creation/loading, prompt, cancel, and session updates: <https://kiro.dev/docs/cli/acp/>.
- Kiro Agent Skills use a `SKILL.md` package with required `name` and `description` metadata; descriptions support discovery and full instruction content can be loaded on demand: <https://kiro.dev/docs/skills/>.
- The installed local CLI is v2.25.0. A read-only initialize handshake reported protocol v1, `loadSession: true`, image input support, and audio input false. ACP capability negotiation is authoritative; features will not be assumed from a version number.

## Agent and integration design

- Start with simple, composable agent patterns and add orchestration complexity only as the workflow requires: <https://www.anthropic.com/engineering/building-effective-agents>.
- The official MCP TypeScript SDK exposes MCP tools and resources. The v1 documentation describes local stdio transport; current v2 is a separate package family and should not be substituted without confirming compatibility with the pinned Kiro CLI: <https://ts.sdk.modelcontextprotocol.io/> and <https://ts.sdk.modelcontextprotocol.io/v2/>.
- MCP authorization covers protocol-level access and does not replace application-specific action policy: <https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization>.

## Desktop and browser security

- Electron recommends sandboxing renderers, enabling context isolation, limiting navigation, and validating IPC senders: <https://www.electronjs.org/docs/latest/tutorial/security>.
- Playwright BrowserContext provides isolated browser sessions suitable for per-task/browser-profile boundaries: <https://playwright.dev/docs/browser-contexts>.
- macOS Accessibility exposes `AXIsProcessTrusted()` to check whether an app is authorized as an accessibility client: <https://developer.apple.com/documentation/applicationservices/1460720-axisprocesstrusted>.

## Implementation consequence

Use ACP for Kiro sessions; app-owned MCP tools for Skills and allowed desktop actions; application policy checks at every executor call; and local persistence for task, approval, and artifact history. Skills are content, not permission grants.
