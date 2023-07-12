#!/usr/bin/env python3

import sys
from highlevel import Assembly

FLAG = 'uiuctf{b4s3_3_1s_b4s3d_just_l1k3_vm_r3v3rs1ng}'


def program(a):
    a.println('Welcome to VMWhere 2!')
    a.println('Please enter the password:')

    a.push(0) # used to check that the flags are all correct

    for i, c in enumerate(FLAG):
        a.inputn(1)

        # get the bits of the input
        a.scat()
        a.push(0xff) # sentinel end loop value
        a.reverse(9)
        a.reverse(8)
        a.push(0)

        # treat the bits as base 3 (sort of)
        a.label(f'loop1_{i}')
        a.swap()
        a.jump_if_equal(0xff, f'loop1_end_{i}')
        a.swap()

        a.swap()
        a.jz(f'loop1_skip_{i}')
        a.pop()

        a.add(1)
        a.jmp(f'loop1_skip2_{i}')

        a.label(f'loop1_skip_{i}')
        a.pop()
        a.label(f'loop1_skip2_{i}')

        a.dup()
        a.dup()
        a.add()
        a.add()

        a.jmp(f'loop1_{i}')
        a.label(f'loop1_end_{i}')

        a.pop() # pop sentinel end loop value

    # now check the flag values
    for i, c in list(enumerate(FLAG))[::-1]:
        # pseudocode for the above "treat the bits as base 3 (sort of)"
        correct_val = 0
        for b in bin(ord(c))[2:]:
            if b == '1':
                correct_val += 1
            correct_val *= 3

        a.xor(correct_val)

        a.reverse(i+1)
        a.reverse(i+2)
        a.or_()
        a.reverse(i+1)
        a.reverse(i)

    a.jnz('fail')
    a.println('Correct!')
    a.exit()

    a.label('fail')
    a.println('Incorrect password!')
    a.exit()


def main():
    a = Assembly()

    program(a)

    if len(sys.argv) < 2:
        print(str(a))
    else:
        open(sys.argv[1], 'w+').write(str(a))


if __name__ == '__main__':
    main()
