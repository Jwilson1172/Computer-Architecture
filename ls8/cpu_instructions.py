class CPUInst(object):
    def __init__(self, CPU_obj):
        self.cpu = CPU_obj

        return

    ###########################################################################
    #                        Instructions Functions                           #
    ###########################################################################

    # stacks

    def pop(self):
        """take the value from the top of the stack and load it into the
        register that is specified byself.pc+ 1
        """
        stack_value = self.ram_read(self.reg[SP])
        register_number = self.ram_read(self.pc + 1)
        self.reg[register_number] = stack_value
        self.reg[SP] += 1
        self.pc += 2
        return

    def push(self):
        """loads the args from the ram usingself.pc+ 1,2 respectivly
        then write the value from the register to the top of the stack then
        decrement the stack and advance the pc"""
        # get the register from ram
        self.reg[SP] -= 1
        stack_address = self.reg[SP]
        register_number = self.ram_read(self.pc + 1)
        value = self.reg[register_number]
        self.ram_write(stack_address, value)
        self.pc += 2
        return

    # subroutines
    def call(self):
        self.reg[SP] -= 1
        stack_address = self.reg[SP]
        returned_address = self.pc + 2
        self.ram_write(stack_address, returned_address)
        register_number = self.ram_read(self.pc + 1)
        self.pc = self.reg[register_number]
        return

    def ret(self):
        self.pc = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
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
        exit(1)
        # no need to adnvance theself.pcbecause the progam is finished
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
        """Divides the value of reg_a by the value of the reg_b then store the
        result in reg_a"""

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

    # ALU
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
