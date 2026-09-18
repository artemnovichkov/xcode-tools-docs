# Apple documentation search

Tool: `DocumentationSearch` `[26.5+]` — "Searches Apple Developer Documentation using
semantic matching."

Search Apple's developer documentation from inside the MCP, returning symbol/API
reference without leaving the toolchain.

## May be absent even though the tool is baseline

`DocumentationSearch` does **semantic** matching, so it depends on a search
index/model asset that is **separate from Xcode's browsable documentation bundle** —
having docs viewable in Xcode does not guarantee the tool is available. Apple documents
it as asset-gated (absent from the live tool list until the asset lands, in both
windowed and headless mode). Observed in practice: it can be missing on a current
release Xcode with documentation installed, for reasons that may also include the
headless server not surfacing it or the MCP client filtering it. Treat its presence as
something to verify, not assume.

- If it's missing, that's the reason. It appears once the documentation asset is
  installed (opening documentation in Xcode triggers the download).
- Don't treat its absence as a version problem, and don't retry in a loop — surface it
  and fall back.

## Fallback

If `DocumentationSearch` isn't available and the user needs Apple reference material,
use whatever dedicated Apple-documentation source the environment provides (e.g. a
documentation MCP), or web documentation — rather than blocking on the gated tool.
