#!/usr/bin/env python3

import sys
import os

opcodes = {
    'EXIT':  0,
    'ADD':   1,
    'SUB':   2,
    'AND':   3,
    'OR':    4,
    'XOR':   5,
    'SHL':   6,
    'SHR':   7,
    'IN':    8,  # inputs byte value
    'OUT':   9,  # outputs byte value
    'PUSH': 10,
    'JS':   11,  # branch if signed. Destination relative to next instruction
    'JZ':   12,  # branch if zero. Destination relative to next instruction
    'JMP':  13,  # unconditional branch. Destination relative to next instruction
    'POP':  14,  # ignore popped result
    'DUP':  15,  # duplicate top of stack
    'REV':  16,  # reverse top n elements of stack
    'SCAT': 17,  # scatter 8 bits
    'COAL': 18,  # coalesce 8 bits
    'BKPT': 40,  # breakpoint
}
jumps = ['JS', 'JZ', 'JMP']
has_arg = ['PUSH', 'REV']


def assemble_file(filename):
    if filename == '-':
        assembly = sys.stdin.read().splitlines()
    else:
        assembly = open(filename).readlines()
    bytecode = []

    # set the jump targets at the end once we know the labels
    # this stores tuples of the form (index, label)
    jump_relocs = []
    # maps label names to their index in the bytecode
    jump_targets = {}

    line_no = 0
    for line in assembly:
        line_no += 1
        # ignore comments
        code = line.split('#')[0].strip()
        if len(code) == 0:
            continue

        # handle labels
        if code[-1] == ':':
            jump_targets[code[:-1]] = len(bytecode)
            continue

        opcode, *args = code.split()
        opcode = opcode.upper()
        if opcode not in opcodes:
            raise Exception(f'Invalid opcode: {opcode} at line: {line_no}')

        arguments = []
        if opcode in jumps:
            if len(args) != 1:
                raise Exception(f'Invalid number of arguments for {opcode} at line: {line_no}')
            arg = args[0]
            # check if the argument is a label
            if not arg.startswith('-') and not arg.isdigit():
                jump_relocs.append((len(bytecode) + 1, arg))
                arguments += [0, 0]
            else:
                offset = int(arg)
                arguments += [(offset >> 8) & 0xff, offset & 0xff]
        elif opcode in has_arg:
            if len(args) != 1:
                raise Exception(f'{opcode} requires an argument at line: {line_no}')
            arg = args[0]
            if arg.startswith('0x'):
                arguments.append(int(arg, 16))
            elif arg.startswith('-0x'):
                arguments.append(int(arg, 16) & 0xff)
            elif len(arg) == 3 and arg[0] == "'" and arg[2] == "'":
                arguments.append(ord(arg[1]))
            else:
                arguments.append(int(arg) & 0xff)

        bytecode += [opcodes[opcode]] + arguments

    # resolve jump targets
    for index, label in jump_relocs:
        if label not in jump_targets:
            raise Exception(f'Invalid jump target: {label} at line: {line_no}')
        # -1 because the jump offset is relative to the next instruction
        jump_offset = jump_targets[label] - index - 2
        if jump_offset < -0x8000 or jump_offset > 0x7fff:
            raise Exception(f'Jump target out of range: {label} at line: {line_no}')
        bytecode[index] = (jump_offset >> 8) & 0xff
        bytecode[index + 1] = jump_offset & 0xff

    return bytecode


def main():
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <assembly_file> <output_file>')
        return

    assembly_file = sys.argv[1]
    output_file = sys.argv[2]

    bytecode = assemble_file(assembly_file)
    bytecode_bytes = bytes(bytecode)
    if output_file == '-':
        # warn if outputting to terminal
        if sys.stdout.isatty():
            print('Warning: outputting to terminal. Aborting', file=sys.stderr)
            return
        os.write(sys.stdout.fileno(), bytecode_bytes)
    else:
        open(output_file, 'wb+').write(bytecode_bytes)


if __name__ == "__main__":
    main()
