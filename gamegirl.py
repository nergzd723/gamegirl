import threading
import sys
class GGCPU:
    class Registers:
        def __init__(self):
            self.a, self.b, self.c, self.d, self.e, self.h, self.l = 0,0,0,0,0,0,0
            self.flag_zero, self.flag_sub, self.flag_hc, self.flag_carry = False, False, False, False
            self.pc = 0x0
            self.sp = 0x0
        def af_read(self):
            return (self.a << 8) | self.f
        def bc_read(self):
            return (self.b << 8) | self.c
        def de_read(self):
            return (self.d << 8) | self.e
        def hl_read(self):
            return (self.h << 8) | self.l
        def af_write(self, value):
            self.a = (value & 0xFF00) >> 8
            self.f = value & 0xFF
        def bc_write(self, value):
            self.b = (value & 0xFF00) >> 8
            self.c = value & 0xFF
        def de_write(self, value):
            self.d = (value & 0xFF00) >> 8
            self.e = value & 0xFF
        def hl_write(self, value):
            self.h = (value & 0xFF00) >> 8
            self.l = value & 0xFF
    def __init__(self, mem):
        self.registers = self.Registers()
        self.memory = mem
    def updatePC(self, sizeB):
        #print("updatePC: was at {} pointed at {} now at {} points at {}".format(hex(self.registers.pc), hex(self.memory.memory[self.registers.pc]), hex(self.registers.pc+sizeB), hex(self.memory.memory[self.registers.pc+sizeB])))
        self.registers.pc = self.registers.pc + sizeB
    def getInstruction(self):
        return self.memory.readb(self.registers.pc)
    def bit(self, a, bit):
        bit = 1 << bit
        if a & bit:
            self.registers.flag_zero = 0
        else:
            self.registers.flag_zero = 1
        self.registers.flag_sub = 0
        self.registers.flag_hc = 1
    def setb(self, bit, number):
        number_with_bit_set = 1 << bit
        number = number | number_with_bit_set
        return number
    def step(self):
        instruction = self.getInstruction()
        nn = self.memory.readb(self.registers.pc+2) << 8 | self.memory.readb(self.registers.pc+1)
        n = self.memory.readb(self.registers.pc+1)
        HACK = False
        sys.stdout.write(hex(self.registers.pc)+": ")
        if instruction == 0x0:
            print("NOP")
            print(self.memory.memory)
            print(hex(n), hex(nn), hex(self.getInstruction()))
            while True:
                pass
            self.updatePC(1)
        elif instruction == 0xdf:
            print("RST 18")
            self.updatePC(1)
            self.memory.stack.append(self.registers.pc)
            self.registers.pc = 0x18
        elif instruction == 0xef:
            print("RST 28")
            self.updatePC(1)
            self.memory.stack.append(self.registers.pc)
            self.registers.pc = 0x28
        elif instruction == 0xf3:
            print("DI")
            self.memory.writeb(0xFFFF, 0)
            # TODO
            self.updatePC(1)
        elif instruction == 0xfb:
            print("EI")
            self.memory.writeb(0xFFFF, 1)
            # TODO
            self.updatePC(1)
        elif instruction == 0x6:
            print("LD B, n")
            self.registers.b = n
            self.updatePC(2)
        elif instruction == 0x2e:
            print("LD L, n")
            self.registers.l = n
            self.updatePC(2)
        elif instruction == 0x26:
            print("LD H, n")
            self.registers.h = n
            self.updatePC(2)
        elif instruction == 0x11:
            print("LD DE, nn")
            self.registers.de_write(nn)
            self.updatePC(3)
        elif instruction == 0x01:
            print("LD BC, nn")
            self.registers.bc_write(nn)
            self.updatePC(3)
        elif instruction == 0x22:
            print("LDI (HL), a")
            #print("writing {} to {}".format(hex(self.registers.hl_read()), hex(self.registers.a)))
            self.memory.writeb(self.registers.hl_read(), self.registers.a)
            self.registers.hl_write(self.registers.hl_read()+1)
            self.updatePC(1)
        elif instruction == 0x78:
            print("LD A, B")
            self.registers.a = self.registers.b
            self.updatePC(1)
        elif instruction == 0x67:
            print("LD H, A")
            self.registers.h = self.registers.a
            self.updatePC(1)
        elif instruction == 0x7b:
            print("LD A, E")
            self.registers.a = self.registers.e
            self.updatePC(1)
        elif instruction == 0x7c:
            print("LD A, H")
            self.registers.a = self.registers.h
            self.updatePC(1)
        elif instruction == 0x7a:
            print("LD A, D")
            self.registers.a = self.registers.d
            self.updatePC(1)
        elif instruction == 0x7d:
            print("LD A, L")
            self.registers.a = self.registers.l
            self.updatePC(1)
        elif instruction == 0x6f:
            print("LD L, A")
            self.registers.l = self.registers.a
            self.updatePC(1)
        elif instruction == 0x50:
            print("LD D, B")
            self.registers.d = self.registers.b
            self.updatePC(1)
        elif instruction == 0x40:
            print("LD B, B")
            self.registers.b = self.registers.b
            self.updatePC(1)
        elif instruction == 0x41:
            print("LD B, C")
            self.registers.b = self.registers.c
            self.updatePC(1)
        elif instruction == 0x16:
            print("LD D, n")
            self.registers.d = n
            self.updatePC(2)
        elif instruction == 0x87:
            print("ADD A, A")
            if (self.registers.a & 0xF) + (self.registers.a & 0xF) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a = self.registers.a + self.registers.a
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a &= 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x79:
            print("LD A, C")
            self.registers.a = self.registers.c
            self.updatePC(1)
        elif instruction == 0xb1:
            print("OR C")
            self.registers.a |= self.registers.c
            if self.registers.a:
                self.registers.flag_zero = False
            else:
                self.registers.flag_zero = True
            self.registers.flag_sub = False
            self.registers.flag_hc = True
            self.registers.flag_carry = False
            self.updatePC(1)
        elif instruction == 0xa6:
            print("AND (HL)")
            self.registers.a &= self.memory.readb(self.registers.hl_read())
            if self.registers.a:
                self.registers.flag_zero = True # REVERSE ME PLZ
            else:
                self.registers.flag_zero = False # REVERSE ME
            self.registers.flag_sub = False
            self.registers.flag_hc = False
            self.registers.flag_carry = False
            self.updatePC(1)
        elif instruction == 0xa7:
            print("AND A")
            self.registers.a &= self.registers.a
            if self.registers.a:
                self.registers.flag_zero = True # REVERSE ME PLZ
            else:
                self.registers.flag_zero = False # REVERSE ME
            self.registers.flag_sub = False
            self.registers.flag_hc = False
            self.registers.flag_carry = False
            self.updatePC(1)
        elif instruction == 0xe6:
            print("AND n")
            self.registers.a &= n
            if self.registers.a:
                self.registers.flag_zero = False
            else:
                self.registers.flag_zero = True
            self.registers.flag_sub = False
            self.registers.flag_hc = False
            self.registers.flag_carry = False
            self.updatePC(2)
        elif instruction == 0x13:
            print("INC DE")
            # FIXME
            self.registers.de_write(self.registers.de_read()+1)
            self.updatePC(1)
        elif instruction == 0x35:
            print("DEC, (HL)")
            n = self.memory.readb(self.registers.hl_read())
            if n - 1 < 0xFF:
                n &= 0xFF
            n = n-1
            self.memory.writeb(self.registers.hl_read(), n)
            self.updatePC(1)
        elif instruction == 0x34:
            print("INC, (HL)")
            n = self.memory.readb(self.registers.hl_read())
            if n + 1 > 0xFF:
                n &= 0xFF
            n = n+1
            self.memory.writeb(self.registers.hl_read(), n)
            self.updatePC(1)
        elif instruction == 0x0b:
            print("DEC BC")
            self.registers.bc_write(self.registers.bc_read()-1)
            self.updatePC(1)
        elif instruction == 0x1a:
            print("LD a, (de)")
            self.registers.a = self.memory.readb(self.registers.de_read())
            self.updatePC(1)
        elif instruction == 0x0a:
            print("LD a, (bc)")
            self.registers.a = self.memory.readb(self.registers.bc_read())
            self.updatePC(1)
        elif instruction == 0x5e:
            print("LD E, (HL)")
            self.registers.e = self.memory.readb(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0xcf:
            print("RST 8")
            self.updatePC(1)
            self.memory.stack.append(self.registers.pc)
            self.registers.pc = 0x8
        elif instruction == 0x20:
            print("JR NZ, n")
            if not self.registers.flag_zero:
                self.updatePC((n ^ 0x80) - 0x80)
            self.updatePC(2)
        elif instruction == 0x57:
            print("LD D, A")
            self.registers.d = self.registers.a
            self.updatePC(1)
        elif instruction == 0x5f:
            print("LD E, A")
            self.registers.e = self.registers.a
            self.updatePC(1)
        elif instruction == 0xd4:
            print("CALL NC, nn")
            self.updatePC(3)
            if not self.registers.flag_carry:
                self.memory.stack.append(self.registers.pc)
                self.registers.pc = nn
        elif instruction == 0xd5:
            print("PUSH DE")
            self.memory.stack.append(self.registers.de_read())
            self.updatePC(1)
        elif instruction == 0xcd:
            print("CALL nn")
            self.updatePC(3)
            self.memory.stack.append(self.registers.pc)
            self.registers.pc = nn
        elif instruction == 0xc9:
            print("RET")
            self.registers.pc = self.memory.stack.pop()
        elif instruction == 0x1f:
            print("RR A")
            self.registers.a = (self.registers.a >> 1) + (self.registers.flag_carry << 7) + ((self.registers.a & 0x1) << 8)
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
            else:
                self.registers.flag_carry = False
            self.registers.a = self.registers.a & 0xFF
            self.updatePC(1)
        elif instruction == 0xc5:
            print("PUSH bc")
            self.memory.stack.append(self.registers.bc_read())
            self.updatePC(1)
        elif instruction == 0xe5:
            print("PUSH HL")
            self.memory.stack.append(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0x4f:
            print("LD C, A")
            self.registers.c = self.registers.a
            self.updatePC(1)
        elif instruction == 0x28:
            print("JR Z, n")
            self.updatePC(2)
            if self.registers.flag_zero:
                self.updatePC((n ^ 0x80) - 0x80)
        elif instruction == 0x2a:
            print("LDI a, (hl)")
            self.registers.a = self.memory.readb(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0x18:
            print("JR n")
            self.updatePC(2)
            self.updatePC((n ^ 0x80) - 0x80)
            if (n ^ 0x80) - 0x80 == -2:
                print("infinite loop")
                while True:
                    pass
        elif instruction == 0x07:
            print("RLC A")
            self.registers.a = (self.registers.a << 1) + (self.registers.a >> 7)
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            if self.registers.a > 0xFF:
                self.registers.a &= 0xFF
                self.registers.flag_carry = True
            else:
                self.registers.flag_carry = False
            self.updatePC(1)
        elif instruction == 0x3e:
            print("LD a, n")
            self.registers.a = n
            self.updatePC(2)
        elif instruction == 0x08:
            print("LD (nn), SP")
            self.memory.writeb(nn, self.registers.sp & 0xFF)
            self.memory.memory(nn+1, (self.registers.sp & 0xFF00) >> 8)
            self.updatePC(3)
        elif instruction == 0x88:
            print("ADC A, B")
            self.registers.a = self.registers.a + self.registers.b + self.registers.flag_carry
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a = self.registers.a & 0xFF
            if (self.registers.a & 0xF) > 0xF: # THIS IS PROBABLY SO WRONG, NEED TO CHECK a & 0xf + b & 0xf + carry THEN MAYBE IT'D BE FINE
                self.registers.flag_hc = True
            if self.registers.a == 0:
                self.registers.flag_zero = True
            self.updatePC(1)
        elif instruction == 0x89:
            print("ADC A, C")
            self.registers.a = self.registers.a + self.registers.c + self.registers.flag_carry
            print(hex(self.registers.a), hex(self.registers.c), hex(self.registers.flag_carry))
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a = self.registers.a & 0xFF
            if (self.registers.a & 0xF) > 0xF: # THIS IS PROBABLY SO WRONG, NEED TO CHECK a & 0xf + c & 0xf + carry THEN MAYBE IT'D BE FINE
                self.registers.flag_hc = True
            if self.registers.a == 0:
                self.registers.flag_zero = True
            self.updatePC(1)
        elif instruction == 0x0e:
            print("LD C, n")
            self.registers.c = n
            self.updatePC(2)
        elif instruction == 0xcc:
            print("CALL Z, nn")
            print("ADDRESS ", hex(nn))
            if self.registers.flag_zero:
                self.memory.stack.append(self.registers.pc)
                self.registers.pc = nn
            self.updatePC(3)
        elif instruction == 0x03:
            print("INC BC")
            # FIXME
            self.registers.bc_write(self.registers.bc_read()+1)
            if self.registers.bc_read() > 0xFFFF:
                self.registers.flag_carry = True
                self.registers.bc_write(self.registers.bc_read() & 0xFFFF)
            else:
                self.registers.flag_carry = False
            if self.registers.bc_read() == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x23:
            print("INC HL")
            # FIXME
            self.registers.hl_write(self.registers.hl_read()+1)
            if self.registers.hl_read() > 0xFFFF:
                self.registers.flag_carry = True
                self.registers.hl_write(self.registers.hl_read() & 0xFFFF)
            else:
                self.registers.flag_carry = False
            if self.registers.hl_read() == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x02:
            print("LD (BC), A")
            self.registers.a = self.memory.readb(self.registers.bc_read())
            self.updatePC(1)
        elif instruction == 0x0c:
            print("INC C")
            if (self.registers.c & 0xF) + (1 & 0xF) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.c += 1
            if self.registers.c > 0xFF:
                self.registers.c &= 0xFF
                self.registers.flag_carry = True
            else:
                self.registers.flag_carry = False
            if self.registers.c == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x2c:
            print("INC L")
            if (self.registers.l & 0xF) + (1 & 0xF) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.l += 1
            if self.registers.l == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x3c:
            print("INC A")
            if (self.registers.a & 0xF) + (1 & 0xF) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a += 1
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x0d:
            print("DEC C")
            if (self.registers.c & 0xF) - (1 & 0xF) < 0:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.c -= 1
            if self.registers.c < 0:
                self.registers.flag_carry = True
                self.registers.c &= 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.c == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0xc3:
            print("JMP nn")
            location = nn
            self.registers.pc = location
            print("Now at", hex(self.registers.pc))
        elif instruction == 0xe9:
            print("JP (HL)")
            self.registers.pc = self.registers.hl_read()
        elif instruction == 0xfa:
            print("LD A, (nn)")
            self.registers.a = self.memory.readb(nn)
            self.updatePC(3)
        elif instruction == 0x3d:
            print("DEC A")
            if (self.registers.a & 0xF) - (1 & 0xF) < 0:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a -= 1
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0xca:
            print("JP Z, nn")
            if self.registers.flag_zero:
                self.registers.pc = nn
            else:
                self.updatePC(3)
        elif instruction == 0xea:
            print("LD (nn), A")
            self.memory.writeb(nn, self.registers.a)
            self.updatePC(3)
        elif instruction == 0x83:
            print("ADD A, E")
            if ((self.registers.a & 0xF) + (self.registers.e & 0xF)) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a = self.registers.a + self.registers.e
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a = self.registers.a & 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x76:
            print("HALT")
            self.updatePC(1)
        elif instruction == 0xc6:
            print("ADD A, n")
            if ((self.registers.a & 0xF) + (n & 0xF)) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a = self.registers.a + n
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a = self.registers.a & 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(2)
        elif instruction == 0x19:
            print("ADD HL, DE")
            if (self.registers.hl_read() & 0xFF) + (self.registers.de_read() & 0xFF) > 0xFFFF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.hl_write(self.registers.hl_read() + self.registers.de_read())
            if self.registers.hl_read() > 0xFFFF:
                self.registers.flag_carry = True
                self.registers.hl_write(self.registers.hl_read() & 0xFFFF)
            else:
                self.registers.flag_carry = False
            if self.registers.hl_read() == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x66:
            print("LD H, (HL)")
            self.registers.h = self.memory.readb(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0x68:
            print("LD L, B")
            self.registers.l = self.registers.b
            self.updatePC(1)
        elif instruction == 0x09:
            print("ADD HL, BC")
            if (self.registers.hl_read() & 0xFF) + (self.registers.bc_read() & 0xFF) > 0xFFFF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.hl_write(self.registers.hl_read() + self.registers.bc_read())
            if self.registers.hl_read() > 0xFFFF:
                self.registers.flag_carry = True
                self.registers.hl_write(self.registers.hl_read() & 0xFFFF)
            else:
                self.registers.flag_carry = False
            if self.registers.hl_read() == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x31:
            print("LD SP, nn")
            self.registers.sp = nn
            self.updatePC(3)
        elif instruction == 0x73:
            print("LD HL, E")
            self.registers.e = self.memory.readb(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0x32:
            print("LDD HL, a")
            self.memory.writeb(self.registers.hl_read(), self.registers.a)
            self.registers.hl_write(self.registers.hl_read()-1)
            self.updatePC(1)
        elif instruction == 0x21:
            print("LD HL, nn")
            self.registers.hl_write(nn)
            self.updatePC(3)
        elif instruction == 0xaf:
            print("XOR a")
            self.registers.a = self.registers.a ^ self.registers.a
            self.updatePC(1)
        elif instruction == 0xf0:
            print("LDH a, n")
            self.registers.a = self.memory.readb(n + 0xFF00)
            self.updatePC(2)
        elif instruction == 0xe2:
            print("LDH (C), A")
            self.memory.writeb(self.registers.c + 0xFF00, self.registers.a)
            self.updatePC(1)
        elif instruction == 0xb0:
            print("OR B")
            self.registers.a |= self.registers.b
            self.updatePC(1)
        elif instruction == 0xb2:
            print("OR D")
            self.registers.a |= self.registers.d
            self.updatePC(1)
        elif instruction == 0xa9:
            print("XOR C")
            self.registers.a = self.registers.a ^ self.registers.c
            self.updatePC(1)
        elif instruction == 0xa1:
            print("AND C")
            self.registers.a = self.registers.a & self.registers.c
            self.updatePC(1)
        elif instruction == 0x7e:
            print("LD A, (HL)")
            self.registers.a = self.memory.readb(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0x56:
            print("LD D, (HL)")
            self.registers.d = self.memory.readb(self.registers.hl_read())
            self.updatePC(1)
        elif instruction == 0x12:
            print("LD (DE), A")
            self.memory.writeb(self.registers.de_read(), self.registers.a)
            self.updatePC(1)
        elif instruction == 0x05:
            print("DEC B")
            if (self.registers.b & 0xF) - (1 & 0xF) < 0:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.b -= 1
            if self.registers.b < 0:
                self.registers.flag_carry = True
                self.registers.b &= 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.b == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x25:
            print("DEC H")
            if (self.registers.h & 0xF) - (1 & 0xF) < 0:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.h -= 1
            if self.registers.h < 0:
                self.registers.flag_carry = True
                self.registers.h &= 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.h == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x80:
            print("ADD A, B")
            if ((self.registers.a & 0xF) + (self.registers.b & 0xF)) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a = self.registers.a + self.registers.b
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a = self.registers.a & 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x81:
            print("ADD A, C")
            if ((self.registers.a & 0xF) + (self.registers.c & 0xF)) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.a = self.registers.a + self.registers.c
            if self.registers.a > 0xFF:
                self.registers.flag_carry = True
                self.registers.a = self.registers.a & 0xFF
            else:
                self.registers.flag_carry = False
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0x47:
            print("LD B, A")
            self.registers.b = self.registers.a
            self.updatePC(1)
        elif instruction == 0xf1:
            print("POP AF")
            # this is fucking difficult...
            try:
                a = self.memory.stack.pop()
            except:
                a = 0
            self.registers.a = (a & 0xFF00) >> 8
            self.registers.f = a & 0xFF
            # well, I can't do that...
            self.updatePC(1)
        elif instruction == 0xc1:
            print("POP BC")
            self.registers.bc_write(self.memory.stack.pop())
            self.updatePC(1)
        elif instruction == 0x04:
            print("INC B")
            if (self.registers.b & 0xF) + (1 & 0xF) > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.registers.b += 1
            if self.registers.b == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            self.updatePC(1)
        elif instruction == 0xd1:
            print("POP DE")
            try:
                a = self.memory.stack.pop()
            except:
                a = 0
            self.registers.de_write(a)
            # well, I can't do that...
            self.updatePC(1)
        elif instruction == 0xe1:
            print("POP HL")
            try:
                a = self.memory.stack.pop()
            except:
                a = 0
            self.registers.hl_write(a)
            # well, I can't do that...
            self.updatePC(1)
        elif instruction == 0xe0:
            print("LDH n, a")
            self.memory.writeb(n + 0xFF00, self.registers.a)
            self.updatePC(2)
        elif instruction == 0x38:
            print("JR C, n")
            self.updatePC(2)
            if self.registers.flag_carry:
                self.updatePC((n ^ 0x80) - 0x80)
        elif instruction == 0xde:
            print("SBC A, n")
            if (self.registers.a & 0xF) - (n & 0xF) - self.registers.flag_carry > 0xF:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            
            self.registers.a = self.registers.a - n - self.registers.flag_carry
            if self.registers.a == 0:
                self.registers.flag_zero = True
            else:
                self.registers.flag_zero = False
            if self.registers.a < 0:
                self.registers.flag_carry = True
                self.registers.a &= 0xFF
            else:
                self.registers.flag_carry = False
            self.updatePC(2)
        elif instruction == 0x36:
            print("LD (HL), n")
            self.memory.writeb(self.registers.hl_read(), n)
            self.updatePC(2)
        elif instruction == 0x77:
            print("LD (HL), a")
            self.memory.writeb(self.registers.hl_read(), self.registers.a)
            self.updatePC(1)
        elif instruction == 0xc0:
            print("RET NZ")
            if not self.registers.flag_zero:
                self.registers.pc = self.memory.stack.pop()
            else:
                self.updatePC(1)
        elif instruction == 0xc8:
            print("RET Z")
            if self.registers.flag_zero:
                self.registers.pc = self.memory.stack.pop()
            else:
                self.updatePC(1)
        elif instruction == 0xfe:
            print("CP n")
            self.registers.flag_sub = True
            if self.registers.a == n:
                self.registers.flag_zero = False # swap me
            else:
                self.registers.flag_zero = True # swap me #### WORKAROUND FOR IO PORT READS, they are not implemented :(
            if n > self.registers.a:
                self.registers.flag_carry = True
            else:
                self.registers.flag_carry = False
            if n & 0x0f > self.registers.a & 0x0f:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.updatePC(2)
        elif instruction == 0xb9:
            print("CP C")
            self.registers.flag_sub = True
            if self.registers.a == self.registers.c:
                self.registers.flag_zero = True # swap me
            else:
                self.registers.flag_zero = False # swap me
            if self.registers.c > self.registers.a:
                self.registers.flag_carry = True
            else:
                self.registers.flag_carry = False
            if self.registers.c & 0x0f > self.registers.a & 0x0f:
                self.registers.flag_hc = True
            else:
                self.registers.flag_hc = False
            self.updatePC(1)
        elif instruction == 0x2f:
            print("CPL")
            self.registers.a = ~self.registers.a & 0xFF
            self.updatePC(1)
        elif instruction == 0xcb: #PREFIXED INSTRUCTION
            self.updatePC(1)
            print("PREFIXED INSTRUCTION")
            instruction = self.getInstruction()
            if instruction == 0x7c:
                print("BIT 7, H")
                self.bit(self.registers.h, 7)
                self.updatePC(1)
            elif instruction == 0xde:
                print("SET 3, (HL)")
                n = self.memory.readb(self.registers.hl_read())
                self.memory.writeb(self.registers.hl_read(), self.setb(3, n))
                self.updatePC(1)
            elif instruction == 0x37:
                print("SWAP A")
                self.registers.a = ((self.registers.a) & 0x0F0F) & ((self.registers.a & 0x0F0F) << 4)
                self.updatePC(1)
            elif instruction == 0x3F:
                print("SRL A")
                self.registers.a = self.registers.a >> 1
                if self.registers.a == 0:
                    self.registers.flag_zero = True
                else:
                    self.registers.flag_zero = False
                if self.registers.a > 0xFF:
                    self.registers.a &= 0xFF
                    self.registers.flag_carry = True
                else:
                    self.registers.flag_carry = False
                self.updatePC(1)
            elif instruction == 0x27:
                print("SLA A")
                self.registers.a = self.registers.a << 1
                if self.registers.a == 0:
                    self.registers.flag_zero = True
                else:
                    self.registers.flag_zero = False
                if self.registers.a > 0xFF:
                    self.registers.a &= 0xFF
                    self.registers.flag_carry = True
                else:
                    self.registers.flag_carry = False
                self.updatePC(1)
        else:
            print("Undefined instruction {}".format(hex(instruction)))
            raise Exception()
class GGMemory:
    def __init__(self):
        self.memory = [0]*0x10000 # 0xFFFF
        self.vram = [0]* (0x2000+1) # 0x2000 of VRAM
        self.OAM = [0] * (0xFF+1) # 0xFF of OAM
        self.iomem = [0] * (0x7F+1) # 0x7F of I/O registers
        self.stack = []
    def readb(self, address):
        if address >= 0x8000 and address <= 0x9FFF:
            print("READ VRAM")
            return self.vram[address - 0x8000]
        elif address >= 0xFE00 and address <= 0xFE9F:
            print("READ OAM")
            return self.OAM[address - 0xFE00] 
        elif address >= 0xFF00 and address <= 0xFF7F:
            print("READ IOMEM")
            return self.iomem[address - 0xFF00]
        elif address >= 0xE000 and address <= 0xFDFF:
            print("READ ECHO")
            return self.memory[address - 0x2000] # ECHO RAM
        else:
            return self.memory[address]
    def writeb(self, address, val):
        if address >= 0x8000 and address <= 0x9FFF:
            self.vram[address - 0x8000] = val
        elif address >= 0xFE00 and address <= 0xFE9F:
            self.OAM[address - 0xFE00] = val
        elif address >= 0xFF00 and address <= 0xFF7F:
            self.iomem[address - 0xFF00] = val
        elif address >= 0xE000 and address <= 0xFDFF:
            self.memory[address - 0x2000] = val # ECHO RAM
        else:
            self.memory[address] = val
class GGIO:
    def __init__(self, iomem, vram):
        self.memory = iomem
        self.vmemory = vram
        self.hz = 60
        self.lcdc = 0x40
        self.stat = 0x41
        self.scy = 0x42
        self.scx = 0x43
        self.ly_reg = 0x44
        self.lyc = 0x45
        self.dma = 0x46
        self.bgp = 0x47
        self.obp0 = 0x48
        self.gbp2 = 0x49
        self.wy = 0x4A
        self.wx = 0x4B
        self.startTimers()
        self.tilecache = []
    def updateTile(self, address):
        addr &= 0x1FFE
        tile = (addr >> 4) & 511
        y = (addr >> 1) & 7
        
    def update_ly_reg(self):
        if self.memory[self.ly_reg] < 153:
            self.memory[self.ly_reg] += 1
        else:
            self.memory[self.ly_reg] = 0
        threading.Timer(0.0025, self.update_ly_reg).start()
    def startTimers(self):
        self.update_ly_reg()
    def process(self):
        pass
class Machine:
    def __init__(self):
        self.memory = GGMemory()
        self.cpu = GGCPU(self.memory)
        self.io = GGIO(self.memory.iomem, self.memory.vram)
    def loadROM(self, file):
        with open(file, "rb") as h:
            buf = h.read()
            for index, i in enumerate(buf):
                self.memory.memory[index] = i
    def Execute(self):
        last_command = ""
        while True:
            i = input(">>> ")
            if i == "":
                i = last_command
            last_command = i
            if i == "c":
                try:
                    while True:
                        self.cpu.step()
                        self.io.process()
                except KeyboardInterrupt:
                    continue
            if i[:3] == "set":
                targetRegister = i[4]
                targetValue = i[5:]
                exec("self.cpu.registers.{} = {}".format(targetRegister, targetValue))
            if i[:4] == "dump":
                print(i[5:])
                if i[5:] == "vram":
                    print("dumped VRAM into vram.bin")
                    with open("vram.bin", "wb+") as a:
                        i = 0
                        while i < 0x2000:
                            a.write(self.memory.vram[i].to_bytes(1, "little"))
                            i+=1
            if i == "r":
                print("REGISTER DUMP\na---- {}\nb---- {}\nc---- {}\nd---- {}\ne---- {}\nh---- {}\nl---- {}".format(hex(self.cpu.registers.a), hex(self.cpu.registers.b), hex(self.cpu.registers.c), hex(self.cpu.registers.d), hex(self.cpu.registers.e), hex(self.cpu.registers.h), hex(self.cpu.registers.l)))
            if i == "s":
                self.cpu.step()
                self.io.process()

if __name__ == "__main__":
    m = Machine()
    m.loadROM("drmario.gb")
    m.Execute()