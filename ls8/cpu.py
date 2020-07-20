"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        # for speed I want to implement ram as a hashtable, because its
        # accurate to how ram works
        # this implementation is un-sized which means that it can be exploited
        # during execution I want to make sure that I check the size of this
        self.ram = {}
        # init a register
        self.reg = {}
        # init a program counter
        self.pc = 0

        # not sure if I need anything else here

    def load(self):
        """Load a program into memory."""
        # check if there is an alt adress to load into
        # (great to inject code into the runtime from pdb)
        if ALT_ADR != None:
            address = ALT_ADR
        # if there is not an injection address then just mount the program from
        # the first address, this will rewrite the ram for any program that
        # is running
        else:
            address = 0

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

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, addy):
        """Returns the content of a memory address
        Arguments:
        ----------
        `addy` {str or int} - the address to use to fetch data from the ram
        Returns:
        ----------
        data {Object} - the data that is stored in the ram at `addy`"""

        if isinstance(addy, list):
            raise ValueError("List is not an expected input to this function\n\
                please use a string or int")
        else:
            return self.ram[addy]

        # this should be unreachable code
        # but i still want to make my linter happy
        return None

    def ram_write(self, addy, d):
        """A function that takes some data then adds it at address `addy`
        Only compleats if the len(d) < len(free_ram) and
        ram[d.index.min() : d.index.max()] (has to fit)
        """

        # check if there is something already in that address
        if self.ram[addy] is not None:
            print(
                "the memory at the address of {addy} is already taken by another program"
            )
            print("Content of RAM[{addy}]:\n", self.ram[addy])
            return False

        # check to make sure that the ram can hold the data that is being loaded
        # eg os.sizeof(d) > 100Tb is obviously not going into ram,
        # this protects against overflows
        if len(self.ram) < len(d):
            print(
                "Overflow Killswitch got triggered, please use a smaller data\n\
                source or use a buffered reader if you are streaming from a file"
            )
            return False

        # if the d is a list or dict then i want to make sure that I copy the
        # whole d to a range of addresses using the starting address of `addy`
        # if its not a list or a dict(like a hardcoded program)
        # then justadd to that addy then return
        if (isinstance(d, list)) or (isinstance(d, dict)):
            # take each entry in d and append it to the ram
            for i in range(len(d)):
                self.ram[addy + i] = d[i]
            return True
        else:
            self.ram[addy]
            return True

        # should be unreachable code
        return False

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
        """Run the CPU."""
        pass
