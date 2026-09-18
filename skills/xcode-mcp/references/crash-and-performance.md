# Crash & field-performance triage

Tools `[27+]`: `GetTopCrashIssues`, `GetCrashIssueLogs`, `GetTopFieldPerformanceIssues`,
`GetFieldPerformanceIssueLogs`.

Read shipped diagnostics (from the App Store / TestFlight field data Xcode surfaces)
so the agent can triage real-world crashes and performance regressions.

## Recipe: triage crashes

1. `GetTopCrashIssues` — the ranked list of crash signatures affecting users.
2. Pick one, then `GetCrashIssueLogs` for its stack traces and per-crash guidance.
3. Correlate the frames with source (`XcodeGrep`/`XcodeRead`) to locate the fault.

## Recipe: triage field performance

1. `GetTopFieldPerformanceIssues` — the ranked performance issues (hangs, launch time,
   memory, etc.).
2. `GetFieldPerformanceIssueLogs` for the detail on a chosen issue.

## Gotchas

- **Requires field data.** These read what Xcode has for the signed-in team/app; with
  no shipped data (a brand-new or unreleased app) there's nothing to return.
- **All `[27+]`** — absent on 26.5; verify via the live tool list.
- This is read-only triage. Fixes go through the normal edit → build → test loop.
