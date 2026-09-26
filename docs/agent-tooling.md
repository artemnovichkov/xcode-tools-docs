# Agent tooling

[README](../README.md) · [Tool reference](tools.md) · [Headless mode](headless.md) · [Agent tooling](agent-tooling.md) · [Schemas](schemas.md) · [Changelog](../CHANGELOG.md)

Around the MCP server Xcode 27 ships a launcher for coding agents, an exporter for its own skills, and a second MCP server for LLDB.

## Connecting through mcpbridge

`xcrun mcpbridge` is the stdio MCP server your agent connects to. It uses the Xcode selected by `xcode-select`; `MCP_XCODE_PID` targets a specific instance, and `MCP_XCODE_SESSION_ID` passes a session UUID. With [headless mode](headless.md#headless-mode) enabled, the same command reaches the headless service.

Its `run-agent` subcommand launches a coding agent with Xcode tools configured. The `skills` and `plugin` subcommands export Xcode's skills, as described below.

## `run-agent` — launch an agent the way Xcode does

```bash
xcrun mcpbridge run-agent claude      # or: xcrun agent claude
xcrun agent --dry-run claude          # print the resolved command, launch nothing
```

`xcrun agent` is a shim for `mcpbridge run-agent`. Agents: `antigravity`, `claude`, `claude-ext`, `codex`, `mock-agent`.

It launches Xcode's own copy of the agent (`~/Library/Developer/Xcode/CodingAssistant/Agents/`, version-pinned per Xcode build), checks its code signature, passes a temp `--mcp-config` with the `xcode-tools` server (`--no-xcode-tools` omits it), and injects Xcode's environment — `MCP_XCODE_PID` binds the session to that Xcode instance, `CLAUDE_CONFIG_DIR` points at a config dir separate from your own. It does **not** pass `--plugin-dir`, so the agent starts without Xcode's skills.

## `plugin` / `skills` — Xcode's skills

Xcode keeps its skills inside `IDEIntelligenceChat.framework` and renders them on demand into an agent plugin (`xcode-integration`, 15 skills):

```bash
xcrun agent plugin path --plugin-format claude|codex|gemini
claude --plugin-dir "$(xcrun agent plugin path --plugin-format claude)"
```

The path is `~/Library/Developer/Xcode/CodingAssistant/ExportedPlugins/<build>/<format>` — cached, and versioned per Xcode build. Each format differs only in packaging (`.claude-plugin/plugin.json` + an `.mcp.json` wired to `mcpbridge`, `.codex-plugin/plugin.json`, `gemini-extension.json`); the skills themselves are the same. Rendering needs a running Xcode or `XcodeService`, otherwise you get an empty scaffold.

`skills export` writes bare skill directories instead, but only **10** of the 15 — without the three `accessibility-*` skills and the two [localization](tools.md#localization) ones:

```bash
xcrun agent skills export --replace-existing ~/my-skills    # default: ./xcode-skills
```

## `lldb-mcp`

`xcrun lldb-mcp` is a separate stdio MCP server (`lldb-mcp 0.1.0`) exposing LLDB rather than Xcode, with two tools: `command` (run an lldb command; optional `debugger` id or session URI) and `debugger_list`. To drive the debugger through Xcode instead, use [`InvokeDebuggerCommand`](tools.md#invokedebuggercommand).
