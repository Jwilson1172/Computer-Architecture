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
    def __init__(self, DBG=False, ram_size=256, cores=1):
        """Construct a new CPU."""
        # the location of the currently executing program
        if cores > 1:
            # this is added because at some point i would like to implement
            # a multiprocessing solution to this class
            raise NotImplementedError("this feature is not implemented please\
                please just use one core for now")

        # set to NOP by default
        self.pc = 0b00000000

        # the IR register is just going to hold a copy of the PC reg
        self.ir = self.pc

        # init the execution interupt registry
        self.ie = 0

        # stack pointer is going to be init to 0 but will change later in
        # self.run()
        self.sp = 4

        # general pourpose registry for holding the arguments for alu
        # operations
        self.reg = [] * 8

        # flag register
        self.fl = 0
        # initalize the hash table that will be acting as ram
        self.RAM = {k: None for k in range(ram_size)}

        # global debugging toggle
        self.DBG = DBG

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
#######################################################
#           ALU OPPERATIONS                           #
#######################################################

# before you harp on me about the type(0b00) its a dirty way of
# figuring out what the binary datatype is

    def alu(self, op: type(0b00), reg_a, reg_b) -> type(None):
        """ALU for the cpu that handles a veritity of operations preformed
        by the cpu, this method handles the `brains` of the cpu essentially
        Arguments:
        -----------
        `reg_a` : the first register to take from
        `reg_b` : the second register to act on
        `op` : a binary opperator that tells the alu what to execute

        * for CMP and some of the other operators this isn't nessisarly the case
        for instance during a LDI(op code: 0b10000010) operation the reg_b is
        the integer value that is going to be put on the reg_a aka op argument:
        iiiiiiii
        Returns:
        ------------
        type(None)
        (ideally this isn't going to return anything just modify the state of the internal vars)
        """
        # TODO
        # I plan on making this a dispach table using hashtable mechanics
        # to get O(1) lookup on executing the operators
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
            reg_a = reg_a & reg_b
        # NOP
        elif op == 0b00000000:
            # very litterally no operation
            pass
        # HLT
        elif op == 0b00000001:
            print("HALTING")
            if self.DBG:
                print("dumping ram:\n")
                self.dump_ram()
                print("dumping registers")
                self.dump_registers()
                print("printing out a full trace")
                self.trace()
            exit()
        # LDI
        elif op == 0b10000010:
            # the LDI operation takes the inteager value that is givin as a
            # second argument
            if isinstance(reg_b, int):
                # going to add the int value to the first register as a binary
                # representation of the integer value that is passed
                reg_a[self.PC] = int(reg_b, base=2)
                # increment the PC by one to denote that there has been a change
                self.PC += 1
            else:
                raise ValueError(
                    "the value of reg_b must be an integer for LDI\
                    to work properly")

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
        elif op == 0b01001000:
            # not sure what PRA does
            pass
        else:
            self.trace()
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        """Returns the Data that is stored in the ram at `address`

        Args:
            address ([type]): [description]

        Returns:
            entries from the ram hashtable
        """
        return self.RAM[address]

#############################################################
#           CPU DEBUGGING FUNCTIONS                         #
#############################################################

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

    def run(self):
        """Starts the main execution of the program"""
        running = True
        # a simple count to figure out how many times my cpu has cycled
        clock = 0
        while running:
            clock += 1
            # read next op from ram
            op = self.ram_read(self.pc)
            if self.DBG:
                self.trace()

            # set the IR to reflect the PC
            self.ir = op
            if self.DBG:
                self.trace()

            # unpack the arguments from the next two slots in ram
            a0, a1 = self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)
            if self.DBG:
                self.trace()

            # send the op and arguments to the alu
            self.alu(op, a0, a1)
            if self.DBG:
                self.trace()

            # going to want to increment past the arguments that were used
            # in the last operator
            self.pc += 3
            if self.DBG:
                self.trace()
                print(f"clock_num: {clock}")
        return None


#############################################################
#              SUPPORT FUNCTIONS/CLASSES                    #
#############################################################

if __name__ == '__main__':
    # init the cpu in debug mode with 256 bytes of ram and 1 compute core
    cpu = CPU(DBG=True, ram_size=256, cores=1)

    # load a file from the local directory to run
    p = cpu.load_file("./examples/print8.ls8")

    # execute the program by running the main loop in the run()
    # function for the cpu
    cpu.run()

    # hopefully the output of the print8.ls8 is going to be:
    # 8
