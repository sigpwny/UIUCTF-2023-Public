# Solution

- VM reversing challenge
- figure out opcodes
- big switch table in function at `0x0000144c` (base address `0x00001000`)
- write disassembler for `program` file, figure out what the opcodes do
- realize that it's doing a bunch of XORs and comparisons, do the XORs yourself to figure out the flag
