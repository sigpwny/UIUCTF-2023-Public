#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <signal.h>

/*
 * The stack:
 * 2-byte words
 */

/*
 * Opcodes:
 * All opcodes pop the second argument and then the first. The result is pushed
 * back onto the stack.
 */
#define OP_EXIT 0
#define OP_ADD  1
#define OP_SUB  2
#define OP_AND  3
#define OP_OR   4
#define OP_XOR  5
#define OP_SHL  6
#define OP_SHR  7
#define OP_IN   8 // inputs byte value
#define OP_OUT  9 // outputs byte value

// these opcodes have a one byte argument
#define OP_PUSH 10

// these opcodes have a two byte argument (big endian)
#define OP_JS   11 // branch if signed. Destination relative to next instruction
#define OP_JZ   12 // branch if zero. Destination relative to next instruction
#define OP_JMP  13 // unconditional branch. Destination relative to next instruction

#define OP_POP  14 // ignore popped result
#define OP_DUP  15 // duplicate top of stack
#define OP_REV  16 // reverse top n elements of stack

#define OP_SCAT 17 // scatter 8 bits of top element by pushing each bit to the stack
                   // pushes least significant bit first
#define OP_COAL 18 // coalesce top 8 elements and merge into 1

#define OP_BKPT 40 // breakpoint


#define STACK_SIZE 0x1000

uint8_t* read_program(char* program_name, int* program_size) {
    // read the program into memory
    FILE* fp = fopen(program_name, "r");
    if (fp == NULL) {
        return NULL;
    }

    fseek(fp, 0, SEEK_END);
    *program_size = ftell(fp);
    rewind(fp);

    uint8_t* program = malloc(*program_size);
    if (program == NULL) {
        return NULL;
    }
    fread(program, 1, *program_size, fp);
    fclose(fp);

    return program;
}

void print_debug_info(uint8_t* program, uint8_t* stack, uint8_t* sp, unsigned long pc) {
    sp--;
    printf("Program counter: 0x%04lx\n", pc);
    printf("Stack pointer: 0x%04lx\n", sp - stack);
    printf("Stack:\n");
    for (int i = 0; i < 0x10; i++) {
        if (sp - stack - i >= 0) {
            printf("0x%04lx: 0x%04x\n", sp - stack - i, *(sp - i));
        }
    }
}

int interpret(uint8_t* program, int program_size) {
    uint8_t* ip = program;
    uint8_t* stack = malloc(STACK_SIZE);
    uint8_t* sp = stack;
    while (program <= ip && ip < program + program_size) {
        switch (*ip++) {
            case OP_EXIT:
                return 0;
            case OP_ADD:
                sp -= 2;
                sp[0] += sp[1];
                sp++;
                break;
            case OP_SUB:
                sp -= 2;
                sp[0] -= sp[1];
                sp++;
                break;
            case OP_AND:
                sp -= 2;
                sp[0] &= sp[1];
                sp++;
                break;
            case OP_OR:
                sp -= 2;
                sp[0] |= sp[1];
                sp++;
                break;
            case OP_XOR:
                sp -= 2;
                sp[0] ^= sp[1];
                sp++;
                break;
            case OP_SHL:
                sp -= 2;
                sp[0] <<= sp[1];
                sp++;
                break;
            case OP_SHR:
                sp -= 2;
                sp[0] >>= sp[1];
                sp++;
                break;
            case OP_IN:
                sp[0] = getchar();
                sp++;
                break;
            case OP_OUT:
                sp--;
                putchar(sp[0]);
                break;
            case OP_PUSH:
                sp[0] = *ip++;
                sp++;
                break;
            case OP_JS:
                if ((int8_t)sp[-1] < 0) {
                    ip += (int16_t)(*ip << 8 | ip[1]);
                }
                ip += 2;
                break;
            case OP_JZ:
                if (sp[-1] == 0) {
                    ip += (int16_t)(*ip << 8 | ip[1]);
                }
                ip += 2;
                break;
            case OP_JMP:
                ip += (int16_t)(*ip << 8 | ip[1]);
                ip += 2;
                break;
            case OP_POP:
                sp--;
                break;
            case OP_DUP:
                sp[0] = sp[-1];
                sp++;
                break;
            case OP_REV:
                {
                    uint8_t n = *ip++;
                    uint8_t tmp;
                    if (n > sp - stack) {
                        printf("Stack underflow in reverse at 0x%04lx\n", ip - program);
                    }
                    for (int i = 0; i < n / 2; i++) {
                        tmp = sp[-n + i];
                        sp[-n + i] = sp[-1 - i];
                        sp[-1 - i] = tmp;
                    }
                }
                break;
            case OP_SCAT:
                {
                    sp--;
                    uint8_t val = sp[0];
                    for (int i = 0; i < 8; i++) {
                        sp[i] = val & 1;
                        val >>= 1;
                    }
                    sp += 8;
                }
                break;
            case OP_COAL:
                {
                    sp -= 8;
                    uint8_t val = 0;
                    for (int i = 7; i >= 0; i--) {
                        val <<= 1;
                        val |= sp[i] & 1;
                    }
                    sp[0] = val;
                    sp++;
                }
                break;
            case OP_BKPT:
                print_debug_info(program, stack, sp, ip - program);
                break;
            default:
                printf("Unknown opcode: 0x%02x at 0x%04lx\n", *(ip - 1), (ip - 1) - program);
                return 1;
        }
        // check for stack overflow or underflow
        if (sp < stack) {
            printf("Stack underflow at 0x%04lx\n", ip - program);
            return 1;
        }
        if (sp > stack + STACK_SIZE) {
            printf("Stack overflow at 0x%04lx\n", ip - program);
            return 1;
        }
    }
    printf("Program terminated unexpectedly. Last instruction: 0x%04lx\n", ip - program);
    return 1;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: %s <program>\n", argv[0]);
        return 1;
    }

    int program_size;
    uint8_t* program = read_program(argv[1], &program_size);
    if (program == NULL) {
        printf("Failed to read program %s\n", argv[1]);
        return 2;
    }

    int ret = interpret(program, program_size);
    if (ret != 0) {
        return 3;
    }

    return 0;
}
