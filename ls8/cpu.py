"""CPU functionality."""

import sys
class Stack():
    def __init__(self, num: int) -> None:
        """set the size of the with the num argument"""
        if num <= 256:
            self.stack = [None] * num
        else:
            raise ValueError("STACK.size > 256")
        return None

    def push(self, value):
        self.stack.append(value)
        return

    def pop(self):
        if self.size() > 0:
            return self.stack.pop()
        else:
            return None

    def size(self):
        return len(self.stack)

class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        # program counter
        # the location of the currently executing program
        self.PC
        # Instruction Register
        # holds a copy of PC
        self.IR
        # initalize the hash table that will be acting as ram
        self.RAM = {k:None for k in range(256)}


    def load(self, p):
        """Load a program into memory."""
        address = 0

        for instruction in p:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |" % (
                self.pc,
                #self.fl,
                #self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2)),
            end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Starts the main execution of the program"""

        running = True
        while running:
            if op == 'HLT':
                running = False
                break
            op = input("input a command: ")

        return None


if __name__ == '__main__':
    # For now, we've just hardcoded a program:
    program = [
        # From print8.ls8
        0b10000010,  # LDI R0,8
        0b00000000,
        0b00001000,
        0b01000111,  # PRN R0
        0b00000000,
        0b00000001,  # HLT
    ]
    cpu = CPU()
    cpu.load(program)
    cpu.run()
