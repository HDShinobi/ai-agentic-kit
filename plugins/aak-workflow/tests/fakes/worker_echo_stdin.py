#!/usr/bin/env python3
"""Fake worker: reads all of stdin and echoes it before a valid handoff block
(Ruling B — codex-style adapters read their prompt from stdin, not a CLI arg).
"""
import sys
data = sys.stdin.read()
sys.stdout.write(f"stdin={data}\n")
sys.stdout.write("Status: DONE\nRole: code\nModel: fake\nChanged paths:\n"
                 "Verification: none\nDisposition: ACCEPT\nEND OF HANDOFF\n")
sys.exit(0)
