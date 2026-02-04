# Xcode Tools Documentation

A comprehensive reference for the Xcode MCP Server aka Xcode Tools. These tools enable AI assistants to interact with Xcode workspaces — managing files, building projects, running tests, rendering previews, and more.

## Prerequisites

- Xcode installed and running with an open workspace
- MCP server configured with Xcode integration

> **Note:** Most tools require a `tabIdentifier` parameter that identifies which Xcode workspace tab to operate on.

## Apple Documentation

- [Setting up coding intelligence](https://developer.apple.com/documentation/xcode/setting-up-coding-intelligence)
- [Writing code with intelligence in Xcode](https://developer.apple.com/documentation/xcode/writing-code-with-intelligence-in-xcode)
- [Giving agentic coding tools access to Xcode](https://developer.apple.com/documentation/xcode/giving-agentic-coding-tools-access-to-xcode)

## Quick Reference

| Tool | Description |
|------|-------------|
| **XcodeListWindows** | List open Xcode windows and their workspace info |
| **XcodeLS** | List files/directories in the project navigator |
| **XcodeGlob** | Find files matching wildcard patterns |
| **XcodeGrep** | Search file contents with regex |
| **XcodeRead** | Read file contents with line numbers |
| **XcodeWrite** | Create or overwrite files in the project |
| **XcodeUpdate** | Edit files by replacing text |
| **XcodeMakeDir** | Create directories/groups in the project |
| **XcodeMV** | Move, copy, or rename files |
| **XcodeRM** | Remove files/directories from the project |
| **BuildProject** | Build the Xcode project |
| **GetBuildLog** | Retrieve build log entries filtered by severity |
| **ExecuteSnippet** | Run a code snippet in the context of a source file |
| **GetTestList** | List all available tests |
| **RunAllTests** | Run all tests from the active test plan |
| **RunSomeTests** | Run specific tests by identifier |
| **XcodeRefreshCodeIssuesInFile** | Get compiler diagnostics for a file |
| **XcodeListNavigatorIssues** | List issues from Xcode's Issue Navigator |
| **RenderPreview** | Build and snapshot a SwiftUI preview |
| **DocumentationSearch** | Search Apple Developer Documentation |

---

## Workspace

### XcodeListWindows

Lists current Xcode windows and their workspace information. Use this to obtain `tabIdentifier` values needed by all other tools.

**Parameters:** None

**Example:**
```
XcodeListWindows()
```

---

## File Operations

### XcodeLS

Lists files and directories in the Xcode project structure at a given path. Operates on the project navigator hierarchy, not the filesystem.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `path` | string | Yes | Project path to browse (e.g., `ProjectName/Sources/`) |
| `recursive` | boolean | No | List all files recursively (truncated at 100 lines). Default: `true` |
| `ignore` | string[] | No | Patterns to skip |

**Example:**
```
XcodeLS(tabIdentifier: "...", path: "MyApp/Sources/")
```

### XcodeGlob

Finds files in the Xcode project matching wildcard patterns. Supports `*`, `**`, `?`, `[abc]`, and `{swift,m}` syntax.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `pattern` | string | No | Glob pattern (e.g., `**/*.swift`). Defaults to `**/*` |
| `path` | string | No | Directory to search in (defaults to project root) |

**Example:**
```
XcodeGlob(tabIdentifier: "...", pattern: "**/*.swift")
```

### XcodeGrep

Searches file contents using regex patterns within the Xcode project structure.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `pattern` | string | Yes | Regex pattern to search for |
| `path` | string | No | File or directory to search in (defaults to root) |
| `glob` | string | No | Only search files matching this glob |
| `type` | string | No | File type shortcut (`swift`, `js`, `py`, etc.) |
| `outputMode` | string | No | `content`, `filesWithMatches` (default), or `count` |
| `ignoreCase` | boolean | No | Case-insensitive matching |
| `multiline` | boolean | No | Allow patterns to span multiple lines |
| `showLineNumbers` | boolean | No | Show line numbers (content mode only) |
| `linesBefore` | integer | No | Context lines before each match |
| `linesAfter` | integer | No | Context lines after each match |
| `linesContext` | integer | No | Context lines before and after each match |
| `headLimit` | integer | No | Stop after N results |

**Example:**
```
XcodeGrep(
  tabIdentifier: "...",
  pattern: "func viewDidLoad",
  type: "swift",
  outputMode: "content",
  linesAfter: 5
)
```

### XcodeRead

Reads file contents with line numbers (`cat -n` format). Supports offset/limit for large files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path (e.g., `ProjectName/Sources/MyFile.swift`) |
| `offset` | integer | No | Line number to start reading from |
| `limit` | integer | No | Number of lines to read (default: up to 600) |

**Example:**
```
XcodeRead(tabIdentifier: "...", filePath: "MyApp/Sources/ContentView.swift")
```

### XcodeWrite

Creates or overwrites files in the Xcode project. Automatically adds new files to the project structure.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path |
| `content` | string | Yes | File content to write |

**Example:**
```
XcodeWrite(
  tabIdentifier: "...",
  filePath: "MyApp/Sources/NewFeature.swift",
  content: "import Foundation\n\nstruct NewFeature {\n}\n"
)
```

### XcodeUpdate

Edits files by finding and replacing text. Operates on project structure paths.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path |
| `oldString` | string | Yes | Text to find |
| `newString` | string | Yes | Replacement text (must differ from `oldString`) |
| `replaceAll` | boolean | No | Replace all occurrences. Default: `false` |

**Example:**
```
XcodeUpdate(
  tabIdentifier: "...",
  filePath: "MyApp/Sources/ContentView.swift",
  oldString: "Hello, World!",
  newString: "Hello, SwiftUI!"
)
```

### XcodeMakeDir

Creates directories and groups in the Xcode project navigator.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `directoryPath` | string | Yes | Project-relative path for the new directory |

**Example:**
```
XcodeMakeDir(tabIdentifier: "...", directoryPath: "MyApp/Sources/ViewModels")
```

### XcodeMV

Moves, copies, or renames files and directories in the project navigator.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `sourcePath` | string | Yes | Source path in project navigator |
| `destinationPath` | string | Yes | Destination path or new name |
| `operation` | string | No | `move` or `copy` |
| `overwriteExisting` | boolean | No | Overwrite files at destination |

**Example:**
```
XcodeMV(
  tabIdentifier: "...",
  sourcePath: "MyApp/Sources/OldName.swift",
  destinationPath: "MyApp/Sources/NewName.swift"
)
```

### XcodeRM

Removes files and directories from the Xcode project. Optionally deletes underlying filesystem files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `path` | string | Yes | Project path to remove |
| `recursive` | boolean | No | Remove directories and contents recursively |
| `deleteFiles` | boolean | No | Also move files to Trash. Default: `true` |

**Example:**
```
XcodeRM(tabIdentifier: "...", path: "MyApp/Sources/Deprecated.swift")
```

---

## Build & Run

### BuildProject

Builds the Xcode project using the active scheme and waits for completion.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |

**Example:**
```
BuildProject(tabIdentifier: "...")
```

### GetBuildLog

Retrieves build log entries from the current or most recent build. Filter by severity, file pattern, or message regex.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `severity` | string | No | Minimum severity: `error` (default), `warning`, or `remark` |
| `pattern` | string | No | Regex to filter by message, task description, command line, or console output |
| `glob` | string | No | Glob to filter by file path or task location |

**Example:**
```
GetBuildLog(tabIdentifier: "...", severity: "warning")
```

### ExecuteSnippet

Builds and runs a code snippet in the context of a specific source file. The snippet has access to all declarations in that file, including `fileprivate` ones. Output comes from `print` statements.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `codeSnippet` | string | Yes | Swift code to execute |
| `sourceFilePath` | string | Yes | Project-relative path to the context file |
| `timeout` | integer | No | Max wait time in seconds. Default: 120 |

> **Note:** Only works with source files in targets that build apps, frameworks, libraries, or CLI executables.

**Example:**
```
ExecuteSnippet(
  tabIdentifier: "...",
  sourceFilePath: "MyApp/Sources/Models/User.swift",
  codeSnippet: "let user = User(name: \"Test\")\nprint(user)"
)
```

---

## Testing

### GetTestList

Lists all available tests from the active scheme's active test plan.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |

**Example:**
```
GetTestList(tabIdentifier: "...")
```

### RunAllTests

Runs every test in the active scheme's active test plan.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |

**Example:**
```
RunAllTests(tabIdentifier: "...")
```

### RunSomeTests

Runs specific tests by target and identifier. Use `GetTestList` first to discover available test identifiers.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `tests` | array | Yes | Array of test specifiers (see below) |

Each test specifier object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `targetName` | string | Yes | Test target name |
| `testIdentifier` | string | Yes | Test identifier in XCTestIdentifier format |

**Example:**
```
RunSomeTests(
  tabIdentifier: "...",
  tests: [
    { "targetName": "MyAppTests", "testIdentifier": "MyAppTests/LoginTests/testValidLogin" }
  ]
)
```

---

## Diagnostics

### XcodeRefreshCodeIssuesInFile

Retrieves current compiler diagnostics (errors, warnings, notes) for a specific file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `filePath` | string | Yes | Project-relative file path |

**Example:**
```
XcodeRefreshCodeIssuesInFile(
  tabIdentifier: "...",
  filePath: "MyApp/Sources/ContentView.swift"
)
```

### XcodeListNavigatorIssues

Lists issues from Xcode's Issue Navigator, including build errors, package resolution problems, and workspace configuration issues.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `severity` | string | No | Minimum severity: `error` (default), `warning`, or `remark` |
| `pattern` | string | No | Regex to filter by message |
| `glob` | string | No | Glob to filter by file path |

**Example:**
```
XcodeListNavigatorIssues(tabIdentifier: "...", severity: "warning")
```

---

## Preview

### RenderPreview

Builds and renders a SwiftUI preview, returning a snapshot of the resulting UI.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tabIdentifier` | string | Yes | Workspace tab identifier |
| `sourceFilePath` | string | Yes | Project-relative path to the file containing the preview |
| `previewDefinitionIndexInFile` | integer | No | Zero-based index of the `#Preview` macro or `PreviewProvider` in the file. Default: `0` |
| `timeout` | integer | No | Max wait time in seconds. Default: 120 |

**Example:**
```
RenderPreview(
  tabIdentifier: "...",
  sourceFilePath: "MyApp/Sources/Views/ProfileView.swift"
)
```

---

## Documentation

### DocumentationSearch

Searches Apple Developer Documentation using semantic matching. Useful for looking up APIs, frameworks, and usage patterns.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `frameworks` | string[] | No | Limit search to specific frameworks. Searches all if omitted |

## Author

Artem Novichkov, https://artemnovichkov.com
