# Building & running

Tools: `BuildProject`, `GetBuildLog`, `XcodeSwitchScheme`, `XcodeListSchemes`,
`XcodeListRunDestinations`, `XcodeSwitchRunDestination`, `RunProject` `[27+]`,
`StopProject` `[27+]`, `GetConsoleOutput` `[27+]`, `InvokeDebuggerCommand` `[27+]`,
`RunCodeSnippet` `[27+]`, `XcodeRefreshCodeIssuesInFile`.

## Recipe: edit → build → verify

1. Make the source edits (`XcodeWrite` / your editor).
2. `BuildProject`. Pass `buildForTesting: true` `[27+]` when the goal is to run tests
   afterward without a second compile.
3. On failure, `GetBuildLog` and read the diagnostics. Filter with its `severity`,
   `pattern` (message regex), and `glob` (file) parameters instead of pulling the whole
   log. Don't assume every issue entry carries a line number.
4. Optionally `XcodeRefreshCodeIssuesInFile` to re-run in-editor diagnostics for a file
   after an edit without a full build.

## Recipe: run and watch `[27+]`

1. Pick the destination: `XcodeListRunDestinations` → `XcodeSwitchRunDestination`.
   Prefer a real, appropriate destination (Mac Catalyst / a booted simulator / a
   device) over guessing an identifier.
2. `RunProject` to launch.
3. `GetConsoleOutput` to tail stdout/stderr.
4. `StopProject` when done. Don't leave apps running across unrelated work.

To attach the debugger, use `InvokeDebuggerCommand` (LLDB). For richer LLDB access a
separate `xcrun lldb-mcp` server exists `[27+]`; only reach for it when the single
command tool is insufficient.

## Schemes

`XcodeListSchemes` → `XcodeSwitchScheme` `[27+]`. The active scheme determines what
`BuildProject`/`RunProject` act on and which launch arguments/environment apply.
Prefer switching scheme over editing one.

## Gotchas

- **`buildForTesting`** `[27+]` is a `BuildProject` parameter, not a separate tool.
  Building for testing once and then running tests avoids a redundant recompile.
- **Console vs build log** are different tools: `GetBuildLog` is compile-time
  diagnostics; `GetConsoleOutput` `[27+]` is the running app's runtime output.
- **Per-run launch overrides** (arguments/environment) belong on the run/install call,
  not baked into the scheme — see `device-interaction.md` for the `$(inherited)` token
  syntax, which also applies when launching.
- **`RunCodeSnippet`** `[27+]` (formerly `ExecuteSnippet`) now requires a `purpose`
  parameter describing why you're running the snippet.
