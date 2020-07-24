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

    # by default I want to make RAM 256 bytes this is the default for the ls-8
    # I also wanted to leave the option open for increasing the ram_size to
    # something larger to hold larger programs/stacks
    def __init__(self, DBG=False, ram_size=256):
        """Construct a new CPU."""
        # set to NOP by default
        self.pc = 0

        # global toggle settings
        self.running = False

        # the IR register is just going to hold a copy of the PC reg
        self.ir = 0

        # init the execution interupt registry
        self.ie = 0

        # stack pointer set to the 7th registry
        self.sp = 7

        # general pourpose registry for holding the arguments for the operations
        self.reg = [0] * 8

        # flag register
        self.fl = 0

        # initalize the hash table that will be acting as ram
        self.RAM = {k: None for k in range(ram_size)}

        # global debugging toggle
        self.DBG = DBG

    ###########################################################################
    #                        Instructions                                     #
    ###########################################################################
    JMP = 0b01010100
    JEQ = 0b01010101
    JNE = 0b01010110
    JGT = 0b01010111
    JLT = 0b01011000
    JLE = 0b01011001
    JGE = 0b01011010
    NOP = 0b00000000
    HLT = 0b00000001
    LDI = 0b10000010
    LD = 0b10000011
    ST = 0b10000100
    PRN = 0b01000111
    PRA = 0b01001000

    # alu operations
    ADD = 0b10100000
    MLP = 0b10100010
    DIV = 0b10100011
    DEC = 0b01100110
    CMP = 0b10100111
    AND = 0b10101000
    NOT = 0b01101001
    SUB = 0b10100001
    SHL = 0b10101100
    SHR = 0b10101101

    # stack
    PUSH = 0b01000101
    POP = 0b01000110

    ###########################################################################
    #                        Instructions Functions                           #
    ###########################################################################

    def cmp(self, reg_a, reg_b) -> None:
        """This Function takes the regerister arguments and sets the flag register
        accordingly see tyhe spec for a breakdown on the flags
        """
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
        return None

    def jmp(self, address) -> None:
        self.pc = address
        return None

    def nop(self):
        return

    def hlt(self):
        self.running = False
        return

    def ldi(self, reg_a, reg_b):
        return

    def aand(self, reg_a, reg_b):
        self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        return

    def prn(self, reg_a, reg_b):
        print(self.reg[reg_a])
        return

    def load(self, p):
        """Load a program into memory."""
        # changing this number of the binary form of the int to I can have
        # consitencey in the program execution
        address = 0b00

        for instruction in p:
            self.ram[address] = instruction
            address += 1

    def load_file(self, fn):
        """Loads a .ls8 file from disk and runs it

        Args:
            fn: the name of the file to load into memory
        """
        address = 0b00
        with open(fn, 'rt') as f:
            for line in f:
                try:
                    line = line.split("#", 1)[0]
                    line = int(line, base=2)
                    self.RAM[address] = line
                    address += 1
                except ValueError:
                    pass

    ###########################################################################
    #                       ALU OPPERATIONS                                   #
    ###########################################################################

    def alu(self, op: int, reg_a, reg_b) -> type(None):
        """ALU for the cpu that handles a veritity of operations preformed
        by the cpu, this method handles the `brains` of the cpu essentially
        Arguments:
        -----------
        `reg_a` : the first register to take from
        `reg_b` : the second register to act on
        `op` : a binary opperator that tells the alu what to execute
        """
        self.dispatch_table = {
            self.JMP: self.jmp,
            self.NOP: self.nop,
            self.HLT: self.hlt,
            self.LDI: self.ldi,
            self.AND: self.aand,
            self.PRN: self.prn,
        }
        self.dispatch_table[op](reg_a, reg_b)
        return None

    def ram_read(self, address):
        """Returns the Data that is stored in the ram at `address`

        Args:
            address ([type]): [description]

        Returns:
            entries from the ram hashtable
        """
        return self.RAM[address]

    ###########################################################################
    #                 CPU DEBUGGING FUNCTIONS                                 #
    ###########################################################################

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" %
              (self.pc, self.ir, self.fl, self.ie, self.ram_read(self.pc),
               self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)),
              end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def dump_ram(self) -> dict:
        return self.RAM

    def dump_registers(self):
        for i in self.reg:
            print(i)
        return self.reg

    ###########################################################################
    #                              MAIN                                       #
    ###########################################################################
    def run(self):
        """Starts the main execution of the program"""
        self.running = True
        # a simple count to figure out how many times my cpu has cycled
        clock = 0
        while running:
        return None


if __name__ == '__main__':
    # init the cpu in debug mode with 256 bytes of ram and 1 compute core
    cpu = CPU()

    # load a file from the local directory to run
    p = cpu.load_file("./examples/print8.ls8")

    # execute the program by running the main loop in the run()
    # function for the cpu
    cpu.run()

    # hopefully the output of the print8.ls8 is going to be:
    # 8
