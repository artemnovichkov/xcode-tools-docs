# Headless mode

[README](../README.md) · [Tool reference](tools.md) · [Headless mode](headless.md) · [Agent tooling](agent-tooling.md) · [Schemas](schemas.md) · [Changelog](../CHANGELOG.md)

**Xcode 27** adds `xcrun mcp-server`, a preview of an MCP server that runs without an open Xcode workspace, and that can grant code-signed agents access to a directory tree for a longer period instead of asking every time. Apple flags it as an early preview: some commands may not work in every configuration, and some settings or permissions may need an Xcode relaunch or a reboot to take effect.

```bash
sudo xcrun mcp-server enable
```

| Command | Description |
|---------|-------------|
| `open <paths>` | Launch if needed, then open workspaces/projects |
| `stop` | Terminate the running server (no-op if not running) |
| `enable` / `disable` | Turn headless mode on/off (sudo) |
| `status` | Report permissions and, when running, the open workspaces |
| `approve <id>` | Approve a pending agent or folder request (sudo). `--always` (signed agents and folders only) or `--for-24-hours` |
| `allow-folder <path>` | Permit workspaces under a folder without waiting for a request (sudo). `--always` or `--for-24-hours` |
| `deny <id>` | Deny a pending request, permitted agent, or permitted folder (sudo); denying an agent also stops the server |
| `clear-permissions` | Remove all granted agent and folder permissions (sudo) |
| `reset-all` | Delete all permission state and kill the server immediately (sudo); next use shows onboarding again |
| `show-logs` | Dump the agent activity log to a file and print its path. Without a running server it collects the last 24 hours |

Every subcommand takes `--format text\|json`. There is no `start` — `open` launches the server.

`show-logs` is the audit trail: one line per agent connection, with the binary path, PID, signing team, and a summary on disconnect.

```
Xcode Service[850]: agent: Xcode/copilot-xcode [9d474085] | connected | binary: … | pid: 735 | signed by: VEKTX9H2N7 | version: 27.0/0.51.0
Xcode Service[55388]: agent: Claude Code [11bcb302] | disconnected | 25 tool calls over 15h 57m 48s
```

Request and permission ids come from `mcp-server status`. For unattended environments, `sudo xcrun mcp-server enable --unsafe-always-allow-all-agents` approves every agent upfront — Apple does not recommend it for at-desk use.

## What actually runs

`xcrun mcp-server` is only a launcher, and so is `xcrun mcpbridge` — with headless mode on it launches or reuses the headless service through LaunchServices, so no Xcode window is needed. The server itself is `Xcode Service.app`, shipped inside Xcode at `Xcode.app/Contents/Developer/Library/Xcode/Agents/Xcode Service.app` with bundle identifier `com.apple.dt.mcp-server` and `LSUIElement`, so it has no Dock icon and no menu bar. It is started as a RunningBoard-managed application job — `launchctl print gui/$(id -u)/application.com.apple.dt.mcp-server.<n>.<n>` shows the job with `managed_by = com.apple.runningboard`. It is the same Xcode engine, not a separate reimplementation, and it can attach a UI later, so headless is a mode rather than a different product.

## Permissions

Granted permissions are stored in a JSON file inside Xcode's secure settings group container, readable only by the user:

```
~/Library/Group Containers/group.com.apple.dt.Xcode.SecureSettingsContainer/CodingAssistant/HeadlessPermissions/mcp-server.json
```

```json
{
  "version": 1,
  "enabled": true,
  "agentPermissions": [
    { "id": "1B162114-…", "trust": { "signed": { "signingIdentifier": "com.anthropic.claude-code", "teamIdentifier": "Q6L2SF6YDW" } } }
  ],
  "folderPermissions": [
    { "id": "B9BAFD34-…", "subtreeRoot": "/Users/username/Developer/MyApp" }
  ]
}
```

Agent trust is a code-signing identity — team identifier plus signing identifier — not a filesystem path, so moving or renaming an approved agent binary does not invalidate its grant, but re-signing it does. Unsigned agents are recorded by path and a content hash, and can only be approved with `--for-24-hours`; `--always` is rejected for them.

Two things are worth knowing before enabling this:

- The identity that gets recorded is the process that **launched** `mcpbridge`, not `mcpbridge` itself. Wrapping the command (for example `timeout xcrun mcpbridge`) registers the wrapper as the agent.
- An already-approved agent can widen its own reach: calling `XcodeOpenWorkspace` on a project outside every permitted folder adds that folder to `folderPermissions` without a prompt, and launching `mcpbridge` from an approved agent's process tree grants the launcher a 24-hour agent permission of its own.

## Tool surface in headless mode

Every tool that takes a `tabIdentifier` in a window takes a **`workspaceIdentifier`** instead: *"Identifies the target workspace directly (used in headless mode): its workspace identifier (e.g. workspace1) or its absolute path."* It accepts either the identifier returned by `XcodeOpenWorkspace`/`XcodeListWorkspaces` (in practice something like `workspace-LKfjPJCMBL`) or the absolute path of the project. Prompts, skills, and scripts that hardcode `tabIdentifier` need updating for headless mode.

[`DocumentationSearch`](tools.md#documentationsearch-) behaves the same in both modes: listed once its documentation asset is installed, absent from `tools/list` while it isn't.
