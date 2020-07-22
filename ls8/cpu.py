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
        # CMP
        if op == 0b10100111:
            # adding the compare operation
            if reg_a == reg_b:
                self.fl = 0b00000001
            elif reg_a > reg_b:
                self.fl = 0b00000010
            elif reg_a < reg_b:
                self.fl = 0b00000100
            else:
                self.trace()
                raise Exception("fault with CMP operation")
        # AND
        elif op == 0b10101000:
            return reg_a & reg_b
        # NOP
        elif op == 0b00000000:
            pass
        # HLT
        elif op == 0b00000001:
            print("HALTING")
            exit()
        # LDI
        elif op == 0b10000010:
            # in this instance the second argument should be an int
            reg_b == int(reg_b, 10)
        # LD
        elif op == 0b10000011:
            # not sure what LD does going to implement later
            pass
        # ST
        elif op == 0b10000100:
            # again not sure what this does atm
            pass
        # PUSH
        elif op == 0b01000101:
            # this method should push a value onto a stack
            # I think that the stack is R7 which is that stack pointer register
            pass
        # POP
        elif op == 0b01000110:
            #Same thing as push but instead its poping a value off of a stack
            pass
        # PRN
        elif op == 0b01000111:
            print(reg_a)
            # PRA
        elif op == 0B01001000:
            # not sure what PRA does
            pass
        else:
            self.trace()
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address, upper_limit=1):
        """Returns the Data that is stored in the ram at `address` and reads
        `upper_limit` number of ram slots

        Args:
            address ([type]): [description]
            upper_limit (int, optional): [description]. Defaults to 1.

        Returns:
            entries from the ram hashtable
        """
        # using some fancy slicing here
        return self.RAM[address:(address + upper_limit)]

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


        return None

class LS8IO():
    def __init__(self, program_file: str, emulator: CPU):
        if program_file[-3] != 'ls8':
            print("please use an ls8 file type for the ls8 emulator")
        self.file = open(program_file, 'rb')

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
