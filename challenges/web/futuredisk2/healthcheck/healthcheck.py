#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import zlib
import numpy as np

url = "http://localhost:1337/haystack2.bin.gz"

# set to false to use memoized values for healthcheck
SOLVE_FROM_SCRATCH = True

"""
so the user has to figure out:
* deflate blocks are sequential in size (by number of match blocks)
* size increases 3-4-5... 32767 (requires binary search to determine end)
* next sequence is 4-5-6... 32767
* then do some math to find 11726513455105 as the large modulo
* then download that area to find it reset from 32766-32767-3-4-5-6...
* then do some more math to find how to calculate any arbitrary bit offset's data
* then, finally, binary search
most of that is manual work and manual-ish binary searching
so what this solve script has is just the final step, assuming the structure is known, but without knowing the flag offset or flag
"""

# === begin copied from mount.py ===


class DeflateBits():
    def __init__(self, bytes=b'', partial="", dsize=0):
        self.bytes = bytes
        self.partial = partial
        self.dsize = dsize  # dsize is decompressed size, only managed externally for testing

    def addBits(self, bits):
        # if bits.replace("0", "").replace("1", "") != "":
        #   raise "lol"
        self.partial = bits + self.partial
        while len(self.partial) >= 8:
            self.bytes += int(self.partial[-8:],
                              2).to_bytes(1, byteorder='little')
            self.partial = self.partial[:-8]
        return self

    def concat(self, next):
        if len(self.partial) == 0:
            # fast case
            self.bytes += next.bytes
            self.partial = next.partial
            self.dsize += next.dsize
            return self
        # slow case
        for b in next.bytes:
            self.addBits('{0:08b}'.format(b))
        self.addBits(next.partial)
        self.dsize += next.dsize
        return self

    def copy(self):
        return DeflateBits(self.bytes[:], self.partial[:], self.dsize)

    def bitlen(self):
        return len(self.bytes)*8 + len(self.partial)

    def skipBits(self, nbits):  # warning: does not change dsize! use only for outputting
        nbytes = nbits // 8
        nbits -= nbytes * 8
        self.bytes = self.bytes[nbytes:]

        if nbits > 0:
            assert (nbits < 8)
            c = DeflateBits(b'', "0"*(8 - nbits))
            c.concat(self)
            self.bytes = c.bytes[1:]
            self.partial = c.partial

        return self

    def finish(self):
        while len(self.partial) != 0:
            self.addBits("0")
        return self


def gen_match_chunk(num):
    assert (num >= 3 and num <= 32767)
    # total 32767 match 01s
    aas = (num - 3) // 4

    c = DeflateBits(bytes.fromhex("ecc181000000000090ff6b23a8") +  # header then 2.5 01s
                    b'\xaa' * aas,  # aas*4 01s
                    "0",  # 0.5 01s
                    0
                    )
    for _ in range(num - 3 - aas*4):
        c.addBits("01")
    c.addBits("0")  # 0 = end
    c.dsize = num*258
    assert (c.bitlen() == (num*2+100))
    return c

# find median root with numpy, then manually check a few integer values to round down correctly
# the polynomials are constructed from the integer series so an epsilon of 0.5 should be okay


def int_root(poly):
    roots = np.roots(poly)
    root = round(min(roots[roots > -0.5]))
    lastp = None
    for i in range(root-2, root+2):
        p = np.polyval(poly, i)
        if p > 0.5:
            if lastp is not None:
                return i-1, -round(lastp)
            else:
                assert False
        lastp = p
    assert False

# just do math here without worrying about the flag chunk


def two_seq_invert(bitlen):
    # sum i=3 to 32767 of sum of j=i to 32767 of (2j+100) = 23506705809710
    # modulo for repeating the entire sequence
    mm = 23506705809710
    modulos = bitlen // mm
    modulo_offset = bitlen % mm

    # sum i=3 to x of sum of j=i to 32767 of (2j+100) = -x^3/3 - 50 x^2 + (3230957419 x)/3 - 2153971410
    (row, rem) = int_root(
        [-1/3, -50, 3230957419/3, -2153971410 - modulo_offset])
    row += 1

    # decompose rem into col and offset using same strategy
    # sum of j=x to y of (2j+100) = y^2 + 101 y + 100 -x^2 - 99 x
    (col, rem) = int_root([1, 101, 100 - row*row - 99*row - rem])
    col += 1

    return ((modulos, row, col), rem)


def two_seq_convert(modulos, row, col):
    # same polynomials in reverse, just use the forward polynomials ( = summation)
    bitlen = 23506705809710*modulos
    col -= 1
    bitlen += round(np.polyval([1, 101, 100 - row*row - 99*row], col))
    row -= 1
    bitlen += round(np.polyval([-1/3, -50, 3230957419/3, -2153971410], row))
    return bitlen


MATCH_CHUNK = [None]*3 + [gen_match_chunk(num) for num in range(3, 32767+1)]

# === end copied from mount.py ===
print("match chunk generation done")
print()

START_OFFSET = 65641 + 8*10  # manual inspection, = INIT_BITLEN + 8*gzip header size


def calc_bytes_one(bitoffset):
    ((_, _, col), rem) = two_seq_invert(bitoffset)
    return MATCH_CHUNK[col].copy().skipBits(rem)


def calc_bytes_two(offset):
    bitoffset = offset*8 - START_OFFSET  # bit offset
    assert bitoffset > 0

    # calculate this and next block since usually we don't have a header so it's just 0x55's which is a lot of false positives
    bits = calc_bytes_one(bitoffset)
    bitoffset += bits.bitlen()
    bits.concat(calc_bytes_one(bitoffset))
    return bits.bytes


def get_bytes(offset, size=8205):
    start = offset
    end = start + size
    r = requests.get(
        url, headers={"Range": "bytes=" + str(start) + "-" + str(end-1)})
    assert (len(r.content) == size)
    return r.content


# assume start_a is past first chunk but before flag, start_b is past flag before end chunk
a = 1000*1024
# 8589934592 obtained from nginx index size
b = 8589934592*1073741824 - 1000*1024

a_loc = None if SOLVE_FROM_SCRATCH else 6256375869413382493
if a_loc is None:
    print("binary search time!!")
    while b-a > 1:
        print("search space:", b-a)
        c = (a + b) // 2
        calc = calc_bytes_two(c)
        get = get_bytes(c, len(calc))
        if calc == get:
            # before flag
            a = c
        else:
            # after flag
            b = c
    print("found a_loc", a)
    a_loc = a

b = get_bytes(a_loc)
# print(b) - from manually looking at this, we find 7850 into the offset to be the non-U's
b = DeflateBits(b[7850:])

# brute force bitlens to finally decompress
for i in range(b.bitlen()):
    try:
        flag = zlib.decompressobj(
            wbits=-zlib.MAX_WBITS).decompress(b.copy().skipBits(i).finish().bytes)
    except Exception:
        # print("failed decomp offset", i)
        continue
    if b'uiuctf' not in flag:
        print("not flag at", i, flag)
    else:
        print("success!", flag.rstrip(b'\0'))
        break
