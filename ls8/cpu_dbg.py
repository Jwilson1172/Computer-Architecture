from ls8.cpu import CPU
import sys

cpu = CPU(DBG=True)
cpu.load("./ls8/examples/sctest.ls8")
cpu.run()
