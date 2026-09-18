# Localization & String Catalogs

Tools `[27+]`: `StringCatalogRead`, `StringCatalogContext`, `StringCatalogEdit`,
`LocalizationPlanner`.

## Runtime gate — activate the translation skill first

These four tools are **gated**: each one's own description states you MUST activate a
specific Xcode integration skill before calling it, and the required skill differs by
tool:

| Tool | Activate first |
|---|---|
| `StringCatalogContext`, `StringCatalogEdit` | `xcode-integration:translation` |
| `StringCatalogRead`, `LocalizationPlanner` | `xcode-integration:translation-coordinator` |

If they're missing from the live tool list, that gate — not a version problem — is
usually why. Read the tool's own description for the exact skill to load, activate it,
then proceed.

## Always go through these tools, never hand-edit

`.xcstrings` (and `.strings`) files are generated/managed artifacts. Editing them by
hand desyncs Xcode's catalog codegen and can break the build (the generated
`LocalizedStringResource` symbols come from Xcode, not from `swift build`). Use the
`StringCatalog*` tools for every read and write.

## Recipe: translate the app

1. `LocalizationPlanner` to prepare the project / identify what needs translating.
2. `StringCatalogRead` to pull current strings and states.
3. `StringCatalogContext` to get the surrounding context for a key (helps produce
   accurate, in-context translations rather than literal ones).
4. `StringCatalogEdit` to write translations back per locale.

## Gotchas

- **Absent tools usually mean the gate, not the version** — check skill activation
  before concluding the feature is unavailable.
- **Context matters for quality.** Prefer `StringCatalogContext` over translating from
  the raw key string alone.
