#!/usr/bin/env python3
"""Main."""

import sys
from cpu import *

cpu = CPU(DBG=True)

cpu.load("./ls8/examples/sctest.ls8")
cpu.run()
