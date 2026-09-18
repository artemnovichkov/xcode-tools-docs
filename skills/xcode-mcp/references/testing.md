# Testing

Tools: `GetTestList`, `RunAllTests`, `RunSomeTests`, `XcodeListTestPlans` `[27+]`,
`XcodeSwitchTestPlan` `[27+]`, and `BuildProject` (with `buildForTesting`).

## Recipe: test a change

1. `[27+]` If the project has multiple test plans, `XcodeListTestPlans` →
   `XcodeSwitchTestPlan` to select the right one first.
2. `GetTestList` to discover available tests (targets → suites → cases). Use it to
   build the identifiers you'll pass to `RunSomeTests`.
3. Run:
   - `RunSomeTests` for a targeted subset — pass test identifiers.
   - `RunAllTests` for the whole plan.
4. Read results. `[27+]` output includes `xcresultBundlePath` — open that bundle for
   full failure detail, attachments, and logs beyond the summary.

## Test identifiers

`RunSomeTests` takes identifiers shaped `Target/Suite/Case` (Swift Testing) or the
XCTest equivalent. Get exact strings from `GetTestList` rather than constructing them
by hand — module and suite naming is easy to get subtly wrong.

## Gotchas

- **Build once for testing.** `BuildProject` with `buildForTesting: true` `[27+]`
  before running avoids a redundant compile inside the test run.
- **Hanging/expensive test targets are a project concern, not the MCP's.** If a
  specific bundle wedges or is slow, skip it in the broad run and exercise it
  separately — capture that in the project's own CLAUDE.md, not here.
- **`xcresultBundlePath`** `[27+]` is the authoritative artifact. When a summary is
  ambiguous, read the bundle rather than re-running.
