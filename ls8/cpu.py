"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 0xF4
        self.dispatch_table = {}
        self.dispatch_table[LDI] = self.handle_LDI
        self.dispatch_table[PRN] = self.handle_PRN
        self.dispatch_table[MUL] = self.handle_MUL
        self.dispatch_table[HLT] = self.handle_HLT
        self.dispatch_table[POP] = self.handle_POP
        self.dispatch_table[PUSH] = self.handle_PUSH
        self.alu_dispatch_table = {}
        self.alu_dispatch_table['ADD'] = self.alu_ADD
        self.alu_dispatch_table['MUL'] = self.alu_MUL
        self.running = True
        self.pc = 0

    def handle_LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_PRN(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def handle_MUL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def handle_HLT(self):
        self.running = False

    def handle_POP(self):
        operand_a = self.ram_read(self.pc + 1)
        if self.sp == 0xF4:
            print("Stack is empty")
            sys.exit(1)
        else:
            self.sp += 1
            self.reg[operand_a] = self.ram[self.sp]
            self.pc += 2

    def handle_PUSH(self):
        operand_a = self.ram_read(self.pc + 1)
        self.ram[self.sp] = self.reg[operand_a]
        self.sp -= 1
        self.pc += 2

    def alu_ADD(self, reg_a, reg_b):
        self.reg[reg_a] = (self.reg[reg_a] + self.reg[reg_b]) & 0xFF

    def alu_MUL(self, reg_a, reg_b):
        self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b]) & 0xFF

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        address = 0
        program = []
        try:
            with open(sys.argv[1]) as b:
                for line in b:
                    if line.startswith('0') | line.startswith('1'):
                        l = line.split('#')[0].strip()
                        number = int(l, 2)
                        program.append(number)
            for instruction in program:
                self.ram[address] = instruction
                address += 1
        except:
            print("Error!",sys.exc_info()[0],"present in load function.")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        try:
            self.alu_dispatch_table[op](reg_a, reg_b)
        except:
            print("Error!",sys.exc_info()[0],"present in alu function.")
            sys.exit(1)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            try:
                IR = self.ram[self.pc]
                self.dispatch_table[IR]()
            except:
                print("Error",sys.exc_info()[0],"present in run function.")
                sys.exit(1)