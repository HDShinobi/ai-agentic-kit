#!/usr/bin/env python3
"""Fake worker: silent on stdout but genuinely busy (simulates a long compile)."""
import time, sys
end = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else "2")
x = 0
while time.time() < end:
    x += 1  # burn CPU; no stdout
sys.stdout.write("Status: DONE\nRole: code\nModel: fake\nChanged paths:\n"
                 "Verification: build ok\nDisposition: ACCEPT\nEND OF HANDOFF\n")
sys.exit(0)
