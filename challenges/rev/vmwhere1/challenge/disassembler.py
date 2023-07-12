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
    'BKPT': 40,  # breakpoint
}
opcode_to_mnemonic = {v: k for k, v in opcodes.items()}
jumps = ['JS', 'JZ', 'JMP']
has_arg = ['PUSH', 'REV']

def disassemble(bytecode):
    assembly = []
    i = 0
    while i < len(bytecode):
        if bytecode[i] not in opcode_to_mnemonic:
            raise ValueError(f'Invalid opcode {bytecode[i]} at {i}')
        mnemonic = opcode_to_mnemonic[bytecode[i]]
        if mnemonic in has_arg:
            assembly.append((i, mnemonic, f'{bytecode[i+1]}'))
            i += 2
        elif mnemonic in jumps:
            # sign extend the 16-bit jump offset
            offset = (bytecode[i+1] << 8) | bytecode[i+2]
            if offset & 0x8000:
                offset -= 0x10000
            assembly.append((i, mnemonic, f'{offset} ({i+3 + offset:04x})'))
            i += 3
        else:
            assembly.append((i, mnemonic, ''))
            i += 1
    return assembly

def disassemble_file(filename):
    if filename == '-':
        assembly = disassemble(sys.stdin.buffer.read())
    else:
        assembly = disassemble(open(filename, 'rb').read())
    output = ''
    for ip, mnemonic, operand in assembly:
        output += f'{ip:04x}: {mnemonic:4} {operand}\n'
    return output

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <binary_file> <output_file>')
        return

    binary_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = '-'

    assembly = disassemble_file(binary_file)
    if output_file == '-':
        print(assembly, end='')
    else:
        open(output_file, 'w+').write(assembly)


if __name__ == "__main__":
    main()
