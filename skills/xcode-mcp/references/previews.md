# SwiftUI previews

Tool: `RenderPreview` `[26.5+]`.

Render a SwiftUI preview to an image so the agent can see the UI without a full run.
This is the fastest way to validate a view change — prefer it over launching the app
when you only need to confirm layout/appearance.

## Recipe

1. Ensure the file/preview builds (a broken build yields no image).
2. `RenderPreview` for the target preview.
3. Inspect the returned image; iterate on the source and re-render.

## Locale / variant / canvas overrides

`RenderPreview` takes `previewLocalizationOverride`, `previewVariantOverrides`, and
`previewCanvasControlOverrides` to render a specific locale/variant/appearance, plus
`previewDefinitionIndexInFile` to pick which preview in the file.

- **Serial when overriding localization.** Per Apple's docs, when
  `previewLocalizationOverride` is set, **do not call `RenderPreview` in parallel** — it
  relies on internal state that isn't concurrency-safe. Render one at a time. (This is
  documented behavior, not stated in the tool's one-line schema description.)

## Choosing the render destination `[27.2 beta]`

Xcode 27.2 beta adds destination control to `RenderPreview`:

- New input `preferredRenderDestination` — target a specific device/simulator by
  `identifier`, `platformName`, `deviceModelName`, or `systemVersion`.
- Output gains `availableRenderDestinations` (what you can pick from) and
  `renderedDestination` now carries a required `identifier`.

**Verify first.** This is beta-only: on release Xcode the parameter is absent. Check
the live tool schema before relying on `preferredRenderDestination`; if the user needs
it and it's missing, tell them it requires the Xcode 27.2 beta.

## Gotchas

- **No image ≠ no preview** — a failed build or an unrenderable preview both yield
  nothing. Confirm the build first.
- Previews validate appearance, not behavior. For interaction, use
  `device-interaction.md`.
