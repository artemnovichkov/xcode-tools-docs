---
name: update-xcode-mcp
description: Check a newly installed Xcode (beta, RC, or release) for changes in its MCP server — capture `tools/list` from the windowed and headless servers, diff against the committed schemas, and update tools-*.json, CHANGELOG.md, README.md, and docs/. Use when the user installed a new Xcode build, asks to "check MCP changes", "update docs for Xcode X", or mentions a build number like 27B52.
---

# Update docs for a new Xcode build

Repo documents Xcode's MCP server. Source of truth = raw `tools/list` captures in the root (`tools*.json`); docs describe them.

## 1. Identify the build

```bash
xcode-select -p
for a in /Applications/Xcode*.app; do echo "$a $(defaults read $a/Contents/version.plist ProductBuildVersion) $(defaults read $a/Contents/Info.plist CFBundleShortVersionString)"; done
mdls -name kMDItemWhereFroms ~/Downloads/Xcode_*.xip   # URL tells beta / Release_Candidate / release
```

Build suffix letter (e.g. `27B5028f`) = beta; plain (`27B48`, `27B52`) = RC or release — confirm via xip URL or release notes. Ask user if unclear.

Use the new Xcode's bridge explicitly: `BRIDGE=/Applications/XcodeN.app/Contents/Developer/usr/bin/mcpbridge` (or `xcrun -f mcpbridge` if it's the selected one).

## 2. Capture schemas

Scripts live in `.claude/skills/update-xcode-mcp/scripts/`. Write to the scratchpad first, never straight over committed files.

**Headless** (`xcrun mcp-server status` must show `running`/enabled; bridge then launches the new Xcode's `Xcode Service.app`):

```bash
python3 -I scripts/capture_tools.py "$BRIDGE" $SCRATCH/headless.json
pgrep -lf "Xcode Service"   # confirm service path belongs to the new Xcode
```

**Windowed** — open a project in the new Xcode, target it by PID:

```bash
open -a /Applications/XcodeN.app ~/Developer/TaskExample/TaskExample.xcodeproj
P=$(pgrep -f "^/Applications/XcodeN.app/Contents/MacOS/Xcode$")   # PID may change after launch; re-read
MCP_XCODE_PID=$P python3 -I scripts/capture_tools.py "$BRIDGE" $SCRATCH/windowed.json
```

stderr prints `serverInfo.version` (server build, e.g. `25464`) and tool count — record both.

If windowed capture fails ("bridge closed before response 2"): Xcode may show an agent-approval dialog or have Xcode Tools off in Settings › Intelligence — ask user to allow, retry once. If still failing, ask whether to proceed headless-only; never claim the windowed file was re-captured when it wasn't.

## 3. Diff

```bash
python3 -I scripts/diff_tools.py tools-headless-27.2.json $SCRATCH/headless.json
python3 -I scripts/diff_tools.py tools-27.2.json $SCRATCH/windowed.json
```

Shows added/removed tools and per-tool changed paths (descriptions, input/output schema properties, enums, required). `identical` = only server build changed.

Also check:
- Windowed vs headless split still the same (`diff_tools.py windowed.json headless.json`; expected: `tabIdentifier` ↔ `workspaceIdentifier`; windowed-only `XcodeListWindows`, `XcodeGetCurrentFile`, `XcodeListNavigatorIssues`; headless-only `XcodeListWorkspaces`, `XcodeOpenWorkspace`, `XcodeCloseWorkspace`, `XcodeNewProject`).
- `DocumentationSearch` is asset-gated — absence may mean missing `com.apple.MobileAsset.AppleDeveloperDocumentation`, not removal.
- Tools announced in release notes but absent (e.g. `GetCodeCoverage`) — mention in changelog.

## 4. Update files

Captures use `json.dump(indent=2, sort_keys=True)`, ASCII-escaped, no trailing newline — the script matches this, so unchanged schemas are byte-identical.

| File | What to change |
|---|---|
| `tools-<ver>.json`, `tools-headless-<ver>.json` | Copy captures over (new minor version → new files, e.g. `tools-27.3.json`) |
| `CHANGELOG.md` | `## Xcode <ver> [beta N / RC]` section: build, server version, prior builds history line; bullets per change, tagged *(beta N)* / *(RC)* when introduced mid-cycle; *(breaking)* for renames/removals. Link tools as ``[`Name`](docs/tools.md#anchor)`` |
| `docs/tools.md` | Parameter tables + per-tool notes; mark new params *Xcode <ver>.*; new tools get full sections and an index entry |
| `docs/schemas.md` | Version/build column for each file |
| `README.md` | Version mention + changelog anchor in intro and "Further documentation" table |

When stage changes (beta → RC → release), rename headings/anchors everywhere: `grep -rn -E "RC|beta|<old build>|<old anchor>" README.md CHANGELOG.md docs`. Anchors: `## Xcode 27.2 RC` → `#xcode-272-rc`.

Style: concise, factual, describe what the schema says; don't speculate about behavior not in the schema or verified by calling the tool.

## 5. Finish

- Show `git diff --stat` and a short summary: build, server version, changes (or "schemas identical").
- Commit only when asked. Message style: `Update with Xcode 27.2 RC`.
