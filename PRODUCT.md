# Product

<!-- impeccable:product-schema 1 -->

## Platform

macOS

## Stack

Electron, React, TypeScript, Kiro CLI ACP, SQLite, Playwright, and allow-listed Finder/TextEdit actions.

## Users

One individual using an Apple Silicon Mac who wants an AI agent to carry out observable personal computer tasks.

## Product Purpose

Agentic OS is a personal desktop control surface for delegating browser and supported macOS tasks to an AI agent, with progress, approvals, and results visible in one place.

## Positioning

Kiro CLI provides the agent harness; Agentic OS owns the dashboard, application-managed Agent Skills library, action permissions, task history, and local computer executors.

## Operating Context

The user sends tasks in Vietnamese or English through chat. Initial workflows research web pages, locate files in user-granted folders, and create documents for TextEdit. The user can observe browser activity and approve consequential actions.

## Capabilities and Constraints

- macOS only, single user, local app data, Kiro CLI as the cloud-backed agent.
- Agent Skills are imported into and managed only in the application's own library.
- The renderer does not receive direct filesystem, shell, or credential access.
- Initial desktop targets are a managed browser, Finder, and TextEdit.
- Voice, wake word, external account integrations, marketplace skills, arbitrary application control, and background operation after app exit are out of scope for the MVP.
- Imported skill scripts are preserved but not executed.

## Evidence on Hand

- Kiro CLI 2.25.0 is installed at `/Users/ngochungnguyen/.local/bin/kiro-cli`.
- A read-only ACP initialize handshake completed successfully; the installed CLI advertises session loading and image input, but not audio input.
- No credentials, quota, or end-to-end model request has been verified.
- No logos, customer claims, or external brand assets were supplied.

## Product Principles

- Keep computer actions visible and interruptible.
- Keep local skills, task state, and permission decisions under application control.
- Require explicit approval for consequential or unclear changes.
- Show verifiable results and recover clearly from interruptions.
