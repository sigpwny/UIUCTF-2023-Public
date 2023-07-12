import struct
from construct import *
from construct.lib import *
import enum
import itertools

OP_PROPS = b"\x7f\x60\x11\x12\x13\x14\x15\x16\x17\x18\x19\x12\x51\x70\x31\x42\x60\x31\x31\x14\x40\x20\x20" \
    b"\x41\x02\x13\x21\x21\x21\x60\x60\x10\x11\x11\x60\x60\x60\x60\x60\x60\x60\x60\x10\x03\x00\x41" \
    b"\x40\x41\x40\x40\x41\x40\x41\x41\x41\x41\x41\x41\x42\x42\x42\x42\x42\x42\x42\x42\x42\x42\x42" \
    b"\x42\x42\x42\x41\x32\x21\x20\x41\x10\x30\x12\x30\x70\x10\x10\x51\x51\x71\x10\x41\x42\x40\x42" \
    b"\x42\x11\x60"

BYTECODEFLAG_NUM_ARGS_MASK = 0xf
BYTECODEFLAG_IS_STMT = 0x10
BYTECODEFLAG_TAKES_NUMBER = 0x20
BYTECODEFLAG_IS_STATELESS = 0x40  # fun modifier - only valid when !is_stmt
BYTECODEFLAG_IS_FINAL_STMT = 0x40 # final modifier - only valid when is_stmt

FIRST_MULTIBYTE_INT = 0xf8
DIRECT_CONST_OP = 0x80

class Opcode(enum.IntEnum):
    INVALID_META_FUNC_END = 0
    EXPRx_BUILTIN_OBJECT = 1
    STMT1_CALL0 = 2
    STMT2_CALL1 = 3
    STMT3_CALL2 = 4
    STMT4_CALL3 = 5
    STMT5_CALL4 = 6
    STMT6_CALL5 = 7
    STMT7_CALL6 = 8
    STMT8_CALL7 = 9
    STMT9_CALL8 = 10
    STMT2_INDEX_DELETE = 11
    STMT1_RETURN = 12
    STMTx_JMP = 13
    STMTx1_JMP_Z = 14
    EXPR2_BIND = 15
    EXPRx_OBJECT_FIELD = 16
    STMTx1_STORE_LOCAL = 17
    STMTx1_STORE_GLOBAL = 18
    STMT4_STORE_BUFFER = 19
    EXPR0_INF = 20
    EXPRx_LOAD_LOCAL = 21
    EXPRx_LOAD_GLOBAL = 22
    EXPR1_UPLUS = 23
    EXPR2_INDEX = 24
    STMT3_INDEX_SET = 25
    EXPRx1_BUILTIN_FIELD = 26
    EXPRx1_ASCII_FIELD = 27
    EXPRx1_UTF8_FIELD = 28
    EXPRx_MATH_FIELD = 29
    EXPRx_DS_FIELD = 30
    STMT0_ALLOC_MAP = 31
    STMT1_ALLOC_ARRAY = 32
    STMT1_ALLOC_BUFFER = 33
    EXPRx_STATIC_SPEC_PROTO = 34
    EXPRx_STATIC_BUFFER = 35
    EXPRx_STATIC_BUILTIN_STRING = 36
    EXPRx_STATIC_ASCII_STRING = 37
    EXPRx_STATIC_UTF8_STRING = 38
    EXPRx_STATIC_FUNCTION = 39
    EXPRx_LITERAL = 40
    EXPRx_LITERAL_F64 = 41
    STMT0_REMOVED_42 = 42
    EXPR3_LOAD_BUFFER = 43
    EXPR0_RET_VAL = 44
    EXPR1_TYPEOF = 45
    EXPR0_UNDEFINED = 46
    EXPR1_IS_UNDEFINED = 47
    EXPR0_TRUE = 48
    EXPR0_FALSE = 49
    EXPR1_TO_BOOL = 50
    EXPR0_NAN = 51
    EXPR1_ABS = 52
    EXPR1_BIT_NOT = 53
    EXPR1_IS_NAN = 54
    EXPR1_NEG = 55
    EXPR1_NOT = 56
    EXPR1_TO_INT = 57
    EXPR2_ADD = 58
    EXPR2_SUB = 59
    EXPR2_MUL = 60
    EXPR2_DIV = 61
    EXPR2_BIT_AND = 62
    EXPR2_BIT_OR = 63
    EXPR2_BIT_XOR = 64
    EXPR2_SHIFT_LEFT = 65
    EXPR2_SHIFT_RIGHT = 66
    EXPR2_SHIFT_RIGHT_UNSIGNED = 67
    EXPR2_EQ = 68
    EXPR2_LE = 69
    EXPR2_LT = 70
    EXPR2_NE = 71
    EXPR1_IS_NULLISH = 72
    STMTx2_STORE_CLOSURE = 73
    EXPRx1_LOAD_CLOSURE = 74
    EXPRx_MAKE_CLOSURE = 75
    EXPR1_TYPEOF_STR = 76
    STMT0_REMOVED_77 = 77
    STMTx_JMP_RET_VAL_Z = 78
    STMT2_CALL_ARRAY = 79
    STMTx_TRY = 80
    STMTx_END_TRY = 81
    STMT0_CATCH = 82
    STMT0_FINALLY = 83
    STMT1_THROW = 84
    STMT1_RE_THROW = 85
    STMTx1_THROW_JMP = 86
    STMT0_DEBUGGER = 87
    EXPR1_NEW = 88
    EXPR2_INSTANCE_OF = 89
    EXPR0_NULL = 90
    EXPR2_APPROX_EQ = 91
    EXPR2_APPROX_NE = 92
    STMT1_STORE_RET_VAL = 93
    EXPRx_STATIC_SPEC = 94
    OP_PAST_LAST = 95

JUMP_OPCODES = [Opcode.STMTx_JMP, Opcode.STMTx1_JMP_Z, Opcode.STMTx_JMP_RET_VAL_Z, Opcode.STMTx_TRY, Opcode.STMTx_END_TRY, Opcode.STMTx1_THROW_JMP]

section = Struct(
    "section_start" / Int32ul,
    "section_size" / Int32ul,
)

function_desc = Struct(
    "start" / Int32ul,
    "length" / Int32ul,
    "num_slots" / Int16ul,
    "num_args" / Int8ul,
    "flags" / Int8ul,
    "name_idx" / Int16ul,
    "num_try_frames" / Int8ul,
    "reserved" / Int8ul,
)
function_desc_list = GreedyRange(function_desc)

#cstring_list = GreedyRange(CString("ascii"))
SECTIONS = ["functions", "functions_data", "float_literals", "roles_removed", "ascii_strings", "utf8_strings", "buffers", "string_data", "service_specs", "dcfg"]

header = Struct(
    "magic1" / Int32ul,
    "magic2" / Int32ul,
    "version" / Int32ul,
    "num_globals" / Int16ul,
    "num_service_specs" / Int16ul,
    "reserved" / Int8ul[16],
    "sections" / Rebuild(
        Struct(
            "functions" / section,
            "functions_data" / section,
            "float_literals" / section,
            "roles_removed" / section,
            "ascii_strings" / section,
            "utf8_strings" / section,
            "buffers" / section,
            "string_data" / section,
            "service_specs" / section,
            "dcfg" / section,
        ),
        lambda this: dict(list(itertools.accumulate(SECTIONS, lambda a,b: (b, {
            "section_start": a[1]["section_start"] + a[1]["section_size"],
            "section_size": len(this["_"][b]) if b != "functions" else len(this["_"][b]) * function_desc.sizeof(),
        }), initial=(None, {"section_start": header.sizeof(), "section_size": 0})))[1:])
    ),
)

format = Struct(
    "header" / header,

    "functions" / Array(this.header.sections.functions.section_size // function_desc.sizeof(), function_desc),
    #"functions" / Bytes(lambda this: this.header.sections.functions.section_size),
    "functions_data" / Bytes(lambda this: this.header.sections.functions_data.section_size),
    "float_literals" / Bytes(lambda this: this.header.sections.float_literals.section_size),
    "roles_removed" / Bytes(lambda this: this.header.sections.roles_removed.section_size),
    "ascii_strings" / Bytes(lambda this: this.header.sections.ascii_strings.section_size),
    "utf8_strings" / Bytes(lambda this: this.header.sections.utf8_strings.section_size),
    "buffers" / Bytes(lambda this: this.header.sections.buffers.section_size),
    "string_data" / Bytes(lambda this: this.header.sections.string_data.section_size),
    "service_specs" / Bytes(lambda this: this.header.sections.service_specs.section_size),
    "dcfg" / Bytes(lambda this: this.header.sections.dcfg.section_size),
)


import sys
fname = sys.argv[1]
f = open(fname, "rb").read()

parsed = format.parse(f)
print("\n--Parsed--")
print(parsed)

print("\n--Function Descs--")
print(parsed.functions)

pc = 0
#bytecode = parsed.functions_data.rawdata

def fetch_byte(mem, pc=0):
    if pc >= len(mem):
        print(f"fetch_byte: out of bounds at {pc} (len={len(mem)})")
        return 0, pc+1
    ret = mem[pc]
    return ret, pc+1

def encode_int(v, size=None):
    if size is None:
        if v==0:
            return bytes([0])
        size = ((v.bit_length() + 7) // 8)
        if size > 1:
            size += 1
    if size == 1:
        return bytes([v])
    
    if v < 0:
        v = -v
        return bytes([(0xf8 + size - 2) | 4]) + v.to_bytes(size - 1, "big")
    return bytes([0xf8 + size - 2]) + v.to_bytes(size - 1, "big")

def fetch_int(mem,pc=0):
    v, pc = fetch_byte(mem, pc)
    if v < FIRST_MULTIBYTE_INT:
        return v, pc
    r = 0
    n = not (not (v & 4))
    len = (v & 3) + 1
    for i in range(len):
        b, pc = fetch_byte(mem, pc)
        r <<= 8
        r |= b
    return -r if n else r, pc


# align to multiple of 4 bytes (dword)
def align(dat, n=4):
    if len(dat) % n == 0:
        return dat
    return dat + b"\x00" * (n - len(dat) % n)



class Instruction(object):
    def __init__(self, opcode, num=None, pc=None):
        self.pc = pc
        #if isinstance(opcode, int):
        #    opcode = Opcode(opcode)
        self.opcode = opcode
        self.num = num
        self.jmp_target = None

def obf(mem, parsed):
    new_function_data = b""

    current_function_offset = header.sizeof() + parsed.header.sections.functions.section_size


    for function_desc in parsed.functions:

        # need to do first pass to add jmp target labels
        # then do second pass to change jmp targets
        instructions = []

        print(f"\n--Function {function_desc.name_idx}--")
        print(f"start={function_desc.start} length={function_desc.length} slots={function_desc.num_slots} args={function_desc.num_args} flags={function_desc.flags} try_frames={function_desc.num_try_frames}")
        function_bytecode = mem[function_desc.start:function_desc.start+function_desc.length]
        print(f"code={function_bytecode}")

        pc = 0
        print(f"pc={function_desc.start}, end={function_desc.start + function_desc.length}")
        while pc < function_desc.length:
            orig_pc = pc
            opcode, pc = fetch_byte(function_bytecode, pc)
            if opcode >= DIRECT_CONST_OP:
                instructions.append(Instruction(opcode, pc=orig_pc))
                continue
            if opcode == 0:
                continue
            opcode = Opcode(opcode)
            flags = OP_PROPS[opcode.value]

            print(f"{orig_pc:04} {opcode.name}({opcode.value}) flags={flags:02x}")
            if flags & BYTECODEFLAG_TAKES_NUMBER:
                num, pc = fetch_int(function_bytecode, pc)
                print(f"  num={num}")
                instructions.append(Instruction(opcode, num, pc=orig_pc))
            else:
                instructions.append(Instruction(opcode, pc=orig_pc))

        # resolve jmp targets
        for instruction in instructions:
            if instruction.opcode in JUMP_OPCODES:
                jmp_target = instruction.num + instruction.pc
                print(f"jmp target: {jmp_target:04}")
                target = [x for x in instructions if x.pc == jmp_target][0]
                instruction.jmp_target = target

        # now we can make modifications to instruction list



        # after each stmt, add a jmp to the next stmt and another jmp to confuse the disassembler
        new_instructions = []
        for i, instruction in enumerate(instructions):
            if i == len(instructions) - 1:
                new_instructions.append(instruction)
                continue
            # check if stmt
            if int(instruction.opcode) < len(OP_PROPS) and OP_PROPS[int(instruction.opcode)] & BYTECODEFLAG_IS_STMT:
                new_instructions.append(instruction)
                jmp = Instruction(Opcode.STMTx_JMP, 69)
                jmp.jmp_target = instructions[i+1]
                new_instructions += [jmp, Instruction(Opcode.EXPR0_UNDEFINED), Instruction(Opcode.STMT1_RETURN), Instruction(Opcode.STMTx_JMP)]
            else:
                new_instructions.append(instruction)
        instructions = new_instructions    

        # pass to compute new pc values
        pc = 0
        for instruction in instructions:
            instruction.pc = pc
            pc += 1
            if instruction.num is not None:
                if instruction.jmp_target is not None:
                    pc += 3
                else:
                    pc += len(encode_int(instruction.num))

        # print
        print("\n--Modified Instructions--")
        for instruction in instructions:
            if isinstance(instruction.opcode, Opcode):
                print(f"{instruction.pc:04} {instruction.opcode.name}({instruction.opcode.value}) num={instruction.num} jmp_target={instruction.jmp_target.pc if instruction.jmp_target is not None else None}")
            else:
                print(f"{instruction.pc:04} CONST {instruction.opcode}")
        
        # convert instructions back to bytecode
        new_function_bytecode = b""
        for instruction in instructions:
            new_function_bytecode += bytes([int(instruction.opcode)])

            if instruction.num is not None:
                if instruction.jmp_target is not None:
                    new_function_bytecode += encode_int(instruction.jmp_target.pc - instruction.pc, 3)
                else:
                    new_function_bytecode += encode_int(instruction.num)
                
        # pad to multiple of 4
        new_function_bytecode = align(bytes(new_function_bytecode), 4)

        function_desc.length = len(new_function_bytecode)
        function_desc.start = current_function_offset
        current_function_offset += len(new_function_bytecode)

        new_function_data += new_function_bytecode
    parsed.functions_data = new_function_data


obf(f, parsed)

out = open("./.devicescript/bin/bytecode.obf.devs", "wb+")
out_bytes = align(format.build(parsed), 32)
out.write(out_bytes)
out.close()

