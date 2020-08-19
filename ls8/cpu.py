"""CPU functionality."""

import sys
from sys import argv
from time import time
import numpy as np
#from util import CpuMaths


class CPU:
    """Main CPU class."""

    # by default I want to make RAM 256 bytes this is the default for the ls-8
    # I also wanted to leave the option open for increasing the ram_size to
    # something larger to hold larger programs/stacks
    def __init__(self, DBG=False, ram_size=256):
        """Construct a new CPU."""
        if ram_size >= 4096:
            self.signed = True

        # set to NOP by default
        self.pc = 0

        # global toggle settings
        self.running = False

        # the IR register is just going to hold a copy of the PC reg
        self.ir = 0

        # init the interuption
        self.interruption_signal = 0b00000000
        self.interruption_mask = 0b00000000

        # stack pointer set to the 7th registry
        self.sp = 7
        # set the interuption mask pointer to the 5th registry
        self.im = 5

        # set the interruption status/signal as registry 6
        self.IS = 6

        # general pourpose registry for holding the arguments for the operations
        self.reg = [0] * 8

        # setting the stack pointer to the defualt location
        # made it scale off of ram size
        self.reg[self.sp] = ram_size - (256 - 0xf3)

        # set the interruption mask and signal as cleared
        self.reg[self.IS] = 0b00000000
        self.reg[self.im] = 0b00000000

        # from my understanding this part of the ram stores the address to
        # the interuption handler
        self.I_vectors = [0] * 8

        # int toggle
        self._w = False

        # flag register
        self.fl = 0

        # initalize the hash table that will be acting as ram
        self.RAM = {k: None for k in range(ram_size)}

        # global debugging toggle
        self.DBG = DBG

        self.clock = 0

    def ram_read(self, address):
        return self.RAM[address]

    def ram_write(self, address, value):
        self.RAM[address] = value
        return

    ###########################################################################
    #                        Instructions                                     #
    ###########################################################################

    JMP = 0b01010100
    LDI = 0b10000010
    NOP = 0b00000000
    HLT = 0b00000001
    INT = 0b01010010

    # printing instructions
    PRN = 0b01000111
    PRA = 0b01001000
    # supported cmp jumps
    JEQ = 0b01010101
    JNE = 0b01010110
    # other cmp jumps
    JGT = 0b01010111
    JGE = 0b01011010
    JLE = 0b01011001
    JLT = 0b01011000
    # counter
    DEC = 0b01100110
    INC = 0b01100101
    # compare
    CMP = 0b10100111
    # shifting
    SHL = 0b10101100
    SHR = 0b10101101
    # arithmetic
    MUL = 0b10100010
    MOD = 0b10100100
    DIV = 0b10100011
    SUB = 0b10100001
    ADD = 0b10100000
    MLP = 0b10100010
    # logic
    OR = 0b10101010
    NOT = 0b01101001
    XOR = 0b10101011
    AND = 0b10101000
    # ram
    LD = 0b10000011
    ST = 0b10000100
    # stack
    PUSH = 0b01000101
    POP = 0b01000110
    # coroutines
    RET = 0b00010001
    CALL = 0b01010000

    # 16bit instructions
    # 0b000000000 0  0  0  0  0  0  0
    # 0b123456789 10 11 12 13 14 15 16

    # for functions use 0b01
    # 0b0100000000000000

    # for markers or flags use 0b10
    # 0b1000000000000000

    ARRAY_START = 0b1000000000000000
    ARRAY_STOP = 0b1000000000000001

    LOAD_A = 0b0100000000000000
    MEAN = 0b0100000000000010

    ###########################################################################
    #                        Instruction Functions                            #
    ###########################################################################

    # Logic
    def instr_or(self):
        """Perform a bitwise-OR between the values in registerA and registerB,
        storing the result in registerA"""
        self.reg[self.ram_read(self.pc +
                               1)] |= self.reg[self.ram_read(self.pc + 2)]
        return

    def instr_and(self):
        """REG[A] = AND(REG[A],REG[B])"""
        self.reg[self.ram_read(self.pc +
                               1)] &= self.reg[self.ram_read(self.pc + 2)]
        return

    def instr_xor(self):
        """REG[A] = XOR(REG[A],REG[B])"""
        self.reg[self.ram_read(self.pc +
                               1)] ^= self.reg[self.ram_read(self.pc + 2)]
        return

    def instr_not(self):
        """REG[A] = ~REG[A]"""
        self.reg[self.ram_read(self.pc +
                               1)] = ~self.reg[self.ram_read(self.pc + 1)]
        return

    # stacks
    def pop(self):
        """take the value from the top of the stack and load it into the
        register that is specified byself.pc+ 1
        """
        # not quite sure how to handle the underflow
        # of the stack but for now we can hlt
        #@TODO
        if self.reg[self.sp] >= 0xf3:
            print("STACK UNDERFLOW DETECTED")
            self.hlt()
            return
        # get the value from the stack
        stack_value = self.ram_read(self.reg[self.sp])
        # get the target register from ram
        register_number = self.ram_read(self.pc + 1)
        # set the value of the register = to the value pulled off the stack
        self.reg[register_number] = stack_value
        # increment the stack pointer
        self.reg[self.sp] += 1
        # increment the program counter
        self.pc += 2
        return

    def push(self):
        """loads the args from the ram usingself.pc+ 1,2 respectively
        then write the value from the register to the top of the stack then
        decrement the stack and advance the pc"""
        # @TODO
        if self.reg[self.sp] <= self.pc:
            print("OverFlow Detected: HALTING")
            self.hlt()
            return
        # decrement the stack pointer
        self.reg[self.sp] -= 1
        # get the current stack pointer
        stack_address = self.reg[self.sp]
        # get the register number from ram
        register_number = self.ram_read(self.pc + 1)
        # pull the data  value from the register
        value = self.reg[register_number]
        # write value to the stack address
        self.ram_write(stack_address, value)
        # inc. program counter
        self.pc += 2
        return

    # subroutines
    def call(self):
        # decrement the stack pointer
        self.reg[self.sp] -= 1
        # get the current stack pointer value
        stack_address = self.reg[self.sp]
        # address of the next instr to return to
        returned_address = self.pc + 2
        #  write to the stack address with the value of return address
        self.ram_write(stack_address, returned_address)
        # get the register number from ram
        register_number = self.ram_read(self.pc + 1)
        # set the current program counter to the value stored in the register
        self.pc = self.reg[register_number]
        return

    def ret(self):
        # pull the return address from the stack and set the current program
        # counter to that address
        self.pc = self.ram_read(self.reg[self.sp])
        # increment the stack pointer
        self.reg[self.sp] += 1
        return

    # other operators
    def prn(self):
        """prints value in register PC + 1,
        then increments the program counter."""

        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2
        return

    def pra(self):
        print(chr(self.reg[self.ram_read(self.pc + 1)]))
        self.pc += 2

    def nop(self):
        """Does nothing, advances the PC"""
        self.pc += 1
        return

    def hlt(self):
        """Signals the run while loop to stop"""
        self.running = False
        self.pc += 1
        return

    def jmp(self) -> None:
        """Jump to location provided in register"""
        self.pc = self.reg[self.ram_read(self.pc + 1)]
        return

    def ldi(self):
        """f(A,B) | REG[A] = B, PC +3"""
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3
        return

    def st(self):
        """f(A,B) | RAM[REG[B]] = REG[A]"""
        reg_a, reg_b = self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)
        self.ram_write(self.reg[reg_b], self.reg[reg_a])
        self.pc += 3
        return

    # alu instructions
    def alu(self, operation, reg_a, reg_b):
        """ALU operations."""

        if operation == self.ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif operation == self.SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif operation == self.MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif operation == self.DIV:
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("ALU operation not supported")

    def add(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(self.ir, reg_a, reg_b)
        self.pc += 3
        return

    def sub(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(self.ir, reg_a, reg_b)
        self.pc += 3
        return

    def mul(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(self.ir, reg_a, reg_b)
        self.pc += 3
        return

    def div(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(self.ir, reg_a, reg_b)
        self.pc += 3
        return

    def mod(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.reg[reg_a] %= self.reg[reg_b]
        self.pc += 3
        return

    def jeq(self):
        """Jump to address stored in REG[PC +1] if the equals flag (self.fl) is set"""
        if not self.fl & 0b1:
            self.pc += 2
        elif self.fl & 0B1:
            reg_a = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_a]
        return

    def jne(self):
        """same as jeq but jumps on not equal"""
        if self.fl & 0b1:
            self.pc += 2
        elif not self.fl & 0b0:
            reg_a = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_a]
        return

    def shl(self):
        # get both of the registers
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        # shift the reg_a by the amount stored in reg_b
        self.reg[reg_a] <<= self.reg[reg_b]
        # advance pc
        self.pc += 3
        return

    def shr(self):
        # get both of the registers
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.read_ram(self.pc + 2)
        # shift the value in the first registry by the value in the second
        # registry and store the result in the reg_a
        self.reg[reg_a] >>= self.reg[reg_b]
        # advance pc
        self.pc += 3
        return

    def inc(self):
        # increment the register that is passed in ram
        self.reg[self.ram_read(self.pc + 1)] += 1
        # increment the pc
        self.pc += 2
        return

    def dec(self):
        # decrement the register that is passed in ram
        self.reg[self.ram_read(self.pc + 1)] -= 1
        self.pc += 2
        return

    def cmp(self) -> None:
        """This Function takes the regerister arguments and sets the flag register
        accordingly see the spec for a breakdown on the flags
        """
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        value_a = self.reg[reg_a]
        value_b = self.reg[reg_b]
        if value_a == value_b:
            self.fl = 0b1
        elif value_a > value_b:
            self.fl = 0b10
        elif value_b > value_a:
            self.fl = 0b100
        self.pc += 3
        return

    def ld(self):
        # Loads registerA with the value at the memory address
        # stored in registerB.
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(
            self.reg[self.ram_read(self.pc + 2)])
        self.pc += 3

        return

    def inter(self):
        # if INTS ar disabled do nothing
        if self._w:
            pass
        else:
            # issue the interupt number stored in the register
            # toggle the interuption bool that will trigger the main loop to hook
            self._w = True
            # get the interupt number from the register
            interupt_number = self.reg[self.ram_read(self.pc + 1)]
            self.ram_read()
        return

    def read_array(self):
        # reads an array from memory and stores the resulting list object in register specified
        # read_array R#, ARRAY_START (flag)
        register = self.ram_read(self.pc + 1)
        i = 2
        a = []
        # starting with the ARRAY_START flag and ending with the STOP flag load
        while True:
            next_instr = self.ram_read(self.pc + i)
            a.append(next_instr)
            if next_instr == self.ARRAY_STOP:
                break
            i += 1

        # store the resulting array in the register specified by arg
        self.reg[register] = a

        # since we just went n number of spots collecting memebers of the array
        # we need to skip to the next instruction
        self.pc = i + 1

    def mean(self):
        """takes the mean of the array in REG[A] and stores the value at REG[B]"""
        # use numpy to take the mean of the array
        b = np.mean(self.reg[self.ram_read(self.pc + 1)])
        # get the register address to store the value
        reg = self.reg[self.ram_read(self.pc + 2)]
        # set that register equal to the value
        self.reg[reg] = b
        # increment the pc
        self.pc += 3

        return

    ###########################################################################
    #                          UTIL FUNCTIONS                                 #
    ###########################################################################
    def trace(self):
        print(f"""
        pc: {self.pc}\

        main loop iter: {self.clock}
        ir: {self.ir}
        self.pc+ 1: {self.RAM[self.pc + 1]}
        self.pc+ 2: {self.RAM[self.pc + 2]}
        registry values:\n{self.reg}\n
        stack(top):\n{self.ram_read(self.reg[self.sp])}

        """)
        return

    def load(self, fn):
        """Loads a .ls8 file from disk and runs it

        Args:
            fn: the name of the file to load into memory

        """
        address = 0
        with open(fn, 'rt') as f:
            for line in f:
                try:
                    line = line.split("#", 1)[0]
                    line = int(line, base=2)
                    self.RAM[address] = line
                    address += 1
                except ValueError:
                    pass
        # for reloading
        self._file_fn = fn
        return

    def reset(self, *args, **kwargs):
        self.__init__(args, kwargs)
        return

    ###########################################################################
    #                              MAIN                                       #
    ###########################################################################
    def run(self):
        """Starts the main execution of the program"""
        self.running = True
        self.dispatch = {
            self.ADD: self.add,
            self.SUB: self.sub,
            self.MUL: self.mul,
            self.DIV: self.div,
            self.JEQ: self.jeq,
            self.JNE: self.jne,
            self.CMP: self.cmp,
            self.MOD: self.mod,
            self.LDI: self.ldi,
            self.PRN: self.prn,
            self.PRA: self.pra,
            self.HLT: self.hlt,
            self.NOP: self.nop,
            self.PUSH: self.push,
            self.POP: self.pop,
            self.CALL: self.call,
            self.RET: self.ret,
            self.DEC: self.dec,
            self.INC: self.inc,
            self.JMP: self.jmp,
            self.ST: self.st,
            self.LD: self.ld,
            self.INT: self.inter,
            self.OR: self.instr_or,
            self.NOT: self.instr_not,
            self.AND: self.instr_and,
            self.XOR: self.instr_xor,
        }

        self.secondary_dispatch = {
            self.ARRAY_START: self.nop,
            self.ARRAY_STOP: self.nop,
            self.LOAD_A: self.read_array,
            self.MEAN: self.mean,
        }
        while self.running:

            try:
                # absolute clock counter
                self.clock += 1
                # DBG HOOK
                if self.DBG:
                    # so that if i have an infinite loop there is a counter
                    print("CLK: {}".format(self.clock))
                    breakpoint()

                # read instruction and assign the ir register
                self.ir = self.ram_read(self.pc)
                # if the instruction is in the 8-bit table execute the command
                # from the 8-bit table
                if self.ir in self.dispatch:
                    self.dispatch[self.ir]()
                # or if it's in the 16bit then launch it from
                # that dispatch table
                elif self.ir in self.secondary_dispatch:
                    # if asking for 16-bit function and running in 8-bit mode
                    # switch to 16-bit mode by increasing the ram alloted to
                    # the __init__() then reload the program file that was being
                    # run and run it again
                    if self.signed is False:
                        program = self._file_fn
                        self.__init__(ram_size=4096)
                        self.load(program)
                        self.run()

                    self.secondary_dispatch[self.ir]()
                # if the instr isn't found then raise a targeted exception handler
                else:
                    raise KeyError

            # adding unknown instr error hook
            except KeyError as ke:
                print(f"unknown command: {int(self.ir, base=2)}")
                self.running = False

            # adding keyboard int
            except KeyboardInterrupt as kbi:
                self.running = False
                # @TODO figure out what goes here

                print("KeyBoardInt:")

        return None

    #Prior to instruction fetch, the following steps occur:
    #1. The IM register is bitwise AND-ed with the IS register and the
    #   results stored as `maskedInterrupts`.
    #2. Each bit of `maskedInterrupts` is checked, starting from 0 and going
    #   up to the 7th bit, one for each interrupt.
    #3. If a bit is found to be set, follow the next sequence of steps. Stop
    #   further checking of `maskedInterrupts`.
    #If a bit is set:
    #1. Disable further interrupts.
    #2. Clear the bit in the IS register.
    #3. The `PC` register is pushed on the stack.
    #4. The `FL` register is pushed on the stack.
    #5. Registers R0-R6 are pushed on the stack in that order.
    #6. The address (_vector_ in interrupt terminology) of the appropriate
    #   handler is looked up from the interrupt vector table.
    #7. Set the PC is set to the handler address.
    #While an interrupt is being serviced (between the handler being called
    #and the `IRET`), further interrupts are disabled.
    #
    #See `IRET`, below, for returning from an interrupt.
    #
    #### Interrupt numbers
    #
    #* 0: Timer interrupt. This interrupt triggers once per second.
    #* 1: Keyboard interrupt. This interrupt triggers when a key is pressed.
    #  The value of the key pressed is stored in address `0xF4`.
    #
    #```
    #      top of RAM
    #+-----------------------+
    #| FF  I7 vector         |    Interrupt vector table
    #| FE  I6 vector         |
    #| FD  I5 vector         |
    #| FC  I4 vector         |
    #| FB  I3 vector         |
    #| FA  I2 vector         |
    #| F9  I1 vector         |
    #| F8  I0 vector         |
    #| F7  Reserved          |
    #| F6  Reserved          |
    #| F5  Reserved          |
    #| F4  Key pressed       |    Holds the most recent key pressed on the keyboard
    #| F3  Start of Stack    |
    #| F2  [more stack]      |    Stack grows down
    #| ...                   |
    #| 01  [more program]    |
    #| 00  Program entry     |    Program loaded upward in memory starting at 0
    #+-----------------------+
    #    bottom of RAM
    #```
    ### INT
    #
    #`INT register`
    #
    #Issue the interrupt number stored in the given register.
    #
    #This will set the _n_th bit in the `IS` register to the value in the given
    #register.
    #
    #Machine code:
    #```
    #01010010 00000rrr
    #52 0r
    #```
    #
    #### IRET
    #
    #`IRET`
    #
    #Return from an interrupt handler.
    #
    #The following steps are executed:
    #
    #1. Registers R6-R0 are popped off the stack in that order.
    #2. The `FL` register is popped off the stack.
    #3. The return address is popped off the stack and stored in `PC`.
    #4. Interrupts are re-enabled
    #
    #Machine code:
    #```
    #00010011
    #13
    #```


def main():
    try:
        # init the cpu
        if '--DBG' in argv:
            cpu = CPU(DBG=True, ram_size=4096)
            # remove dbg flag from argv so it dosent
            # break loading ls8 files
            argv.pop('--DBG')
        else:
            cpu = CPU(DBG=False, ram_size=4096)

        if len(argv) > 1:
            print("Launching in multi-test mode:\n")
            for test in argv[1:]:
                print(test)
                now = time()
                cpu.reset()
                cpu.load(test)
                cpu.run()
                later = time()
                print(f"Exec Time: {later - now}/sec")
                print("\n")
        else:
            now = time()
            cpu.load('examples/sctest.ls8')
            cpu.run()
            later = time()
            print(f"Execution time: {later - now}/sec")
    except Exception as e:
        pass
    return


if __name__ == '__main__':
    main()
