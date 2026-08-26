# Xcode Tools Documentation

A comprehensive reference for the Xcode MCP Server aka Xcode Tools. These tools enable AI assistants to interact with Xcode workspaces — managing files, building projects, running tests, rendering previews, and more.

> Reflects **Xcode 27 beta 6** (27A5252f). Everything marked 🆕 or listed under [What's new in Xcode 27](#whats-new-in-xcode-27) is relative to the current release, **Xcode 26.5**.

<p align="center">
  <img src=".github/screenshot.png" width="60%"/>
</p>

## Apple Documentation

- [Setting up coding intelligence](https://developer.apple.com/documentation/xcode/setting-up-coding-intelligence)
- [Writing code with intelligence in Xcode](https://developer.apple.com/documentation/xcode/writing-code-with-intelligence-in-xcode)
- [Giving agentic coding tools access to Xcode](https://developer.apple.com/documentation/xcode/giving-agentic-coding-tools-access-to-xcode)

## Prerequisites

- Xcode 27.0+ installed and running with an open workspace — or headless mode enabled, see [Headless mode](#headless-mode-)
- MCP server configured with Xcode integration

> **Note:** Most tools accept an optional `tabIdentifier` parameter that identifies which Xcode workspace tab to operate on — omit it when only one tab is open. In [headless mode](#headless-mode-) the same parameter is named `workspaceIdentifier` and takes a workspace identifier or an absolute path instead.

## Installation

Add the Xcode MCP server to your coding tool via `xcrun mcpbridge`:

**Claude Code:**
```bash
claude mcp add --transport stdio xcode -- xcrun mcpbridge
```

**Codex:**
```bash
codex mcp add xcode -- xcrun mcpbridge
```

Verify with `claude mcp list` or `codex mcp list`.

By default `mcpbridge` connects to the Xcode selected by `xcode-select`; set `MCP_XCODE_PID` to target a specific instance, or `MCP_XCODE_SESSION_ID` to pass a UUID identifying an Xcode tool session. With [headless mode](#headless-mode-) enabled, the same `xcrun mcpbridge` command reaches the headless service — it launches or reuses `XcodeService.app` through LaunchServices, so no Xcode window is needed.

`mcpbridge` also has a `run-agent` subcommand that launches a coding agent pre-configured with the Xcode MCP tools (`xcrun mcpbridge run-agent claude`, `--dry-run` to print the resolved command, `--no-xcode-tools` to leave the tools out), and `xcrun mcpbridge run-agent skills` inspects and exports the Xcode-provided skills.

## Headless mode 🆕

**Xcode 27** adds `xcrun mcp-server`, a preview of an MCP server that runs without an open Xcode workspace, and that can grant code-signed agents access to a directory tree for a longer period instead of asking every time. Apple flags it as an early preview: some commands may not work in every configuration, and some settings or permissions may need an Xcode relaunch or a reboot to take effect.

```bash
sudo xcrun mcp-server enable
```

| Command | Description |
|---------|-------------|
| `start` / `stop` | Launch or terminate the server (no-op if already in that state) |
| `open <paths>` | Launch if needed, then open workspaces/projects |
| `enable` / `disable` | Turn headless mode on/off (sudo) |
| `status` | Report permissions and, when running, the open workspaces. `--format text\|json` |
| `approve <id>` | Approve a pending agent or folder request (sudo). `--always` (signed agents and folders only) or `--for-24-hours` |
| `allow-folder <path>` | Permit workspaces under a folder without waiting for a request (sudo). `--always` or `--for-24-hours` |
| `deny <id>` | Deny a pending request, permitted agent, or permitted folder (sudo); denying an agent also stops the server |
| `clear-permissions` | Remove all granted agent and folder permissions (sudo) |

Request and permission ids come from `mcp-server status`. For unattended environments, `sudo xcrun mcp-server enable --unsafe-always-allow-all-agents` approves every agent upfront — Apple does not recommend it for at-desk use.

### What actually runs

`xcrun mcp-server` is only a launcher. The server itself is `XcodeService.app`, shipped inside the toolchain at `Xcode.app/Contents/Developer/Applications/XcodeService.app` with bundle identifier `com.apple.dt.mcp-server` and `LSUIElement`, so it has no Dock icon and no menu bar. It is started as a RunningBoard-managed application job — `launchctl print gui/$(id -u)/application.com.apple.dt.mcp-server.<n>.<n>` shows the job with `managed_by = com.apple.runningboard`. It is the same Xcode engine, not a separate reimplementation, and it can attach a UI later, so headless is a mode rather than a different product.

### Permissions

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

### Tool surface in headless mode

Headless mode does not expose the same tools as an Xcode window. [tools-headless.json](tools-headless.json) has the full headless schema; the differences from the windowed server are:

| | Tools |
|---|---|
| **Headless only** | [`XcodeListWorkspaces`](#xcodelistworkspaces-), [`XcodeOpenWorkspace`](#xcodeopenworkspace-), [`XcodeCloseWorkspace`](#xcodecloseworkspace-), [`XcodeNewProject`](#xcodenewproject-) |
| **Windowed only** | [`XcodeListWindows`](#xcodelistwindows), [`XcodeGetCurrentFile`](#xcodegetcurrentfile), [`XcodeListNavigatorIssues`](#xcodelistnavigatorissues) |

The tools that only make sense with a UI — the window list, the file the user is looking at, the issue navigator — are gone, and the tools for driving the workspace set yourself take their place.

Every other tool that took a `tabIdentifier` takes a **`workspaceIdentifier`** instead: *"Identifies the target workspace directly (used in headless mode): its workspace identifier (e.g. workspace1) or its absolute path."* It accepts either the identifier returned by `XcodeOpenWorkspace`/`XcodeListWorkspaces` (in practice something like `workspace-LKfjPJCMBL`) or the absolute path of the project. Prompts, skills, and scripts that hardcode `tabIdentifier` need updating for headless mode.

[`DocumentationSearch`](#documentationsearch-), which is hidden from `tools/list` in the windowed server, is listed normally in headless mode.

## Schema

[tools.json](tools.json) contains the full MCP tool definitions (name, title, description, input/output schemas) generated directly from `xcrun mcpbridge` against a running Xcode. [tools-headless.json](tools-headless.json) is the same listing captured from [headless mode](#headless-mode-) — 54 tools instead of 53, see [Tool surface in headless mode](#tool-surface-in-headless-mode) for the differences. [tools-26.5.json](tools-26.5.json) is the same listing from the current release, **Xcode 26.5** (21 tools), kept as the baseline for [What's new in Xcode 27](#whats-new-in-xcode-27).

The tool sections below document the windowed server; in headless mode read `tabIdentifier` as `workspaceIdentifier`.

## What's new in Xcode 27

Everything below compares **Xcode 27 beta 5** against the current release, **Xcode 26.5** — 21 tools → 53 windowed, 54 headless. Both schemas were captured from `tools/list`: [tools-26.5.json](tools-26.5.json) and [tools.json](tools.json). 🆕 in the sections below marks a tool that doesn't exist in Xcode 26.5.

### Server

- **Added:** `xcrun mcp-server` — headless MCP server that runs without an open workspace, plus durable per-agent/per-folder permissions; see [Headless mode](#headless-mode-)
- **Changed:** `mcpbridge` connects to the `xcode-select` Xcode by default (`MCP_XCODE_PID`/`MCP_XCODE_SESSION_ID` to override), and reaches the headless `XcodeService.app` when headless mode is on; it also gained the `run-agent` subcommand
- **Changed:** `tabIdentifier` is no longer required on any tool — omit it when only one workspace tab is open. In headless mode it becomes `workspaceIdentifier` and takes a workspace identifier or an absolute path

### Added tools

- **Workspace:** [`XcodeListSchemes`](#xcodelistschemes-), [`XcodeSwitchScheme`](#xcodeswitchscheme-), [`XcodeListRunDestinations`](#xcodelistrundestinations-), [`XcodeSwitchRunDestination`](#xcodeswitchrundestination-) — plus headless-only [`XcodeListWorkspaces`](#xcodelistworkspaces-), [`XcodeOpenWorkspace`](#xcodeopenworkspace-), [`XcodeCloseWorkspace`](#xcodecloseworkspace-)
- **Project configuration:** [`XcodeListTargets`](#xcodelisttargets-), [`XcodeListTemplates`](#xcodelisttemplates-), [`XcodeNewTarget`](#xcodenewtarget-), [`AddEntitlement`](#addentitlement-), [`AddInfoPlist`](#addinfoplist-), [`GetTargetBuildSettings`](#gettargetbuildsettings-), [`UpdateTargetBuildSetting`](#updatetargetbuildsetting-), [`GetFileCompilerFlags`](#getfilecompilerflags-), [`UpdateFileCompilerFlags`](#updatefilecompilerflags-) — plus headless-only [`XcodeNewProject`](#xcodenewproject-)
- **Run & debug:** [`RunProject`](#runproject-), [`StopProject`](#stopproject-), [`GetConsoleOutput`](#getconsoleoutput-), [`InvokeDebuggerCommand`](#invokedebuggercommand-)
- **Testing:** [`XcodeListTestPlans`](#xcodelisttestplans-), [`XcodeSwitchTestPlan`](#xcodeswitchtestplan-) — inspect and change the active scheme's test plan, which all testing tools operate on
- **Device interaction:** [`DeviceInteractionStartSession`](#deviceinteractionstartsession-), [`DeviceInteractionStartWorkspaceSession`](#deviceinteractionstartworkspacesession-), [`DeviceInteractionInstallAndRun`](#deviceinteractioninstallandrun-), [`DeviceInteractionSynthesize`](#deviceinteractionsynthesize-), [`DeviceInteractionEndSession`](#deviceinteractionendsession-)
- **Crash & field performance:** [`GetTopCrashIssues`](#gettopcrashissues-), [`GetCrashIssueLogs`](#getcrashissuelogs-), [`GetTopFieldPerformanceIssues`](#gettopfieldperformanceissues-), [`GetFieldPerformanceIssueLogs`](#getfieldperformanceissuelogs-)
- **Localization:** [`StringCatalogRead`](#stringcatalogread-), [`StringCatalogContext`](#stringcatalogcontext-), [`StringCatalogEdit`](#stringcatalogedit-), [`LocalizationPlanner`](#localizationplanner-)

### Changed tools

- **Renamed:** `ExecuteSnippet` → [`RunCodeSnippet`](#runcodesnippet), which gained a required `purpose` parameter
- **Asset-gated:** [`DocumentationSearch`](#documentationsearch-) — its results gained a `kind` field. In 27 the tool is gated on the local `com.apple.MobileAsset.AppleDeveloperDocumentation` asset; earlier 27 betas didn't list it in the windowed server's `tools/list`. On beta 6 with the asset installed it's listed normally by both the windowed and headless servers
- **Fixed:** [`XcodeMV`](#xcodemv)'s `operation` is now a plain string enum (`move`/`copy`); in 26.5 it was declared as an object with a `rawValue` field
- [`BuildProject`](#buildproject): new `buildForTesting` parameter — also build test targets that a regular build would skip
- [`GetBuildLog`](#getbuildlog): `line` is no longer required on an issue — issues without a line number are now representable
- [`RunAllTests`](#runalltests) / [`RunSomeTests`](#runsometests): output adds `xcresultBundlePath` for `xcresulttool`/`xccov`
- [`RenderPreview`](#renderpreview): new `previewCanvasControlOverrides` (timeline, toggle, group item) and `previewLocalizationOverride` parameters; output adds `displayName`, `sourceLineNumber`, `renderedDestination`, `supportedCanvasControlOverrides`, and `supportedLocalizations`

## Table of Contents

- **[Workspace](#workspace)**
  - [XcodeListWindows](#xcodelistwindows)
  - [XcodeListWorkspaces](#xcodelistworkspaces-) 🆕
  - [XcodeOpenWorkspace](#xcodeopenworkspace-) 🆕
  - [XcodeCloseWorkspace](#xcodecloseworkspace-) 🆕
  - [XcodeGetCurrentFile](#xcodegetcurrentfile)
  - [XcodeListSchemes](#xcodelistschemes-) 🆕
  - [XcodeSwitchScheme](#xcodeswitchscheme-) 🆕
  - [XcodeListRunDestinations](#xcodelistrundestinations-) 🆕
  - [XcodeSwitchRunDestination](#xcodeswitchrundestination-) 🆕
- **[File Operations](#file-operations)**
  - [XcodeLS](#xcodels)
  - [XcodeGlob](#xcodeglob)
  - [XcodeGrep](#xcodegrep)
  - [XcodeRead](#xcoderead)
  - [XcodeWrite](#xcodewrite)
  - [XcodeUpdate](#xcodeupdate)
  - [XcodeMakeDir](#xcodemakedir)
  - [XcodeMV](#xcodemv)
  - [XcodeRM](#xcoderm)
- **[Project Configuration](#project-configuration-)** 🆕
  - [XcodeListTargets](#xcodelisttargets-) 🆕
  - [XcodeListTemplates](#xcodelisttemplates-) 🆕
  - [XcodeNewProject](#xcodenewproject-) 🆕
  - [XcodeNewTarget](#xcodenewtarget-) 🆕
  - [AddEntitlement](#addentitlement-) 🆕
  - [AddInfoPlist](#addinfoplist-) 🆕
  - [GetTargetBuildSettings](#gettargetbuildsettings-) 🆕
  - [UpdateTargetBuildSetting](#updatetargetbuildsetting-) 🆕
  - [GetFileCompilerFlags](#getfilecompilerflags-) 🆕
  - [UpdateFileCompilerFlags](#updatefilecompilerflags-) 🆕
- **[Build & Run](#build--run)**
  - [BuildProject](#buildproject)
  - [GetBuildLog](#getbuildlog)
  - [RunCodeSnippet](#runcodesnippet) (renamed from `ExecuteSnippet`)
  - [RunProject](#runproject-) 🆕
  - [StopProject](#stopproject-) 🆕
  - [GetConsoleOutput](#getconsoleoutput-) 🆕
  - [InvokeDebuggerCommand](#invokedebuggercommand-) 🆕
- **[Testing](#testing)**
  - [XcodeListTestPlans](#xcodelisttestplans-) 🆕
  - [XcodeSwitchTestPlan](#xcodeswitchtestplan-) 🆕
  - [GetTestList](#gettestlist)
  - [RunAllTests](#runalltests)
  - [RunSomeTests](#runsometests)
- **[Diagnostics](#diagnostics)**
  - [XcodeRefreshCodeIssuesInFile](#xcoderefreshcodeissuesinfile)
  - [XcodeListNavigatorIssues](#xcodelistnavigatorissues)
- **[Device Interaction](#device-interaction-)** 🆕
  - [DeviceInteractionStartSession](#deviceinteractionstartsession-) 🆕
  - [DeviceInteractionStartWorkspaceSession](#deviceinteractionstartworkspacesession-) 🆕
  - [DeviceInteractionInstallAndRun](#deviceinteractioninstallandrun-) 🆕
  - [DeviceInteractionSynthesize](#deviceinteractionsynthesize-) 🆕
  - [DeviceInteractionEndSession](#deviceinteractionendsession-) 🆕
- **[Crash & Performance Reports](#crash--performance-reports-)** 🆕
  - [GetTopCrashIssues](#gettopcrashissues-) 🆕
  - [GetCrashIssueLogs](#getcrashissuelogs-) 🆕
  - [GetTopFieldPerformanceIssues](#gettopfieldperformanceissues-) 🆕
  - [GetFieldPerformanceIssueLogs](#getfieldperformanceissuelogs-) 🆕
- **[Localization](#localization-)** 🆕
  - [StringCatalogRead](#stringcatalogread-) 🆕
  - [StringCatalogContext](#stringcatalogcontext-) 🆕
  - [StringCatalogEdit](#stringcatalogedit-) 🆕
  - [LocalizationPlanner](#localizationplanner-) 🆕
- **[Preview](#preview)**
  - [RenderPreview](#renderpreview)
- **[Documentation](#documentation)**
  - [DocumentationSearch](#documentationsearch-) ⚠️

---

## Workspace

### XcodeListWindows

Lists current Xcode windows and their workspace information. Use this to obtain `tabIdentifier` values needed by all other tools. Not available in [headless mode](#headless-mode-) — use `XcodeListWorkspaces` there.

**Parameters:** None

**Example:**
```
XcodeListWindows()
```

### XcodeListWorkspaces 🆕

> Headless mode only.

Lists the workspaces currently open in the headless server, with the identifier and path of each. Use a returned `workspaceIdentifier` (or an absolute path) to target other tools at a specific workspace.

**Parameters:** None

**Example:**
```
XcodeListWorkspaces()
```

### XcodeOpenWorkspace 🆕

> Headless mode only.

Opens a workspace or project at the given path and returns its `workspaceIdentifier`, along with `workspacePath`, `activeScheme`, and `activeRunDestination`. Opening a project also grants its enclosing folder a permission entry — see [Permissions](#permissions).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Absolute path to the `.xcworkspace` or `.xcodeproj` to open |

**Example:**
```
XcodeOpenWorkspace(path: "/Users/username/Developer/MyApp/MyApp.xcodeproj")
```

### XcodeCloseWorkspace 🆕

> Headless mode only.

Closes a workspace previously opened with `XcodeOpenWorkspace`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspaceIdentifier` | string | Yes | Identifier returned by `XcodeOpenWorkspace` or `XcodeListWorkspaces` |

**Example:**
```
XcodeCloseWorkspace(workspaceIdentifier: "workspace-LKfjPJCMBL")
```

### XcodeGetCurrentFile

Gets information about the currently active file in the Xcode editor, including file path, content, and selection. Returns content in `cat -n` format. Not available in [headless mode](#headless-mode-), which has no editor.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `includeContent` | boolean | No | Include file content in the response |
| `includeSelection` | boolean | No | Include current selection information |
| `offset` | integer | No | Line number to start reading from |
| `limit` | integer | No | Number of lines to read (default: up to 600) |

**Example:**
```
XcodeGetCurrentFile(tabIdentifier: "...", includeSelection: true)
```

### XcodeListSchemes 🆕

Lists all schemes in the workspace and identifies the active one, including sharing status and container project. Inline results are capped at 100 (active scheme first); the full list is written to `fullSchemeListPath`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |

**Example:**
```
XcodeListSchemes(tabIdentifier: "...")
```

### XcodeSwitchScheme 🆕

Changes the active scheme. Use `XcodeListSchemes` to discover scheme names — pass the disambiguated name when multiple schemes share a name. May also adjust the active run destination automatically.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `schemeName` | string | Yes | Name (or disambiguated name) of the scheme to activate |

**Example:**
```
XcodeSwitchScheme(tabIdentifier: "...", schemeName: "MyApp")
```

### XcodeListRunDestinations 🆕

Lists run destinations for the active scheme, grouped like the Xcode picker (Devices, Simulators, Build, Incompatible, etc.) and identifies the active one. Inline results are capped at 40 (active destination first, "Incompatible" omitted by default); the full list is written to `fullRunDestinationListPath`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `includeIncompatible` | boolean | No | Include "Incompatible" destinations inline. Default: `false` |

**Example:**
```
XcodeListRunDestinations(tabIdentifier: "...")
```

### XcodeSwitchRunDestination 🆕

Changes the active run destination for the active scheme (the scheme itself is left unchanged). Pass the destination's `displayTitle`, sourced from `XcodeListRunDestinations`, `XcodeSwitchScheme`, or this tool's own output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `displayTitle` | string | Yes | Destination's disambiguated display title, as shown in the Xcode picker |

**Example:**
```
XcodeSwitchRunDestination(tabIdentifier: "...", displayTitle: "iPhone 17 Pro")
```

---

## File Operations

### XcodeLS

Lists files and directories in the Xcode project structure at a given path. Operates on the project navigator hierarchy, not the filesystem.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `path` | string | Yes | Project path to browse (e.g., `ProjectName/Sources/`) |
| `recursive` | boolean | No | List all files recursively (truncated at 100 lines). Default: `true` |
| `ignore` | string[] | No | Patterns to skip |

**Example:**
```
XcodeLS(tabIdentifier: "...", path: "MyApp/Sources/")
```

### XcodeGlob

Finds files in the Xcode project matching wildcard patterns. Supports `*`, `**`, `?`, `[abc]`, and `{swift,m}` syntax.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `pattern` | string | No | Glob pattern (e.g., `**/*.swift`). Defaults to `**/*` |
| `path` | string | No | Directory to search in (defaults to project root) |

**Example:**
```
XcodeGlob(tabIdentifier: "...", pattern: "**/*.swift")
```

### XcodeGrep

Searches file contents using regex patterns within the Xcode project structure.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `pattern` | string | Yes | Regex pattern to search for |
| `path` | string | No | File or directory to search in (defaults to root) |
| `glob` | string | No | Only search files matching this glob |
| `type` | string | No | File type shortcut (`swift`, `js`, `py`, etc.) |
| `outputMode` | string | No | `content`, `filesWithMatches` (default), or `count` |
| `ignoreCase` | boolean | No | Case-insensitive matching |
| `multiline` | boolean | No | Allow patterns to span multiple lines |
| `showLineNumbers` | boolean | No | Show line numbers (content mode only) |
| `linesBefore` | integer | No | Context lines before each match |
| `linesAfter` | integer | No | Context lines after each match |
| `linesContext` | integer | No | Context lines before and after each match |
| `headLimit` | integer | No | Stop after N results |

**Example:**
```
XcodeGrep(
  tabIdentifier: "...",
  pattern: "func viewDidLoad",
  type: "swift",
  outputMode: "content",
  linesAfter: 5
)
```

### XcodeRead

Reads file contents with line numbers (`cat -n` format). Supports offset/limit for large files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path (e.g., `ProjectName/Sources/MyFile.swift`) |
| `offset` | integer | No | Line number to start reading from |
| `limit` | integer | No | Number of lines to read (default: up to 600) |

**Example:**
```
XcodeRead(tabIdentifier: "...", filePath: "MyApp/Sources/ContentView.swift")
```

### XcodeWrite

Creates or overwrites files in the Xcode project. Automatically adds new files to the project structure.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path |
| `content` | string | Yes | File content to write |

**Example:**
```
XcodeWrite(
  tabIdentifier: "...",
  filePath: "MyApp/Sources/NewFeature.swift",
  content: "import Foundation\n\nstruct NewFeature {\n}\n"
)
```

### XcodeUpdate

Edits files by finding and replacing text. Operates on project structure paths.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path |
| `oldString` | string | Yes | Text to find |
| `newString` | string | Yes | Replacement text (must differ from `oldString`) |
| `replaceAll` | boolean | No | Replace all occurrences. Default: `false` |

**Example:**
```
XcodeUpdate(
  tabIdentifier: "...",
  filePath: "MyApp/Sources/ContentView.swift",
  oldString: "Hello, World!",
  newString: "Hello, SwiftUI!"
)
```

### XcodeMakeDir

Creates directories and groups in the Xcode project navigator.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `directoryPath` | string | Yes | Project-relative path for the new directory |

**Example:**
```
XcodeMakeDir(tabIdentifier: "...", directoryPath: "MyApp/Sources/ViewModels")
```

### XcodeMV

Moves, copies, or renames files and directories in the project navigator.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `sourcePath` | string | Yes | Source path in project navigator |
| `destinationPath` | string | Yes | Destination path or new name |
| `operation` | string | No | `move` or `copy` |
| `overwriteExisting` | boolean | No | Overwrite files at destination |

**Example:**
```
XcodeMV(
  tabIdentifier: "...",
  sourcePath: "MyApp/Sources/OldName.swift",
  destinationPath: "MyApp/Sources/NewName.swift"
)
```

### XcodeRM

Removes files and directories from the Xcode project. Optionally deletes underlying filesystem files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `path` | string | Yes | Project path to remove |
| `recursive` | boolean | No | Remove directories and contents recursively |
| `deleteFiles` | boolean | No | Also move files to Trash. Default: `true` |

**Example:**
```
XcodeRM(tabIdentifier: "...", path: "MyApp/Sources/Deprecated.swift")
```

---

## Project Configuration 🆕

### XcodeListTargets 🆕

Lists targets in the workspace, optionally scoped to one project. Each entry carries the target name, containing project, product type, and role flags (`isTestTarget`, `supportsHostingTests`, `isAppExtension`, `isAggregate`). Hidden synthetic blueprints and Swift package products are excluded. Inline results are capped at 100; the full list is written to `fullTargetListPath` in grep-friendly format (`TARGET_NAME`, `CONTAINING_PROJECT`, `PRODUCT_TYPE_IDENTIFIER`, ...). Pass the returned `containingProjectPath` back as `projectPath` to other target-aware tools.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `projectPath` | string | No | Restrict the listing to one `.xcodeproj` (with or without the suffix) |
| `productTypeFilter` | string[] | No | Product-type identifiers, full or suffixed (e.g. `application`, `bundle.unit-test`). Any non-empty filter excludes aggregate targets |

**Example:**
```
XcodeListTargets(tabIdentifier: "...", productTypeFilter: ["application"])
```

### XcodeListTemplates 🆕

Lists the target templates available in this Xcode install, with the option schema for each — the source of `templateIdentifier` and option keys for `XcodeNewTarget`. The unfiltered listing is large (~200 templates) and returns empty `options` for each entry; always pass at least one filter to get full options. Inline results are capped at 100; the complete list is written to `fullTemplateListPath`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `kind` | string | No | Template kind: `target` (default), or `project` in [headless mode](#headless-mode-) to feed `XcodeNewProject` |
| `platformFilter` | string[] | No | Platform identifiers or names (e.g. `ios`, `macos`). Multi-platform and platform-generic templates are always included |
| `categoryFilter` | string[] | No | Substrings matched against the category (e.g. `Application`, `Framework & Library`) |
| `nameFilter` | string | No | Substring matched against the template name (e.g. `Widget`) |
| `templateIdentifier` | string | No | Exact identifier — returns just that template with its options |

**Example:**
```
XcodeListTemplates(platformFilter: ["ios"], categoryFilter: ["Framework & Library"])
```

### XcodeNewProject 🆕

> Headless mode only.

Creates a new Xcode project from a template and writes it to disk in a subdirectory of `destinationPath` named after `productName`. Discover `templateIdentifier` values and their options with `XcodeListTemplates(kind: "project")`. Open the result with `XcodeOpenWorkspace`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `templateIdentifier` | string | Yes | Template to instantiate (e.g. `com.apple.dt.unit.storyboardApplication`) |
| `productName` | string | Yes | Product name — becomes the project filename and default target name |
| `destinationPath` | string | Yes | Directory the project is created in |
| `options` | object | No | Template-specific options from `XcodeListTemplates`. All values are strings; checkboxes take `true`/`false`, `YES`/`NO`, or `1`/`0`; popups must use a value from `possibleValues`. Do **not** pass `productName` or `organizationIdentifier` here |
| `organizationIdentifier` | string | No | Bundle identifier prefix (e.g. `com.example`) |
| `teamIdentifier` | string | No | Development team ID for code signing |

**Example:**
```
XcodeNewProject(templateIdentifier: "com.apple.dt.unit.multiplatformApp", productName: "MyApp", destinationPath: "/Users/username/Developer", options: ["languageChoice": "SwiftUI"])
```

### XcodeNewTarget 🆕

Adds a target to a project from a template. Discover `templateIdentifier` values and their options with `XcodeListTemplates`. Some templates derive a different target name from `productName` (e.g. Widget Extension appends `Extension`) — use the returned `targetName` for follow-up calls. If "Autocreate schemes" is on, a scheme may be created and activated; the result reports `activeSchemeName`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `templateIdentifier` | string | Yes | Template to instantiate (e.g. `com.apple.dt.unit.iosFramework`) |
| `productName` | string | Yes | Product name for the new target; must be unique within the destination project |
| `options` | object | No | Template options keyed by option identifier, values as strings. `productName`, `organizationIdentifier`, and `bundleIdentifierPrefix` are rejected here |
| `organizationIdentifier` | string | No | Bundle identifier prefix; defaults to the workspace's, or to the host app's when `embedInAppNamed` is set |
| `embedInAppNamed` | string | No | Existing app target to embed into (extensions, widgets, intents). Must live in the same project |
| `projectPath` | string | No | Owning `.xcodeproj`; required only in multi-project workspaces when `embedInAppNamed` doesn't disambiguate |

**Example:**
```
XcodeNewTarget(
  tabIdentifier: "...",
  templateIdentifier: "com.apple.dt.unit.iosFramework",
  productName: "MyFeature",
  options: { "languageChoice": "Swift" }
)
```

### AddEntitlement 🆕

Adds an entitlement to the project's entitlements file. Reserve this for restricted system capabilities — App Groups, Push Notifications, iCloud, paid transactions, privileged IPC, etc. Not for standard frameworks (SwiftUI, MapKit, CoreLocation...) or Info.plist privacy strings — use `AddInfoPlist` for those.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetName` | string | Yes | Target to add the entitlement to |
| `entitlementKey` | string | Yes | Entitlement key |
| `entitlementValueType` | string | Yes | `bool`, `string`, `int`, `stringArray`, or `dictionary` |
| `entitlementValue` | string | No | Value for `bool`/`string`/`int` types (`"true"`/`"false"` for bool) |
| `entitlementValueItems` | string[] | No | Values for `stringArray` type |
| `entitlementDictionaryItems` | string | No | JSON-encoded dictionary for `dictionary` type |
| `projectPath` | string | No | Path to the owning `.xcodeproj`; only needed when the target name is ambiguous |

**Example:**
```
AddEntitlement(
  tabIdentifier: "...",
  targetName: "MyApp",
  entitlementKey: "com.apple.security.application-groups",
  entitlementValueType: "stringArray",
  entitlementValueItems: ["group.com.example.myapp"]
)
```

### AddInfoPlist 🆕

Adds or updates an Info.plist key — privacy usage descriptions, App Transport Security, supported orientations, URL schemes, background modes, bundle metadata, etc. Not for entitlements — use `AddEntitlement` for restricted system capabilities.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetName` | string | Yes | Target to add the key to |
| `infoPlistKey` | string | Yes | Info.plist key (e.g., `NSCameraUsageDescription`) |
| `infoPlistValueType` | string | Yes | `bool`, `string`, `int`, `stringArray`, or `dictionaryArray` |
| `infoPlistValue` | string | No | Value for `bool`/`string`/`int` types (`"true"`/`"false"` for bool) |
| `infoPlistValueItems` | string[] | No | Values for `stringArray` type |
| `infoPlistDictionaryItems` | string | No | JSON-encoded array of dictionaries for `dictionaryArray` type |
| `projectPath` | string | No | Path to the owning `.xcodeproj`; only needed when the target name is ambiguous |

**Example:**
```
AddInfoPlist(
  tabIdentifier: "...",
  targetName: "MyApp",
  infoPlistKey: "NSCameraUsageDescription",
  infoPlistValueType: "string",
  infoPlistValue: "Used to scan documents"
)
```

### GetTargetBuildSettings 🆕

Gets all build settings for an Xcode target. Use this rather than reading `project.pbxproj` directly.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetName` | string | Yes | Target name |
| `projectPath` | string | No | Path to the owning `.xcodeproj`; only needed when the target name is ambiguous |

**Example:**
```
GetTargetBuildSettings(tabIdentifier: "...", targetName: "MyApp")
```

### UpdateTargetBuildSetting 🆕

Updates, appends to, or deletes a build setting on a target. Omit `buildSettingValue` to delete the setting. Use this rather than modifying `project.pbxproj` directly.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetName` | string | Yes | Target name |
| `buildSettingName` | string | Yes | Build setting name |
| `buildSettingValue` | string | No | New value (omit to delete the setting; don't convert `"NO"` to `"false"`) |
| `appendValue` | boolean | No | Append to the existing value instead of replacing it |
| `projectPath` | string | No | Path to the owning `.xcodeproj`; only needed when the target name is ambiguous |

**Example:**
```
UpdateTargetBuildSetting(
  tabIdentifier: "...",
  targetName: "MyApp",
  buildSettingName: "SWIFT_VERSION",
  buildSettingValue: "6.0"
)
```

### GetFileCompilerFlags 🆕

Gets the per-file compiler flags for a source file in a target — the value shown in the Compiler Flags column of Target > Build Phases > Compile Sources. Returns an empty string when none are set. Note: flags on `.swift` files often don't affect builds, since Swift compiles per-module — prefer `OTHER_SWIFT_FLAGS` at the target level.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetName` | string | Yes | Target whose build phase contains the file |
| `filePath` | string | Yes | Project-relative path to the source file |
| `projectPath` | string | No | Path to the owning `.xcodeproj`; only needed when the target name is ambiguous |

**Example:**
```
GetFileCompilerFlags(tabIdentifier: "...", targetName: "MyApp", filePath: "MyApp/Sources/Legacy.m")
```

### UpdateFileCompilerFlags 🆕

Updates, appends to, or deletes the per-file compiler flags for a source file. Use sparingly — prefer `UpdateTargetBuildSetting` unless a flag truly must apply to a single file (e.g. incrementally adopting `-fbounds-safety`). Note: flags on `.swift` files typically don't affect builds — prefer `OTHER_SWIFT_FLAGS` at the target level.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetName` | string | Yes | Target whose build phase contains the file |
| `filePath` | string | Yes | Project-relative path to the source file |
| `compilerFlags` | string | No | Space-separated flags (e.g. `"-DFOO=1 -Wno-unused-variable"`); omit to delete all |
| `appendValue` | boolean | No | Append to existing flags (space-separated) instead of replacing |
| `projectPath` | string | No | Path to the owning `.xcodeproj`; only needed when the target name is ambiguous |

**Example:**
```
UpdateFileCompilerFlags(
  tabIdentifier: "...",
  targetName: "MyApp",
  filePath: "MyApp/Sources/Legacy.m",
  compilerFlags: "-fno-objc-arc"
)
```

---

## Build & Run

### BuildProject

Builds the Xcode project using the active scheme and waits for completion. The result carries the build outcome, any errors, and `fullLogPath` — the complete build log with command lines and task output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `buildForTesting` | boolean | No | 🆕 Also build test targets that a regular build would skip |

**Example:**
```
BuildProject(buildForTesting: true)
```

### GetBuildLog

Retrieves build log entries from the current or most recent build. Filter by severity, file pattern, or message regex.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `severity` | string | No | Minimum severity: `error` (default), `warning`, or `remark` |
| `pattern` | string | No | Regex to filter by message, task description, command line, or console output |
| `glob` | string | No | Glob to filter by file path or task location |

**Example:**
```
GetBuildLog(tabIdentifier: "...", severity: "warning")
```

### RunCodeSnippet

> Renamed from `ExecuteSnippet` in Xcode 27, and gained a required `purpose` parameter.

Builds and runs a code snippet in the context of a specific source file and waits for the result. The snippet has access to all declarations in that file, including `fileprivate` ones. Output comes from `print` statements. Only works with source files in targets that build apps, frameworks, libraries, or CLI executables.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `codeSnippet` | string | Yes | Swift code to execute |
| `sourceFilePath` | string | Yes | Project-relative path to the context file |
| `purpose` | string | Yes | Short human-readable description of why the snippet is being run (avoid the word "test" — this isn't related to testing) |
| `timeout` | integer | No | Max wait time in seconds. Default: 600 |

**Example:**
```
RunCodeSnippet(
  tabIdentifier: "...",
  sourceFilePath: "MyApp/Sources/Models/User.swift",
  codeSnippet: "let user = User(name: \"Test\")\nprint(user)",
  purpose: "Inspect the default User description"
)
```

### RunProject 🆕

Builds and runs the active scheme — equivalent to pressing Run (Cmd+R). Returns once the app has launched and is running.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `attachDebugger` | boolean | No | Attach the debugger to the launched process. Default: `false` |

> Use `InvokeDebuggerCommand` to debug (with `attachDebugger: true`), `GetConsoleOutput` to read logs, and `StopProject` to stop the app when finished.

**Example:**
```
RunProject(tabIdentifier: "...", attachDebugger: true)
```

### StopProject 🆕

Stops the currently running app — equivalent to pressing Stop (Cmd+.). Reports that there's nothing to stop if no app is running.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |

**Example:**
```
StopProject(tabIdentifier: "...")
```

### GetConsoleOutput 🆕

Retrieves stdout, stderr, and OSLog output from a running or completed app launch session, with regex, severity, and context-line filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `launchSessionReference` | string | No | Launch session to read from. Defaults to the current/most recent session |
| `outputType` | string | No | `stdio`, `oslog`, or `all` (default) |
| `oslogSeverity` | string[] | No | Filter OSLog by severity: `error`, `fault`, `info`, `debug`, `default` |
| `pattern` | string | No | Regex to filter stdout/stderr text and OSLog messages |
| `contextLines` | integer | No | Context lines around pattern matches (like `grep -C`). Default: `0` |
| `includeMetadata` | boolean | No | Include OSLog metadata (subsystem, category, pid, tid, sender). Default: `false` |
| `tailLimit` | integer | No | Max lines to return from the end of the output. Default: `500` |

**Example:**
```
GetConsoleOutput(tabIdentifier: "...", outputType: "oslog", oslogSeverity: ["error", "fault"])
```

### InvokeDebuggerCommand 🆕

Sends an lldb command to Xcode's active debugging session and returns the output. The process must already be running with the debugger attached (e.g. via `RunProject(attachDebugger: true)`). The command runs in the same lldb session as Xcode's debug console. Start a debug session with `process status` unless you already know whether the process is stopped — expressions and other commands require a stopped process.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `command` | string | Yes | lldb command (e.g. `bt`, `po self`, `breakpoint set -n viewDidLoad`, `continue`, `thread step-over`, `frame variable`) |
| `timeout` | integer | No | Max seconds to wait. Default: `30` (increase for commands that resume execution, like `continue`) |

**Example:**
```
InvokeDebuggerCommand(tabIdentifier: "...", command: "po self.viewModel")
```

---

## Testing

### XcodeListTestPlans 🆕

Lists the test plans of the active scheme and identifies the active one. All testing tools (`GetTestList`, `RunAllTests`, `RunSomeTests`) and build-for-testing operate on the active plan. If the scheme hasn't been upgraded to test plans, `usesTestPlans` is `false` and `testPlans` is empty. Inline results are capped at 100 (active plan first); the full list goes to `fullTestPlanListPath`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |

**Example:**
```
XcodeListTestPlans(tabIdentifier: "...")
```

### XcodeSwitchTestPlan 🆕

Changes the active test plan of the active scheme — the same persistent change as picking a plan in Xcode's test plan picker. Discover names with `XcodeListTestPlans`; when two plans share a name, pass the reported `path` (or an unambiguous trailing portion of it).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `testPlanName` | string | Yes | Plan name, or its path when the name is ambiguous |

**Example:**
```
XcodeSwitchTestPlan(tabIdentifier: "...", testPlanName: "UnitTests")
```

### GetTestList

Gets all available tests from the active scheme's active test plan. Results are limited to 100 tests. The complete list is written to `fullTestListPath` in grep-friendly format — use grep with keys like `TEST_TARGET`, `TEST_IDENTIFIER`, or `TEST_FILE_PATH` to find specific tests.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |

**Example:**
```
GetTestList(tabIdentifier: "...")
```

### RunAllTests

Runs every test in the active scheme's active test plan. Alongside the per-test results the output carries paths for anything truncated: `fullSummaryPath`, `fullConsoleLogsPath` (everything `print`/`NSLog` emitted during build and run), and 🆕 `xcresultBundlePath` — the `.xcresult` bundle for `xcresulttool`, or `xccov` when coverage is enabled.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |

**Example:**
```
RunAllTests(tabIdentifier: "...")
```

### RunSomeTests

Runs specific tests by target and identifier. Use `GetTestList` first to discover available test identifiers. Output matches [`RunAllTests`](#runalltests), including `xcresultBundlePath`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `tests` | array | Yes | Array of test specifiers (see below) |

Each test specifier object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `targetName` | string | Yes | Test target name |
| `testIdentifier` | string | Yes | Test identifier in XCTestIdentifier format |

**Example:**
```
RunSomeTests(
  tabIdentifier: "...",
  tests: [
    { "targetName": "MyAppTests", "testIdentifier": "MyAppTests/LoginTests/testValidLogin" }
  ]
)
```

---

## Diagnostics

### XcodeRefreshCodeIssuesInFile

Retrieves current compiler diagnostics (errors, warnings, notes) for a specific file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path |

**Example:**
```
XcodeRefreshCodeIssuesInFile(
  tabIdentifier: "...",
  filePath: "MyApp/Sources/ContentView.swift"
)
```

### XcodeListNavigatorIssues

Lists issues from Xcode's Issue Navigator, including build errors, package resolution problems, and workspace configuration issues. Not available in [headless mode](#headless-mode-), which has no navigator.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `severity` | string | No | Minimum severity: `error` (default), `warning`, or `remark` |
| `pattern` | string | No | Regex to filter by message |
| `glob` | string | No | Glob to filter by file path |

**Example:**
```
XcodeListNavigatorIssues(tabIdentifier: "...", severity: "warning")
```

---

## Device Interaction 🆕

Tools for driving a simulator or physical device — booting it, installing and launching the app, and synthesizing UI events. Sessions are expensive to keep open: start one early (in parallel with other work) and always close it with `DeviceInteractionEndSession` when done.

### DeviceInteractionStartSession 🆕

Prepares a runtime for device interaction **without** a workspace — finds and, if necessary, boots the target device. Call this as early as possible if device interaction will be needed. This session cannot build or install the project; use `DeviceInteractionStartWorkspaceSession` for that.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sessionIdentifier` | string | Yes | Unique, human-friendly session name in Title Case (e.g. "Verify Login Flow"), used in logs and UI |
| `deviceIdentifier` | string | Yes | UUID/ECID/name/OS version/type to match against — the best candidate is selected |

**Example:**
```
DeviceInteractionStartSession(deviceIdentifier: "iPhone 17 Pro", sessionIdentifier: "Verify Login Flow")
```

### DeviceInteractionStartWorkspaceSession 🆕

Prepares a runtime for device interaction **with** a workspace. Same as `DeviceInteractionStartSession`, but bound to the workspace: it only offers devices the active scheme can run on, and enables installing & running the project via `DeviceInteractionInstallAndRun`. Do not call it if the app doesn't need to be built and installed on a device.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `sessionIdentifier` | string | Yes | Unique, human-friendly session name in Title Case (e.g. "Verify Login Flow"), used in logs and UI |
| `deviceIdentifier` | string | No | UUID/ECID/name/OS version/type to match against — the best candidate is selected |

**Example:**
```
DeviceInteractionStartWorkspaceSession(sessionIdentifier: "Verify Login Flow")
```

### DeviceInteractionInstallAndRun 🆕

Builds, installs, and starts the app on the currently targeted device. Call again whenever you modify the project, change the target device, or lose the debug session and need fresh logs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `interactionSessionKey` | string | Yes | Session key from `DeviceInteractionStartWorkspaceSession` |
| `commandLineArguments` | string[] | No | Launch arguments; may include `$(inherited)` for scheme-provided arguments |
| `environmentVariables` | object | No | Launch environment variables; may include `$(inherited)` as a key for scheme-provided variables |

**Example:**
```
DeviceInteractionInstallAndRun(interactionSessionKey: "...")
```

### DeviceInteractionSynthesize 🆕

Synthesizes device events — tap, swipe, type, button press, orientation change — and captures the resulting screenshot and UI hierarchy. Always derive coordinates from the latest hierarchy dump; never guess positions from a screenshot alone.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `interactSessionKey` | string | Yes | Session key from `DeviceInteractionStartSession` or `DeviceInteractionStartWorkspaceSession` |
| `interactionCommand` | string | Yes | Interaction command to run (e.g. `t 100 200` to tap at that point) |
| `activationBundleId` | string | No | Bundle identifier of the app to activate before running the interaction |

**Example:**
```
DeviceInteractionSynthesize(interactSessionKey: "...", interactionCommand: "t 100 200")
```

### DeviceInteractionEndSession 🆕

Closes a session opened with `DeviceInteractionStartSession` or `DeviceInteractionStartWorkspaceSession`. Always call this once interaction is finished — keeping a session alive is expensive and affects the user-facing UI.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `interactionSessionKey` | string | Yes | Session key to close |

**Example:**
```
DeviceInteractionEndSession(interactionSessionKey: "...")
```

---

## Crash & Performance Reports 🆕

Tools for querying Apple's crash reporting and field performance data for a shipped app. `bundle_id` and `platform` auto-resolve from the active scheme/run destination when omitted.

### GetTopCrashIssues 🆕

Returns the top crash signatures for an app over the last 14 days, sorted by the number of unique devices affected. Use this to identify and prioritize the most impactful crashes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `bundle_id` | string | No | App bundle identifier (case-sensitive). Auto-resolved from the active scheme's target if omitted |
| `platform` | string | No | `iOS`, `macOS`, `watchOS`, `tvOS`, or `visionOS`. Auto-resolved from the active run destination if omitted |
| `app_version` | string | No | Filter to a specific version (e.g. `4.6`). Returns all versions if omitted |
| `is_beta` | boolean | No | TestFlight (`true`) or App Store (`false`) data. Both channels if omitted |
| `count` | integer | No | Number of signatures to return. Use `1` for "top crash" (singular). Default: `5` |

**Example:**
```
GetTopCrashIssues(tabIdentifier: "...", count: 1)
```

### GetCrashIssueLogs 🆕

Gets detailed crash logs, expert triage knowledge, and actionable recommendations for a specific crash signature. Use after `GetTopCrashIssues` to drill into a signature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `signature_name` | string | Yes | Human-readable crash signature name from `GetTopCrashIssues` |
| `bundle_id` | string | No | App bundle identifier (case-sensitive). Auto-resolved if omitted |
| `platform` | string | No | Platform to query. Auto-resolved if omitted |
| `app_version` | string | No | Filter to a specific version. Returns all versions if omitted |
| `is_beta` | boolean | No | TestFlight (`true`) or App Store (`false`) data. Both channels if omitted |

**Example:**
```
GetCrashIssueLogs(tabIdentifier: "...", signature_name: "SIGABRT in UIViewController.viewDidLoad")
```

### GetTopFieldPerformanceIssues 🆕

Analyzes app performance and identifies regressions across diagnostic types — app launches, hangs, disk writes, or energy usage — using Apple's field report data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `diagnostic_type` | string | Yes | `launches`, `hangs`, `diskwrites`, or `energy` |
| `bundle_id` | string | No | App bundle identifier (case-sensitive). Auto-resolved if omitted |
| `platform` | string | No | Platform to query (supported values depend on diagnostic type). Auto-resolved if omitted |
| `app_version` | string | No | App version (e.g. `4.6`). Lists available versions if omitted |
| `is_beta` | boolean | No | TestFlight (`true`) or App Store (`false`) data. Auto-detected from the version when possible |

**Example:**
```
GetTopFieldPerformanceIssues(tabIdentifier: "...", diagnostic_type: "hangs")
```

### GetFieldPerformanceIssueLogs 🆕

Gets detailed logs, performance data (stack traces, timeline data), and triage guidance for a specific field performance issue. Use after `GetTopFieldPerformanceIssues` to drill into a signature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `app_version` | string | Yes | App version (e.g. `13.14.0`) |
| `signature_name` | string | Yes | Human-readable signature name from `GetTopFieldPerformanceIssues` |
| `diagnostic_type` | string | Yes | `launches`, `hangs`, `diskwrites`, or `energy` |
| `bundle_id` | string | No | App bundle identifier (case-sensitive). Auto-resolved if omitted |
| `platform` | string | No | Platform to query. Auto-resolved if omitted |
| `is_beta` | boolean | No | TestFlight (`true`) or App Store (`false`) data. Auto-detected from the version when possible |

**Example:**
```
GetFieldPerformanceIssueLogs(
  tabIdentifier: "...",
  app_version: "13.14.0",
  signature_name: "Slow launch on iPhone 13",
  diagnostic_type: "launches"
)
```

---

## Localization 🆕

> **Note:** These tools require activating the corresponding `xcode-integration:translation` (for `StringCatalogContext`/`StringCatalogEdit`) or `xcode-integration:translation-coordinator` (for `StringCatalogRead`/`LocalizationPlanner`) skill before use.

### StringCatalogRead 🆕

Returns string keys grouped by translation state for a locale in a String Catalog.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Path to the String Catalog |
| `targetLocaleIdentifier` | string | Yes | Locale identifier to check translations for |
| `requestedState` | string | No | Translation state to retrieve keys for |
| `offset` | integer | No | Number of keys to skip before returning results |
| `keyLimit` | integer | No | Maximum number of keys to return |

**Example:**
```
StringCatalogRead(
  tabIdentifier: "...",
  filePath: "MyApp/Resources/Localizable.xcstrings",
  targetLocaleIdentifier: "de"
)
```

### StringCatalogContext 🆕

Returns context and the source-language value for a string key — the text (`sourceValues`) that needs to be translated.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Path to the String Catalog |
| `stringKey` | string | Yes | String key to get context for |
| `targetLocaleIdentifier` | string | Yes | Locale identifier to translate into |

**Example:**
```
StringCatalogContext(
  tabIdentifier: "...",
  filePath: "MyApp/Resources/Localizable.xcstrings",
  stringKey: "welcome_message",
  targetLocaleIdentifier: "de"
)
```

### StringCatalogEdit 🆕

Inserts a translation for a locale into a String Catalog — a simple string, a template with plural/format substitutions, a top-level plural/device/width variation structure, or a string set.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `filePath` | string | Yes | Path to the String Catalog |
| `stringKey` | string | Yes | String key to translate |
| `targetLocaleIdentifier` | string | Yes | Locale identifier to insert the translation for |
| `translation` | string | No | Simple translation for non-varied strings |
| `templateTranslation` | object | No | Template + substitutions (for strings varied by plural/format) |
| `variationTranslation` | object | No | Top-level plural/device/width variation structure |
| `stringSetTranslation` | string[] | No | Translated values for string sets |

**Example:**
```
StringCatalogEdit(
  tabIdentifier: "...",
  filePath: "MyApp/Resources/Localizable.xcstrings",
  stringKey: "welcome_message",
  targetLocaleIdentifier: "de",
  translation: "Willkommen"
)
```

### LocalizationPlanner 🆕

Ensures the project is in a state where translations can be added for a locale. Call this every time you're asked to add a language to the project, or to localize an entire project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `targetLocaleIdentifier` | string | Yes | Locale identifier to prepare the project for |

**Example:**
```
LocalizationPlanner(tabIdentifier: "...", targetLocaleIdentifier: "de")
```

---

## Preview

### RenderPreview

Builds and renders a SwiftUI preview, returning a snapshot of the resulting UI. The result identifies which preview was rendered via `displayName` and `sourceLineNumber`, matching the title and "Line N" subtitle in Xcode's canvas, and reports the actual `renderedDestination` (platform, device model, OS version), which may differ from the workspace's selected run destination. In the snapshot at `previewSnapshotPath`, areas of the framebuffer that fall outside the render destination's device screen are transparent.

The override parameters are discovery-driven: call the tool once, read `supportedLocalizations`, `supportedPreviewVariantOverrides`, and `supportedCanvasControlOverrides` from the result, then pass values from those back in.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | No | Workspace tab identifier |
| `sourceFilePath` | string | Yes | Project-relative path to the file containing the preview |
| `previewDefinitionIndexInFile` | integer | No | Zero-based index of the `#Preview` macro or `PreviewProvider` in the file. Default: `0` |
| `previewCanvasControlOverrides` | object | No | 🆕 Canvas controls to override: `timelineIndex` (timeline position for Widgets/Live Activities), `toggleState` (boolean toggle control), `groupItemIndex` (which item of a `#Preview(arguments:)` set). Only meaningful for the controls listed in `supportedCanvasControlOverrides` |
| `previewLocalizationOverride` | string | No | 🆕 Locale identifier to preview in (e.g. `"fr"`, `"ja"`), from `supportedLocalizations`. Don't call the tool in parallel when this is set |
| `previewVariantOverrides` | object | No | Variant group name → variant name, from `supportedPreviewVariantOverrides` (e.g. color scheme, dynamic type) |
| `timeout` | integer | No | Max wait time in seconds. Default: 120 |

**Example:**
```
RenderPreview(
  sourceFilePath: "MyApp/Sources/Views/ProfileView.swift",
  previewLocalizationOverride: "ja",
  previewCanvasControlOverrides: { timelineIndex: 2 }
)
```

---

## Documentation

### DocumentationSearch ⚠️

> **Status in Xcode 27:** gated on the local `com.apple.MobileAsset.AppleDeveloperDocumentation` asset (visible under Settings → Components → Downloads) — until it finishes downloading/indexing, the tool returns `Tool 'DocumentationSearch' is not enabled.` Earlier 27 betas also left it out of the windowed server's `tools/list`, so a standard MCP client couldn't discover it through normal enumeration, though it still worked when called directly by name. Verified on beta 6 with the asset installed: it's listed normally by both the windowed and headless servers, and calls return real results. Xcode's own built-in chat knows the tool by name independently of `tools/list` (via a `MCPTool_DocumentationSearch` flag in its system prompt template).

Searches Apple Developer Documentation using semantic matching. Useful for looking up APIs, frameworks, and usage patterns.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `frameworks` | string[] | No | Limit search to specific frameworks. Searches all if omitted |

**Example:**
```
DocumentationSearch(query: "URLSession background download")
```

## Author

Artem Novichkov, https://artemnovichkov.com
