import math
import random
rand = random.SystemRandom()

real_flag = "uiuctf{n0t_So_f45t_w1th_0bscur3_b1ts_of_MaThs}"
fake_flag = "uiuctf{This is a fake flag. You are too fast!}"

if len(real_flag) != len(fake_flag):
    raise ValueError("Lengths of flags are not equal")

def createOperation(operator):
    """
    Helper function to create a standard math operation
    """
    valueA = rand.uniform(-500, 500)
    valueB = rand.uniform(-500, 500)
    while (valueA == valueB): valueB = rand.uniform(-500, 500)
    result = 0
    if operator == "+":
        result = valueA + valueB
    elif operator == "-":
        result = valueA - valueB
    elif operator == "*":
        result = valueA * valueB
    elif operator == "/":
        result = valueA / valueB
    elif operator == "%":
        result = math.fmod(valueA, valueB)
    else:
        raise ValueError("Invalid operator")
    return (valueA, operator, valueB, result)

def generateFastOperation():
    """
    Generates an operation where the gauntlet returns 0 for fast-math and 1 for normal math

    This is done by the output operation either resulting in -0, nan, or inf
    """
    valueA = rand.uniform(0, 500)
    valueB = rand.uniform(0, 500)
    negative = rand.choice([True, False])
    type = rand.choice(["signbit", "isnan"])
    if type == "signbit":
        if not negative:
            copy_valueA = valueA
        else:
            copy_valueA = -valueA
        return (-valueA, "%", copy_valueA)
    else:
        subvalue = rand.uniform(-1, 1)
        while subvalue == -1.0 or subvalue == 1.0: subvalue = rand.uniform(-1, 1)
        return (-valueA, "^", subvalue)

def generateBothOperation():
    """
    Generates an operation where the gauntlet returns 1 for both normal and fast-math
    
    This is done by the output operation resulting in a negative number
    """
    operator = rand.choice(["+", "-", "*", "/", "%", "^"])
    if operator == "^":
        base = rand.uniform(-100, -1)
        exponent = rand.randint(1, 99)
        # Generate an odd exponent between 1 and 100
        if exponent % 2 == 0: exponent += 1
        exponent = float(exponent)
        return (base, "^", exponent)
    else:
        operation = createOperation(operator)
        while (operation[3] >= 0): operation = createOperation(operator)
        return operation

def generateNeutralOperation():
    """
    Generates an operation where the gauntlet returns 0 for both normal and fast math
    
    This is done by generating an operation which will result in a positive number
    and results which are neither -0, nan, nor inf
    """
    operator = rand.choice(["+", "-", "*", "/", "%", "^"])
    if operator == "^":
        base = rand.uniform(1, 100)
        exponent = rand.uniform(1, 100)
        return (base, "^", exponent)
    else:
        operation = createOperation(operator)
        while (operation[3] <= 0): operation = createOperation(operator)
        return operation

def flipBit(byte, bit_idx):
    """
    Flips a bit in a byte
    """
    if byte[bit_idx] == '1':
        return byte[:bit_idx] + "0" + byte[bit_idx + 1:]
    else:
        return byte[:bit_idx] + "1" + byte[bit_idx + 1:]

# Convert flags to decimal
real_flag_dec = [ord(c) for c in real_flag]
fake_flag_dec = [ord(c) for c in fake_flag]

# Generate a random encrypted base, the same length as the flag
encbase = []
for idx in range(len(real_flag_dec)):
    encbase.append(rand.randint(0, 255))

# Generate operations to print real flag when compiled with no fast-math, fake flag with fast-math
operations = []
for byte_idx in range(len(encbase)):
    byte_encbase = format(encbase[byte_idx], "08b")
    byte_real_flag = format(real_flag_dec[byte_idx], "08b")
    byte_fake_flag = format(fake_flag_dec[byte_idx], "08b")
    for bit_idx in range(8):
        # Convert bits to ints
        bit_encbase = int(byte_encbase[bit_idx])
        bit_real_flag = int(byte_real_flag[bit_idx])
        bit_fake_flag = int(byte_fake_flag[bit_idx])
        # Pick operation based on bits
        if bit_real_flag != bit_fake_flag:
            operations.append(generateFastOperation())
            if bit_fake_flag != bit_encbase:
                byte_encbase = flipBit(byte_encbase, bit_idx)
        else:
            if bit_real_flag == bit_encbase:
                operations.append(generateNeutralOperation())
            else:
                operations.append(generateBothOperation())
    # Commit new byte
    encbase[byte_idx] = int(byte_encbase, 2)

# Print operation C code
print("operation_t operations[] = {")
for (idx, operation) in enumerate(operations):
    print(f"    {{ .oper = '{operation[1]}', .operandA = {operation[0]}, .operandB = {operation[2]} }}", end="")
    if (idx + 1) != len(operations):
        print(",")
    else:
        print()
print("  };")

# Print encrypted flag C code
print("  char encflag[] = { ")
for (idx, char) in enumerate(encbase):
    print(f"    {char}", end="")
    if (idx + 1) != len(encbase):
        print(",")
    else:
        print()
print("  };")
