#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import zlib

url = "http://localhost:1337/haystack.bin.gz"

# set to false to use memoized values for healthcheck
SOLVE_FROM_SCRATCH = True


def get_bits(offset, bitsize=2):
    start = offset // 8

    bits = ""
    ptr = offset - (start * 8)
    # warning - endianness!!! we can't naively convert to binary
    # ptr is offset FROM THE END of where we are
    while True:
        end = start + 5*1024
        # print("\trequested", start, end)
        r = requests.get(
            url, headers={"Range": "bytes=" + str(start) + "-" + str(end-1)})
        assert (len(r.content) == end-start)

        bits = ''.join((f'{a:08b}') for a in r.content[::-1]) + bits

        while ptr + bitsize <= len(bits):
            yield bits[len(bits)-(ptr + bitsize):len(bits)-ptr]
            ptr += bitsize
        bits = bits[:len(bits)-ptr]
        ptr = 0

        start = end


# assume start_a is past first chunk but before flag, start_b is past flag before end chunk
start_a = 1000*1024*8
# 8589934592 obtained from nginx index size
start_b = (8589934592*1073741824 - 1000*1024)*8

block_size = None if SOLVE_FROM_SCRATCH else 65634
confirms = 0
if block_size is None:
    print("finding block size")

    twos = 0
    in_chunk = False
    offset = start_a  # 100k in bits
    last_begin = None
    for twobits in get_bits(offset):
        if twobits == "01":
            twos += 1
        else:
            twos = 0

        if twos > 32:
            # new chunk!
            chunk_begin = offset - twos

            if not in_chunk:
                if last_begin is not None:
                    new_block_size = chunk_begin - last_begin
                    print("new chunk", chunk_begin, "size=", new_block_size)
                    if new_block_size == block_size:
                        confirms += 1
                    else:
                        block_size = new_block_size
                        confirms = 0
                    if confirms > 5:
                        break
                last_begin = chunk_begin
                in_chunk = True

        if in_chunk and twos == 0:
            print("chunk ended")
            in_chunk = False

        offset += 2
print()

print("moving start_a forward until it's a block boundary")
twos = 0
in_chunk = False
for twobits in get_bits(start_a):
    start_a += 2

    if twobits == "01":
        twos += 1
    else:
        twos = 0
        if in_chunk:
            break

    if twos > 32:
        in_chunk = True
start_a -= 2
print("start_a", start_a)
print()

interblock_size = 160  # obtained via inspection:
"""
print(next(get_bits(start_a, 160)))
print(next(get_bits(start_a + block_size, 160)))
print(next(get_bits(start_a + block_size*2, 160)))

print(next(get_bits(start_b, 160)))
print(next(get_bits(start_b + block_size, 160)))
print(next(get_bits(start_b + block_size*2, 160)))
"""

a_loc = None if SOLVE_FROM_SCRATCH else 362917535825702
if a_loc is None:
    print("binary search time!!")
    a = 0
    b = (start_b - start_a) // block_size
    while b-a > 1:
        print("search space:", b-a)
        c = (a + b) // 2
        bits = next(get_bits(start_a + c*block_size, interblock_size))
        if bits == "01" * (interblock_size//2):
            # after flag
            b = c
        else:
            # before flag
            a = c
    print("found a_loc", a)
    a_loc = a

# half a block but make sure it's still even
bits = next(get_bits(start_a + a_loc*block_size -
            (block_size // 4)*2, block_size))

while bits[-2:] == "01":
    bits = bits[:-2]

# test offsets until success
for i in range(len(bits)):
    deflate = bits[:len(bits)-i]

    # make into bytes
    b = b''
    while len(deflate) >= 8:
        b += bytes([int(deflate[-8:], 2)])
        deflate = deflate[:-8]

    # decompress flag
    try:
        flag = zlib.decompressobj(wbits=-zlib.MAX_WBITS).decompress(b)
    except Exception:
        print("failed decomp offset", i)
        continue
    print("success!", flag.rstrip(b'\0'))
    break
