from sage.all import *
import random

random.seed(0x69420)

def gen_prime(num_bits):
    tmp = random.getrandbits(num_bits)
    while True:
        if is_prime(tmp):
            return tmp
        tmp += 1


for i in range(10):
    p = gen_prime(192)
    print(i, p, factor(p-1))
