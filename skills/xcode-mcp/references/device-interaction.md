# Device & simulator UI automation

Tools `[27+]`: `DeviceInteractionStartWorkspaceSession`, `DeviceInteractionStartSession`,
`DeviceInteractionInstallAndRun`, `DeviceInteractionSynthesize`,
`DeviceInteractionEndSession`.

> Name drift: the synthesize tool is `DeviceInteractionSynthesize` in current builds;
> older material calls it `DeviceEventSynthesize`. Trust the live tool list.

Drive a real app on a simulator or device: launch it, read its UI hierarchy, tap /
swipe / type, and observe the result — the way to verify behavior and layout end to end.

## Run it in a subagent

UI verification is long-running and chatty. Prefer to run it in a **subagent** with
exclusive use of one session: start the session, hand its identifier to the subagent,
let it do the launch/interact/observe loop, and report back. Keep one session per
subagent to avoid cross-talk.

## Session lifecycle

```
StartWorkspaceSession   (start early; runs in the background)
  → InstallAndRun       (after each code change; builds first)
    → Synthesize        (interact + observe; repeat)
  → EndSession          (always — open sessions are resource-heavy)
```

Two ways to start:

- **`DeviceInteractionStartWorkspaceSession`** — bound to a workspace. Required for
  `InstallAndRun`. Use when verifying the app you're building.
- **`DeviceInteractionStartSession`** — not bound to a workspace. Use only to interact
  with an already-installed app.

**Sessions are expensive.** Start one early (in parallel with other setup) and
**always** `EndSession` when done; leaving them open degrades responsiveness.

### Device discovery

When starting a session, pass a device identifier to pick a target, omit it to use the
current run destination, or pass an **empty string** to get the list of available
targets.

## InstallAndRun: per-run launch overrides

Prefer these over editing the scheme — they apply to the single run only, with no
lasting effect on the user's config:

- `commandLineArguments` — launch arguments. Use the token `$(inherited)` to keep the
  scheme's existing arguments, e.g. `["$(inherited)", "--reset-state"]`.
- `environmentVariables` — launch environment. Use `"$(inherited)"` as a key to keep
  the scheme's existing variables, e.g. `{"$(inherited)": "", "DEBUG_MODE": "1"}`.

Omit both to leave the scheme untouched.

## The observe → act → observe loop

`DeviceInteractionSynthesize` both performs an interaction and returns the resulting
state (screenshot + UI hierarchy). **Always capture and read the hierarchy before
interacting, and capture again after to verify.** To capture without acting, call it
with an empty interaction command.

### Reading the hierarchy

Each element reports its frame and a precomputed **`hitPoint`** — the best point to
tap:

```
UIView {{100, 200}, {60, 30}}, hitPoint: {130.0, 215.0}
  UIButton "Login" {{110, 205}, {30, 20}}, hitPoint: {125.0, 215.0}
  UIButton "Login2" {{140, 205}, {20, 20}}, hitPoint: {150.0, 215.0}, activationBundleId: com.your.app
```

- `{100, 200}` = origin, `{60, 30}` = size, `hitPoint` = where to tap.
- **Always tap the `hitPoint`.** Only if a hitPoint tap demonstrably does nothing (confirm
  by recapturing) may you fall back to a screenshot-estimated coordinate.
- **`isRemoteLeafPlaceholder`** elements don't report children — those require
  screenshot-estimated coordinates.
- For compound controls (toggles, sliders) inspect nested elements; the real control
  may be a child (`Switch`, `Slider`) rather than the container.

### Multiple apps on screen (`activationBundleId`)

When windows from more than one app overlap, elements are suffixed with
`activationBundleId: <bundle-id>`. To interact with such an element you must **activate
that app first** by passing `activationBundleId` to `Synthesize`. Activation is
expensive — only do it when needed. You can pass `activationBundleId` with no
interaction command to just switch focus.

## Interaction command grammar

The interaction command is a compact string:

| Command | Meaning |
|---|---|
| `t <x> <y> [dur]` | Tap (optional hold duration) |
| `d <x> <y>` | Double tap |
| `t <x1> <y1> f <x2> <y2> [dur]` | Swipe from → to |
| `drag <x1> <y1> <x2> <y2> [hold] [move]` | Press-hold then drag (reorder / drag-drop) |
| `mt [x y, ...] dur [x y, ...] dur ...` | Multi-touch. Each `[...]` is a keyframe of finger positions; the duration after a block is travel time to the next (hold time before lift for the last). A finger ends via an empty slot (`[, x y]`) or by absence in a later frame; reappearing after lifting starts a new tap. |
| `b h/p/u/d [dur]` | Hardware button: Home / Power / VolUp / VolDown |
| `b c/s/a [dur]` | **watchOS**: Digital Crown press / side / Action button |
| `sender keyboard kbd <text>` | Type text. **Must be last in the chain**; everything after `kbd ` is verbatim (spaces preserved). Use `\u{XXXX}` escapes, e.g. `\u{000A}` = Return, `\u{0009}` = Tab |
| `w <dur>` | Wait |
| `orientation <value>` | iOS: `faceDown/faceUp/landscapeLeft/landscapeRight/portrait/portraitUpsideDown` |
| `c <rotations>` | **watchOS**: rotate Digital Crown; sign = direction, 1.0 = one turn |
| `r <dir>` | **tvOS**: Siri Remote `up/down/left/right/select/menu/playpause/home` |

Examples: `t 100 200` (tap) · `t 200 600 f 200 200 0.3` (swipe up) ·
`drag 100 300 100 100 0.5 1.5` (drag with 0.5s hold, 1.5s move) ·
`mt [100 300, 300 300] 0.5 [175 300, 225 300] 0.5` (two-finger pinch) ·
`b h b h` (app switcher) · `sender keyboard kbd submit\u{000A}` (type then Return).

## tvOS is focus-based

No touchscreen — coordinate taps don't apply. Exactly one element is `Focused`; you
can only activate what's focused. Read the hierarchy, count steps to the target, and
**chain the presses in one command**, then capture once, e.g. `r right r right r select`.
`r menu` goes back, `r home` to the Home screen.

## Timing & retries

- **Launch**: the app may take seconds. Capture and confirm meaningful UI (not a launch
  screen) before interacting; recapture if empty.
- **After an interaction**: if nothing changed, recapture and retry **once** (the
  element may have moved mid-animation). Still failing → report, don't loop.
- **Loading states**: on a spinner, wait briefly and recapture; don't interact with
  loading elements.
- Don't pad with arbitrary waits — the tools return once animations settle.

## Judging success vs failure

- **Report**: functional bugs (no response, wrong navigation, missing data/elements),
  visual bugs (overlap, truncation, off-screen, wrong colors, broken alignment), and
  crashes/unexpected exits (track the pid; read its output).
- **Don't report as bugs**: transient states (spinners, brief animations, keyboard
  appearing) — recapture after they settle; and expected behavior (empty-state
  placeholders, disabled buttons on incomplete forms, permission dialogs).

## Error handling

- App not visible → retry once (may be a slow device).
- Tap target unclear → re-read the hierarchy for the correct `hitPoint`.
- Suspected timing bug → runtime logs help; suggest to the main agent that temporary
  `print` statements in the relevant code may aid diagnosis.
