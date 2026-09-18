---
name: xcode-mcp
description: >-
  Operate Xcode through its official MCP server: build, run, test, edit project
  configuration, localize, render SwiftUI previews, automate the simulator/device
  UI, triage shipped crashes, and run headless. Use whenever driving the xcode MCP
  tools (BuildProject, RunProject, RunSomeTests, DeviceInteraction*, StringCatalog*,
  RenderPreview, Xcode* workspace/file ops, and the rest).
when_to_use: >-
  Any task that builds, runs, tests, edits, localizes, previews, or inspects an
  Xcode project or its shipped diagnostics through the xcode MCP — or that
  automates an app on a simulator/device. Not for editing Swift source in the
  abstract (that needs no MCP), nor for another build system.
effort: medium
---

# Driving the Xcode MCP

The **xcode MCP server** lets an agent operate a real Xcode: browse and edit the
project, build, run, test, configure targets, localize, render previews, automate
the UI on a simulator or device, and read shipped crash/performance data. It reuses
Xcode's own engine, so results match what a developer sees in the IDE.

This skill is **workflow and gotcha guidance**, not a schema dump. Every tool's
parameters are already visible in the live tool list — read those for signatures.
Come here for *which* tools to chain, in what order, and what will bite you.

## Prime directive: check availability before you rely on it

**Baseline is Xcode 27.** The skill still works on Xcode 26.5, but 26.5 ships a much
smaller toolset (~21 tools vs 53 in 27), and Xcode 27.2 is still in **beta**.

Tools appear and disappear from the live tool list depending on the installed Xcode
and its downloaded assets. **This is the availability signal — use it:**

- **A tool absent from the live tool list is unavailable on this setup.** Don't
  assume; look. Whole categories below are 27-only and simply won't be present on 26.5.
- Some tools are present only after a runtime gate is satisfied (see *Runtime gating*).
- If the user is specifically asking for a feature that isn't available here, **say so
  plainly and offer the path**: update Xcode (name the minimum version), enable the
  gating skill, or use the documented workaround. Don't silently substitute or fail.

### Availability badges used throughout the references

| Badge | Meaning |
|---|---|
| `[26.5+]` | Present in the baseline; safe to assume on any supported Xcode. |
| `[27+]` | Requires Xcode 27. Absent on 26.5 — verify via the live tool list. |
| `[27.2 beta]` | Only in the Xcode 27.2 **beta**. Verify before use; will be absent on release Xcode. |

## Router — load exactly one reference for the task at hand

Read `SKILL.md` (this file) for the cross-cutting rules, then open the **one**
reference that matches what you're doing. They're written to stand alone.

| You are… | Read |
|---|---|
| Compiling, launching, tailing the console, or debugging | `references/building-and-running.md` |
| Discovering or running tests, switching test plans | `references/testing.md` |
| Editing files, targets, build settings, entitlements, Info.plist | `references/project-configuration.md` |
| Working with String Catalogs / translating | `references/localization.md` |
| Rendering SwiftUI previews | `references/previews.md` |
| Searching Apple documentation from the MCP | `references/documentation.md` |
| Automating the app's UI on a simulator/device | `references/device-interaction.md` |
| Triaging shipped crashes or field performance | `references/crash-and-performance.md` |
| Running without an Xcode window / managing permissions | `references/headless-and-permissions.md` |

## Cross-cutting gotchas (apply everywhere)

**`tabIdentifier` is optional in 27, was effectively required in 26.5.** Most tools
take an optional `tabIdentifier` selecting which Xcode workspace tab to act on. Omit
it when only one tab is open. `[27+]` Scripts that hardcode it still work.

**Headless renames it.** In headless mode every `tabIdentifier` becomes
`workspaceIdentifier`, accepting either an identifier (e.g. `workspace-LKfjPJCMBL`)
or an absolute project path. See `references/headless-and-permissions.md`.

**Runtime gating (beyond version):** some tools are hidden until a precondition holds.
- **Localization** tools (`StringCatalog*`, `LocalizationPlanner`) require activating
  the corresponding translation skill first — see `references/localization.md`.
- **Documentation search** is asset-gated: it's absent from the tool list until Apple's
  documentation asset finishes downloading — see `references/documentation.md`.

**Version drift in names.** Tool and parameter names have shifted across versions
(e.g. `ExecuteSnippet` → `RunCodeSnippet`; the device *synthesize* tool is
`DeviceInteractionSynthesize` in current builds, older material calls it
`DeviceEventSynthesize`). Trust the live tool list over any doc, this one included.

**Prefer per-run overrides over mutating the user's config.** Where a tool lets you
pass launch arguments/environment or a render destination for one invocation, use
that instead of editing the scheme or project — it has no lasting effect.

## Version matrix (capability tiers)

Assume 27. On 26.5, treat everything marked `[27+]` as absent and confirm via the
live tool list.

| Capability | Tier |
|---|---|
| File read/write/glob/grep, build, run tests, get build log, render preview, documentation search | `[26.5+]` |
| Run/stop app, console output, debugger (`RunProject`, `StopProject`, `GetConsoleOutput`, `InvokeDebuggerCommand`) | `[27+]` |
| Workspace mgmt (`XcodeListWorkspaces`, `XcodeOpenWorkspace`, `XcodeCloseWorkspace`) + headless mode | `[27+]` |
| Scheme / run-destination / target / template management (`XcodeList*`, `XcodeSwitch*`, `XcodeNewTarget`, `XcodeNewProject`) | `[27+]` |
| Config editing (`AddEntitlement`, `AddInfoPlist`, `*TargetBuildSetting*`, `*FileCompilerFlags`) | `[27+]` |
| Test-plan management (`XcodeListTestPlans`, `XcodeSwitchTestPlan`) | `[27+]` |
| Device/simulator UI automation (`DeviceInteraction*`) | `[27+]` |
| Crash & field-performance analytics (`GetTopCrashIssues`, `GetCrashIssueLogs`, `GetTopFieldPerformanceIssues`, `GetFieldPerformanceIssueLogs`) | `[27+]` |
| String Catalog tools + `LocalizationPlanner` | `[27+]` |
| `RenderPreview` `preferredRenderDestination` param + `availableRenderDestinations` output | `[27.2 beta]` |

## Related, obtained separately

Xcode ships built-in agent skills (SwiftUI, App Intents, tests, device interaction,
etc.) exportable with `xcrun agent skills export <dir>` or packaged via
`xcrun agent plugin path`. Those are API/domain skills; this skill deliberately
duplicates none of them except the device-interaction knowledge, which it folds in so
it stays self-contained.
