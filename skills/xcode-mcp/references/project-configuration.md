# Project configuration & files

File/navigator tools: `XcodeLS`, `XcodeGlob`, `XcodeGrep`, `XcodeRead`, `XcodeWrite`,
`XcodeMV`, `XcodeRM`, `XcodeMakeDir`.
Config tools `[27+]`: `XcodeListTargets`, `XcodeListTemplates`, `XcodeNewTarget`,
`XcodeNewProject`, `AddEntitlement`, `AddInfoPlist`, `GetTargetBuildSettings`,
`UpdateTargetBuildSetting`, `GetFileCompilerFlags`, `UpdateFileCompilerFlags`.

## Files through the project navigator

Prefer the `Xcode*` file tools over raw filesystem access: they operate through the
project navigator, so new/removed/moved files stay in sync with the `.xcodeproj`
instead of dangling.

- Find: `XcodeGlob` (paths) / `XcodeGrep` (contents) → `XcodeRead`.
- Mutate: `XcodeWrite`, `XcodeMakeDir`, `XcodeMV`, `XcodeRM`.
- `[27+]` `XcodeMV`'s `operation` is a plain string enum (`move` / `copy`), not an
  object with a `rawValue`. Older material shows the object form — use the string.

## Entitlements vs Info.plist — not interchangeable `[27+]`

- **`AddEntitlement`** — restricted system capabilities: App Groups, Push
  Notifications, iCloud, and similar entitlement-backed features.
- **`AddInfoPlist`** — bundle metadata and privacy usage strings
  (`NS*UsageDescription`), URL types, and other Info.plist keys.

Using one where the other belongs won't have the intended effect and won't error
obviously. Match the mechanism to the capability.

## Build settings `[27+]`

`GetTargetBuildSettings` to read, `UpdateTargetBuildSetting` to change. Set flags at
the **target** level here rather than per file (below).

## Compiler flags — the Swift trap `[27+]`

`GetFileCompilerFlags` / `UpdateFileCompilerFlags` set flags on individual files.
**Per-file flags on `.swift` files usually don't affect the build**, because Swift
compiles per module — the setting is silently ineffective. For Swift, add flags via
`OTHER_SWIFT_FLAGS` at the target level (`UpdateTargetBuildSetting`) instead. Per-file
flags are meaningful mainly for C/Objective-C/C++ sources.

## New targets / projects `[27+]`

`XcodeListTemplates` → `XcodeNewTarget` / `XcodeNewProject`. `XcodeNewProject` is
primarily a headless-oriented capability; verify it's present before relying on it.
