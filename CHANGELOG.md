# Changelog

[README](README.md) · [Tool reference](docs/tools.md)

## What's new in Xcode 27

Everything below compares **Xcode 27** against the previous release, **Xcode 26.5**. Both schemas were captured from `tools/list`: [tools-26.5.json](tools-26.5.json) and [tools.json](tools.json).

### Server

- **Added:** `xcrun mcp-server` — headless MCP server that runs without an open workspace, plus durable per-agent/per-folder permissions; see [Headless mode](docs/headless.md#headless-mode)
- **Added:** `xcrun lldb-mcp` — a separate MCP server for LLDB; see [Agent tooling](docs/agent-tooling.md#agent-tooling)
- **Changed:** `mcpbridge` connects to the `xcode-select` Xcode by default (`MCP_XCODE_PID`/`MCP_XCODE_SESSION_ID` to override), and reaches the headless `Xcode Service.app` when headless mode is on
- **Changed:** `run-agent` (which 26.5 already had) gained the `skills` and `plugin` subcommands — export Xcode's skills, or materialize them as an agent plugin; see [Agent tooling](docs/agent-tooling.md#agent-tooling)
- **Changed:** `tabIdentifier` is no longer required on any tool — omit it when only one workspace tab is open. In headless mode it becomes `workspaceIdentifier` and takes a workspace identifier or an absolute path

### Added tools

- **Workspace:** [`XcodeListSchemes`](docs/tools.md#xcodelistschemes), [`XcodeSwitchScheme`](docs/tools.md#xcodeswitchscheme), [`XcodeListRunDestinations`](docs/tools.md#xcodelistrundestinations), [`XcodeSwitchRunDestination`](docs/tools.md#xcodeswitchrundestination), [`XcodeListWorkspaces`](docs/tools.md#xcodelistworkspaces), [`XcodeOpenWorkspace`](docs/tools.md#xcodeopenworkspace), [`XcodeCloseWorkspace`](docs/tools.md#xcodecloseworkspace)
- **Project configuration:** [`XcodeListTargets`](docs/tools.md#xcodelisttargets), [`XcodeListTemplates`](docs/tools.md#xcodelisttemplates), [`XcodeNewTarget`](docs/tools.md#xcodenewtarget), [`AddEntitlement`](docs/tools.md#addentitlement), [`AddInfoPlist`](docs/tools.md#addinfoplist), [`GetTargetBuildSettings`](docs/tools.md#gettargetbuildsettings), [`UpdateTargetBuildSetting`](docs/tools.md#updatetargetbuildsetting), [`GetFileCompilerFlags`](docs/tools.md#getfilecompilerflags), [`UpdateFileCompilerFlags`](docs/tools.md#updatefilecompilerflags), [`XcodeNewProject`](docs/tools.md#xcodenewproject)
- **Run & debug:** [`RunProject`](docs/tools.md#runproject), [`StopProject`](docs/tools.md#stopproject), [`GetConsoleOutput`](docs/tools.md#getconsoleoutput), [`InvokeDebuggerCommand`](docs/tools.md#invokedebuggercommand)
- **Testing:** [`XcodeListTestPlans`](docs/tools.md#xcodelisttestplans), [`XcodeSwitchTestPlan`](docs/tools.md#xcodeswitchtestplan) — inspect and change the active scheme's test plan, which all testing tools operate on
- **Device interaction:** [`DeviceInteractionStartSession`](docs/tools.md#deviceinteractionstartsession), [`DeviceInteractionStartWorkspaceSession`](docs/tools.md#deviceinteractionstartworkspacesession), [`DeviceInteractionInstallAndRun`](docs/tools.md#deviceinteractioninstallandrun), [`DeviceInteractionSynthesize`](docs/tools.md#deviceinteractionsynthesize), [`DeviceInteractionEndSession`](docs/tools.md#deviceinteractionendsession)
- **Crash & field performance:** [`GetTopCrashIssues`](docs/tools.md#gettopcrashissues), [`GetCrashIssueLogs`](docs/tools.md#getcrashissuelogs), [`GetTopFieldPerformanceIssues`](docs/tools.md#gettopfieldperformanceissues), [`GetFieldPerformanceIssueLogs`](docs/tools.md#getfieldperformanceissuelogs)
- **Localization:** [`StringCatalogRead`](docs/tools.md#stringcatalogread), [`StringCatalogContext`](docs/tools.md#stringcatalogcontext), [`StringCatalogEdit`](docs/tools.md#stringcatalogedit), [`LocalizationPlanner`](docs/tools.md#localizationplanner)

### Changed tools

- **Renamed:** `ExecuteSnippet` → [`RunCodeSnippet`](docs/tools.md#runcodesnippet), which gained a required `purpose` parameter
- **Asset-gated:** [`DocumentationSearch`](docs/tools.md#documentationsearch-) — its results gained a `kind` field. In 27 the tool is gated on the local `com.apple.MobileAsset.AppleDeveloperDocumentation` asset, and while the asset is missing the tool is absent from `tools/list` in both modes. With the asset installed it's listed normally by both servers
- **Fixed:** [`XcodeMV`](docs/tools.md#xcodemv)'s `operation` is now a plain string enum (`move`/`copy`); in 26.5 it was declared as an object with a `rawValue` field
- [`BuildProject`](docs/tools.md#buildproject): new `buildForTesting` parameter — also build test targets that a regular build would skip
- [`GetBuildLog`](docs/tools.md#getbuildlog): `line` is no longer required on an issue — issues without a line number are now representable
- [`RunAllTests`](docs/tools.md#runalltests) / [`RunSomeTests`](docs/tools.md#runsometests): output adds `xcresultBundlePath` for `xcresulttool`/`xccov`
- [`RenderPreview`](docs/tools.md#renderpreview): new `previewCanvasControlOverrides` (timeline, toggle, group item) and `previewLocalizationOverride` parameters; output adds `displayName`, `sourceLineNumber`, `renderedDestination`, `supportedCanvasControlOverrides`, and `supportedLocalizations`

## Xcode 27.2 RC

The main documentation reflects Xcode 27; this section lists what **Xcode 27.2 RC** (27B48, server 25463; beta 2 is 27B5028f/25447.1, beta 1 is 27B5019j/25434.2, 27 is 25317) changes on top of it. Captured from `tools/list` of both servers: [tools-27.2.json](tools-27.2.json) (windowed) and [tools-headless-27.2.json](tools-headless-27.2.json) (headless). Both change identically; the windowed/headless split is unchanged from 27.

- No tools added or removed
- [`RenderPreview`](docs/tools.md#renderpreview): new `preferredRenderDestination` parameter — pick the device or simulator to render on by `identifier`, `platformName`, `deviceModelName`, and/or `systemVersion`; falls back to the automatic destination with a message in `errors` when nothing matches. `renderedDestination` gains a required `identifier`
- [`RenderPreview`](docs/tools.md#renderpreview) *(RC, breaking)*: the discovery fields move into one `supportedOverrides` object — `supportedLocalizations` → `localizations`, `supportedPreviewVariantOverrides` → `previewVariants`, `supportedCanvasControlOverrides` → `canvasControls`, and the beta's `availableRenderDestinations` → `renderDestinations`. `previewSnapshotPath` becomes `snapshot.path`
- [`RenderPreview`](docs/tools.md#renderpreview) *(RC)*: new `displayMode` parameter — `static` (default) or `interactive`, from `supportedOverrides.displayModes` — and `snapshotDelay`, seconds an interactive preview runs before the snapshot (≥ 0, less than `timeout`)
- [`RenderPreview`](docs/tools.md#renderpreview) *(beta 2)*: `canvasControls.groupItems` entries are now objects `{index, title?}` instead of plain integers — `title` is derived from the `#Preview(arguments:)` value and may not be unique; pass `index` as `groupItemIndex`. `errors` is now always present in the output
- [`AddInfoPlist`](docs/tools.md#addinfoplist) *(RC)*: new `dictionary` value type — `infoPlistDictionaryItems` then takes a JSON-encoded dictionary instead of an array
- [`XcodeMakeDir`](docs/tools.md#xcodemakedir) *(RC)*: new `directoryKind` parameter — `folder` (default) creates a file system synchronized (buildable) folder, `group` a classic group backed by a directory; falls back to what the parent supports
- [`InvokeDebuggerCommand`](docs/tools.md#invokedebuggercommand) *(beta 2)*: description now steers toward `p`/`v` over `po`/`expression` to avoid unnecessary expression evaluation; schema unchanged
- `GetCodeCoverage` is announced in the beta 2 release notes (181141715) but still isn't in the RC — absent from `tools/list` of both servers
