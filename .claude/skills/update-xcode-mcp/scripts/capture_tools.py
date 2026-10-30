#!/usr/bin/env python3
"""Capture Xcode MCP `tools/list` in the repo's schema format.

Usage: capture_tools.py <mcpbridge path> <output.json> [--timeout SECONDS]
Set MCP_XCODE_PID to target a specific (windowed) Xcode instance.
Prints serverInfo and tool count to stderr.
"""
import argparse, json, subprocess, sys, threading

ap = argparse.ArgumentParser()
ap.add_argument("bridge")
ap.add_argument("output")
ap.add_argument("--timeout", type=float, default=120)
args = ap.parse_args()

p = subprocess.Popen([args.bridge], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
threading.Timer(args.timeout, p.kill).start()

def send(m):
    p.stdin.write(json.dumps(m) + "\n")
    p.stdin.flush()

def recv(i):
    while True:
        line = p.stdout.readline()
        if not line:
            sys.exit(f"bridge closed before response {i} (approval dialog? Xcode Tools disabled? timeout?)")
        m = json.loads(line)
        if m.get("id") == i:
            if "error" in m:
                sys.exit(f"error: {m['error']}")
            return m["result"]

send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "capture", "version": "1"}}})
print(json.dumps(recv(1).get("serverInfo")), file=sys.stderr)
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
tools = recv(2)["tools"]

# Repo format: indent 2, sorted keys, ASCII-escaped, no trailing newline
with open(args.output, "w") as f:
    json.dump({"tools": tools}, f, indent=2, sort_keys=True)
print(f"{len(tools)} tools", file=sys.stderr)
p.terminate()
sys.exit(0)
