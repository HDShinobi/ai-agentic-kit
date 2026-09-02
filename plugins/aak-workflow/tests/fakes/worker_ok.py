#!/usr/bin/env python3
"""Fake worker: prints a complete handoff and exits 0."""
import sys
sys.stdout.write("doing work\nStatus: DONE\nRole: code\nModel: fake\n"
                 "Changed paths:\nVerification: none\nDisposition: ACCEPT\n"
                 "END OF HANDOFF\n")
sys.exit(0)
