"""CPU functionality."""

import sys
from sys import argv
from time import time
#from util import CpuMaths


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
        self.reg[self.sp] = 0xf3

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
    PRN = 0b01000111
    ST = 0b10000100
    INT = 0b01010010

    # sc ops
    JEQ = 0b01010101
    JNE = 0b01010110

    # alu operations
    ADD = 0b10100000
    MLP = 0b10100010
    DIV = 0b10100011
    DEC = 0b01100110
    INC = 0b01100101
    CMP = 0b10100111
    AND = 0b10101000
    NOT = 0b01101001
    SUB = 0b10100001
    SHL = 0b10101100
    SHR = 0b10101101
    MUL = 0b10100010
    MOD = 0b10100100
    OR = 0b10101010
    LD = 0b10000011
    # stack
    PUSH = 0b01000101
    POP = 0b01000110

    # coroutines
    RET = 0b00010001
    CALL = 0b01010000

    # custom functions using arrays
    START_ARR = 0b111111101
    END_ARR = 0b1111111110

    ###########################################################################
    #                        Dispatch Table                                   #
    ###########################################################################
    dispatch = {
        ADD: add,
        SUB: sub,
        MUL: mul,
        DIV: div,
        JEQ: jeq,
        JNE: jne,
        CMP: cmp,
        MOD: mod,  # end alu instructions
        LDI: ldi,
        PRN: prn,
        HLT: hlt,
        NOP: nop,  # end other instructions
        PUSH: push,
        POP: pop,  # end stack instructions
        CALL: call,
        RET: ret,  # end subroutine instructions
        DEC: dec,  # adding increment and decrement instructions
        INC: inc,
        JMP: jmp,
        ST: st,
        LD: ld,
        INT: inter,
    }

    ###########################################################################
    #                        Instruction Functions                            #
    ###########################################################################

    # stacks

    def pop(self):
        """take the value from the top of the stack and load it into the
        register that is specified byself.pc+ 1
        """
        # not quite sure how to handle the underflow
        # of the stack but for now we can hlt
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

        stack_address = self.reg[self.sp]
        returned_address = self.pc + 2
        self.ram_write(stack_address, returned_address)
        register_number = self.ram_read(self.pc + 1)
        self.pc = self.reg[register_number]
        return

    def ret(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        return

    # other operators
    def prn(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2
        return

    def nop(self):
        # still going to want to advance the pc
        self.pc += 1
        return

    def hlt(self):
        self.running = False
        self.pc += 1
        return

    def jmp(self) -> None:
        # load the address to jump to
        reg = self.ram_read(self.pc + 1)
        # set the new location for pc
        self.pc = self.reg[reg]

        return

    def ldi(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3
        return

    def st(self):
        """Takes the value stored in reg_a and writes it to the address that is
        stored in reg_b then increments theself.pcby three.
        """
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
        if not self.fl & 0b1:
            self.pc += 2
        elif self.fl & 0B1:
            reg_a = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_a]
        return

    def jne(self):
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
        print("NOT FULLY IMPLEMENTED!!")
        # issue the interupt number stored in the register
        # toggle the interuption bool that will trigger the main loop to hook
        self._w = True
        # get the interupt number from the register
        raise_number = self.reg[self.ram_read(self.pc + 1)]
        print(
            f"DBG: the value in register {self.ram_read(self.pc + 1)} is {raise_number}"
        )
        breakpoint()
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

    def reset(self):
        self.__init__()
        return

    ###########################################################################
    #                              MAIN                                       #
    ###########################################################################
    def run(self):
        """Starts the main execution of the program"""
        self.running = True
        self.clock = 0

        while self.running:

            try:
                # absolute clock counter
                self.clock += 1

                # DBG HOOK
                if self.DBG:
                    # so that if i have an infinite loop there is a counter
                    print("CLK: {}".format(self.clock))
                    breakpoint()

                # INTERUPTION HOOK
                if self._w:
                    # @TODO add int hook here
                    pass

                # read instruction and assign the ir register
                self.ir = self.ram_read(self.pc)
                # execute instruction
                self.dispatch[self.ir]()

            # adding unknown instr error hook
            except KeyError as ke:
                print(f"error instruction {self.ir} not in dispatch table")
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
    return


def main():
    try:
        # init the cpu
        cpu = CPU(DBG=False)
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
            cpu.load('examples/stack.ls8')
            cpu.run()
            later = time()
            print(f"Execution time: {later - now}/sec")
    except Exception as e:
        pass
    return


if __name__ == '__main__':
    testing()
