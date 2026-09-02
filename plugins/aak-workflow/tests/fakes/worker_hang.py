#!/usr/bin/env python3
"""Fake worker: prints nothing, sleeps forever, burns no CPU (idle hang)."""
import time
while True:
    time.sleep(3600)
