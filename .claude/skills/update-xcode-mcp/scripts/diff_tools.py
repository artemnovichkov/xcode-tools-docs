#!/usr/bin/env python3
"""Semantic diff of two `tools/list` captures.

Usage: diff_tools.py <old.json> <new.json>
Reports added/removed tools and, per tool, changed title, description,
annotations, and input/output schema paths (property-level).
"""
import json, sys

def load(path):
    return {t["name"]: t for t in json.load(open(path))["tools"]}

def flatten(node, prefix="", out=None):
    """Map JSON-pointer-ish paths to leaf values."""
    out = {} if out is None else out
    if isinstance(node, dict):
        for k, v in node.items():
            flatten(v, f"{prefix}/{k}", out)
    elif isinstance(node, list) and not all(isinstance(x, (str, int, float, bool)) for x in node):
        for i, v in enumerate(node):
            flatten(v, f"{prefix}[{i}]", out)
    else:
        out[prefix] = node
    return out

def short(v, n=160):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"

old, new = load(sys.argv[1]), load(sys.argv[2])
added, removed = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
print(f"tools: {len(old)} → {len(new)}")
if added: print("added:", ", ".join(added))
if removed: print("removed:", ", ".join(removed))

changed = False
for name in sorted(old.keys() & new.keys()):
    a, b = flatten(old[name]), flatten(new[name])
    diffs = []
    for path in sorted(a.keys() | b.keys()):
        if a.get(path) == b.get(path):
            continue
        if path not in a:
            diffs.append(f"  + {path} = {short(b[path])}")
        elif path not in b:
            diffs.append(f"  - {path} (was {short(a[path])})")
        elif path.endswith("description") and isinstance(a[path], str):
            diffs.append(f"  ~ {path}\n      old: {short(a[path], 400)}\n      new: {short(b[path], 400)}")
        else:
            diffs.append(f"  ~ {path}: {short(a[path])} → {short(b[path])}")
    if diffs:
        changed = True
        print(f"\n{name}")
        print("\n".join(diffs))

if not (added or removed or changed):
    print("identical")
