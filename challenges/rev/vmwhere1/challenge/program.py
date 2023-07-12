#!/usr/bin/env python3

import sys
from highlevel import Assembly

FLAG = 'uiuctf{ar3_y0u_4_r3al_vm_wh3r3_(gpt_g3n3r4t3d_th1s_f14g)}'


def program(a):
    a.println('Welcome to VMWhere 1!')
    a.println('Please enter the password:')

    accum = 0
    a.push(0)

    for i, c in enumerate(FLAG):
        a.inputn(1)
        a.dup()
        a.shr(4)
        a.xor()

        accum ^= ord(c) ^ (ord(c) >> 4)
        a.xor()

        a.dup()
        a.xor(accum)
        a.jnz('fail')
        a.popn(1)

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
