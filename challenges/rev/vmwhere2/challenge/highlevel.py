#!/usr/bin/env python3

import random

class Assembly:
    def __init__(self):
        self.instructions = []

    def __str__(self):
        return '\n'.join(self.instructions)

    def _get_label(self):
        # generate random label
        return '__label_' + str(random.randint(0, 10**9))

    def print(self, string):
        self.instructions.append("PUSH 0")
        for char in string[::-1]:
            self.push(ord(char))
        self.instructions += [
            'JZ 4',
            'OUT',
            'JMP -7',
        ]

    def println(self, string):
        self.print(string + '\n')

    def inputn(self, n):
        self.instructions += ['IN'] * n

    def outputn(self, n):
        self.instructions += ['OUT'] * n

    def jump_if_equal(self, val, target):
        equal = self._get_label()
        end = self._get_label()

        self.dup()
        self.xor(val)
        self.jz(equal)
        self.pop()
        self.jmp(end)

        self.label(equal)
        self.pop()
        self.jmp(target)
        self.label(end)

    def push(self, value):
        if type(value) == list:
            for v in value:
                self.push(v)
        elif type(value) == int:
            self.instructions.append(f'PUSH {value}')
        else:
            raise Exception(f'Invalid type {type(value)}')

    def reverse(self, n):
        self.instructions.append(f'REV {n}')

    def swap(self):
        self.reverse(2)

    def popn(self, n=1):
        self.instructions += ['POP'] * n

    def pop(self):
        self.popn(1)

    def label(self, name):
        self.instructions.append(f'{name}:')

    def jmp(self, name):
        self.instructions.append(f'JMP {name}')

    def jz(self, name):
        self.instructions.append(f'JZ {name}')

    def jnz(self, name):
        self.instructions += [
            'JZ 3',
            f'JMP {name}',
        ]

    def js(self, name):
        self.instructions.append(f'JS {name}')

    def _op_with_optional_arg(self, op, arg):
        if arg is not None:
            self.instructions.append(f'PUSH {arg}')
        self.instructions.append(op)

    def add(self, n=None):
        self._op_with_optional_arg('ADD', n)

    def sub(self, n=None):
        self._op_with_optional_arg('SUB', n)

    def and_(self, n=None):
        self._op_with_optional_arg('AND', n)

    def or_(self, n=None):
        self._op_with_optional_arg('OR', n)

    def xor(self, n=None):
        self._op_with_optional_arg('XOR', n)

    def shl(self, n=None):
        self._op_with_optional_arg('SHL', n)

    def shr(self, n=None):
        self._op_with_optional_arg('SHR', n)

    def dup(self, n=1):
        self.instructions += ['DUP'] * n

    def scat(self, n=1):
        self.instructions += ['SCAT'] * n

    def coal(self, n=1):
        self.instructions += ['COAL'] * n

    def bkpt(self):
        self.instructions.append('BKPT')

    def exit(self):
        self.instructions.append('EXIT')
