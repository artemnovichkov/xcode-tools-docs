# Headless mode & permissions `[27+]`

Headless mode lets the MCP operate **without an open Xcode window**, with durable
per-agent, per-folder permissions that persist across sessions. The runtime is
`XcodeService.app` — a RunningBoard-managed job reusing Xcode's engine, no Dock
presence. Started via `xcrun mcp-server`.

## Windowed vs headless differences

- **`workspaceIdentifier` replaces `tabIdentifier`.** In headless mode every tool that
  took `tabIdentifier` takes `workspaceIdentifier` instead, accepting either an
  identifier (e.g. `workspace-LKfjPJCMBL`) or an **absolute project path**. Tools
  written for windowed mode need this swap.
- Workspace management (`XcodeListWorkspaces`, `XcodeOpenWorkspace`,
  `XcodeCloseWorkspace`) and `XcodeNewProject` matter most here — there's no UI to open
  a project for you.

## Permission model

Granted permissions live in a user-only-readable JSON file:

```
~/Library/Group Containers/group.com.apple.dt.Xcode.SecureSettingsContainer/CodingAssistant/HeadlessPermissions/mcp-server.json
```

- **Agents are identified by code-signing identity** (team + signing identifier) for
  signed binaries — not by file path.
- **Unsigned agents** can only get `--for-24-hours` approval; `--always` is rejected.
- **Wrapping the launch command re-attributes the agent.** If you wrap it (e.g.
  `timeout xcrun mcpbridge …`), the *wrapper* (the launching process) is recorded as
  the agent, not `mcpbridge`. Be deliberate about what launches the server.
- **Opening a project grants its enclosing folder.** `XcodeOpenWorkspace` on a project
  outside every permitted folder **adds that folder to `folderPermissions` without a
  prompt** for an already-approved agent — it can widen its own reach. Keep this in
  mind when scoping access.

## Approval CLI

```bash
xcrun mcp-server approve <agent-id> --always          # persistent (signed agents only)
xcrun mcp-server approve <agent-id> --for-24-hours     # temporary (works for unsigned)
xcrun mcp-server deny <agent-id>
xcrun mcp-server clear-permissions
```

For fully unattended CI you can pre-approve everything with
`--unsafe-always-allow-all-agents` — **not** for interactive use; it removes the trust
boundary.

## Gotchas

- **All headless capability is `[27+]`.** On 26.5 there is no headless mode.
- **Absolute paths are valid `workspaceIdentifier`s** — convenient when you don't have
  the opaque identifier handy.
- **Auto-widening folder permission** (above) is the surprising one — a granted agent
  silently extends its folder reach by opening projects elsewhere.
