#!/usr/bin/env python3

import zlib
import random
import numpy as np

DEPLOY_LEVEL = 0 # 0 or 1 for futuredisk or futuredisk2 respectively
# if this file is modified make sure to sync web/futuredisk/challenge/mount.py and web/futuredisk2/challenge/mount.py!

# note - this is a huge mess, sorry, barely readable lol

# https://www.rfc-editor.org/rfc/rfc1951

# partial bits buffer per DEFLATE spec on bit ordering
# TODO: this could be faster if it were a lazy list of (bytes, trim start bits, trim end bits) instead
# since we move things around quite a lot (and have to re-offset the entire bytes if we do) but only need the
# actual bytes at the way end when outputting
class DeflateBits():
  def __init__(self, bytes=b'', partial="", dsize=0):
    self.bytes = bytes
    self.partial = partial
    self.dsize = dsize # dsize is decompressed size, only managed externally for testing

  def addBits(self, bits):
    # if bits.replace("0", "").replace("1", "") != "":
    #   raise "lol"
    self.partial = bits + self.partial
    while len(self.partial) >= 8:
      self.bytes += int(self.partial[-8:], 2).to_bytes(1, byteorder='little')
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

  def skipBits(self, nbits): # warning: does not change dsize! use only for outputting
    nbytes = nbits // 8
    nbits -= nbytes * 8
    self.bytes = self.bytes[nbytes:]

    if nbits > 0:
      assert(nbits < 8)
      c = DeflateBits(b'', "0"*(8 - nbits))
      c.concat(self)
      self.bytes = c.bytes[1:]
      self.partial = c.partial

    return self

  def finish(self):
    while len(self.partial) != 0:
      self.addBits("0")
    return self

"""
structure of the virtual file:
* fully-zero init chunk (supplies the literal 0)
* X fully-zero match chunks of interestingish sized chunks
* flag inside a normal chunk
* Y fully-zero match chunks of interestingish sized chunks
* end chunk to pad it to FILE_SIZE bytes

FOR PART ONE interestingish just means 32767 = MAX_CHUNK sized chunks

FOR PART TWO interestingish means:
* 3, 4, 5... 32767 sized chunks, then
* 4, 5, 6... 32767 sized chunks
* 5, 6, 7... 32767
* ...
* 50, 51, 52... 32767
* ...
* 32766, 32767
* 32767
* then repeat 3, 4...
this means we have sum_{k=3 to 32767} of k*(k-2) total modulo
https://www.wolframalpha.com/input?i=sum+k*%28k-2%29+of+k%3D3..32767
sum_(k=3)^32767 k (k - 2) = 11726513455105

they can verify the repeat by calculating the modulo and seeking there
and then they can seek backwards from the end twice (once to hit the way end, then skipping back by size)
to find out that it's mismatched

finally, they can binary search using modulo mismatch vs match until flag is found
"""

"""
chunks are up to 8000ish bytes of deflated content
so at 4KiB/s we have half a second to compute each chunk, pretty easy
"""

# flag must end in a null byte so that subsequent match chunks still work
# note - FLAG_X_LOC is not exactly the location! the chunk that includes the loc will be prefixed by the flag chunk
FILE_SIZE_DISK = 0x7fffffffffffffff
FILE_SIZE     = 0x7fffffffffffffff - 18 # minus gzip header size, 10 on top 8 on bottom
FLAG_ONE_LOC  = 0x295215ba3e5300fa
FLAG_TWO_LOC  = 0x56d31cb49db6056b
MAX_CHUNK = 32767

"""
# test values (initial block is 80FCFC large and fixed)
FILE_SIZE_DISK = 0x40000
FILE_SIZE     = 0x40000 - 18
FLAG_ONE_LOC  = 0x20000
FLAG_TWO_LOC  = 0x30000
MAX_CHUNK = 100
# """

# === FIXED CHUNKS ===

# "authentic" cat /dev/zero | gzip --best will make the first block different
# since it has a literal 0 0, and repeats are 0 0 for the match 258 1
# whereas future ones don't need the literals so with the dynamic huffman, match 258 1 becomes 0 1
# see infgen.txt
"""
      1 dynamic                 ! 10 0
      1 count 286 2 18          ! 1110 00001 11101
      1 code 18 2               ! 010 000 000
      1 code 2 2                ! 010 000 000 000 000 000 000 000 000 000 000 000 000
      1 code 1 1                ! 001 000
      1 lens 2                  ! 01
      1 zeros 138               ! 1111111 11
      1 zeros 117               ! 1101010 11
      1 lens 2                  ! 01
      1 zeros 28                ! 0010001 11
      3 lens 1                  ! 0
      1 ! litlen 0 2
      1 ! litlen 256 2
      1 ! litlen 285 1
      1 ! dist 0 1
      1 ! dist 1 1
      2 literal 0               ! 01
  32765 match 258 1             ! 0 0
      1 end                     ! 11
"""
# total 32765 match 00s
INIT_CHUNK = DeflateBits(bytes.fromhex("ecc101010000008090feafee080a") + # header then 1.5 00s
  b'\0' * 8190 + # 8190*4 = 32760 00s
  b'\x80', # 3.5 00s then 1
  "1", # 1 to finish 11 = end
  2 + 32765*258 # size 2 literals and 32765 matches
)

def gen_match_chunk(num):
  """
      1 dynamic                 ! 10 0
      1 count 286 2 18          ! 1110 00001 11101
      1 code 18 1               ! 001 000 000
      1 code 1 1                ! 001 000 000 000 000 000 000 000 000 000 000 000 000 000 000
      1 zeros 138               ! 1111111 1
      1 zeros 118               ! 1101011 1
      1 lens 1                  ! 0
      1 zeros 28                ! 0010001 1
      3 lens 1                  ! 0
      1 ! litlen 256 1
      1 ! litlen 285 1
      1 ! dist 0 1
      1 ! dist 1 1
  32767 match 258 1             ! 0 1 - 32767 or some other number
      1 end                     ! 0
  """
  assert(num >= 3 and num <= 32767)
  # total 32767 match 01s
  aas = (num - 3) // 4

  c = DeflateBits(bytes.fromhex("ecc181000000000090ff6b23a8") + # header then 2.5 01s
    b'\xaa' * aas, # aas*4 01s
    "0", # 0.5 01s
    0
  )
  for _ in range(num - 3 - aas*4):
    c.addBits("01")
  c.addBits("0") # 0 = end
  c.dsize = num*258
  assert(c.bitlen() == (num*2+100))
  return c

# old gen_last_chunk - generates last chunk based on inflated size, we want deflated size to be constant though
# def gen_last_chunk(size):
  # print("last", size)
  # # use match 258s to get up to <258 and then literal zeros to pad out to exactly the end
  # # huffman table taken from initial chunk
  # """
      # 1 dynamic                 ! 10 1 = last!
      # 1 count 286 2 18          ! 1110 00001 11101
      # 1 code 18 2               ! 010 000 000
      # 1 code 2 2                ! 010 000 000 000 000 000 000 000 000 000 000 000 000
      # 1 code 1 1                ! 001 000
      # 1 lens 2                  ! 01
      # 1 zeros 138               ! 1111111 11
      # 1 zeros 117               ! 1101010 11
      # 1 lens 2                  ! 01
      # 1 zeros 28                ! 0010001 11
      # 3 lens 1                  ! 0
      # 1 ! litlen 0 2
      # 1 ! litlen 256 2
      # 1 ! litlen 285 1
      # 1 ! dist 0 1
      # 1 ! dist 1 1
      # X literal 0               ! 01
      # Y match 258 1		          ! 0 0
      # 1 end                     ! 11
  # """
  # # this can happen a little slower since it only happens once, not at runtime
  # c = DeflateBits(bytes.fromhex("edc101010000008090feafee08"), "0", 0) # just header
  # s = size
  # matches = s // 258
  # s -= matches * 258
  # for _ in range(matches):
    # c.addBits('00') # match 258 0
    # c.dsize += 258
  # for _ in range(s):
    # c.addBits('01') # literal 0
    # c.dsize += 1
  # c.addBits('11') # end
  # assert(c.dsize == size)
  # return c

def gen_last_chunk(bitlen):
  # just spew match 258s until we reach bitlen
  # huffman table taken from initial chunk
  """
      1 dynamic                 ! 10 1 = last!
      1 count 286 2 18          ! 1110 00001 11101
      1 code 18 2               ! 010 000 000
      1 code 2 2                ! 010 000 000 000 000 000 000 000 000 000 000 000 000
      1 code 1 1                ! 001 000
      1 lens 2                  ! 01
      1 zeros 138               ! 1111111 11
      1 zeros 117               ! 1101010 11
      1 lens 2                  ! 01
      1 zeros 28                ! 0010001 11
      3 lens 1                  ! 0
      1 ! litlen 0 2
      1 ! litlen 256 2
      1 ! litlen 285 1
      1 ! dist 0 1
      1 ! dist 1 1
      X literal 0               ! 01
      Y match 258 1		          ! 0 0
      1 end                     ! 11
  """
  # this can happen a little slower since it only happens once, not at runtime
  c = DeflateBits(bytes.fromhex("edc101010000008090feafee0802"),
  "0", # header + literal 0 + 3x match 258 1, null bytes can be appended
  1 + 3*258)
  add = bitlen - c.bitlen() - 2 # two for end 11
  assert(add >= 0)

  zeroes = add // 8
  add -= zeroes * 8
  c.bytes += b'\0' * zeroes
  c.dsize += 258*4*zeroes

  while add > 1:
    add -= 2
    c.addBits('00')
    c.dsize += 258
  c.addBits('11')
  if add == 1:
    c.addBits('0')

  assert(c.bitlen() == bitlen)
  return c

# === FLAG CHUNKS ===
"""
Note: the chunk the flag is in only has the flag and a null

{ echo -ne 'uiuctf{binary search means searching a binary stream, right :D}'; head -c 10M /dev/zero; } | gzip --best > with-flag-one.gz
{ echo -ne 'uiuctf{i sincerely hope that was not too contrived, deflate streams are cool}'; head -c 10M /dev/zero; } | gzip --best > with-flag-two.gz
./infgen with-flag-one.gz -dd | uniq -c > with-flag-one.gz.def
./infgen with-flag-two.gz -dd | uniq -c > with-flag-two.gz.def
then manually compare the def's tail with the hex to slice off the last bits of the last byte
and also remove the gzip header
"""
ONE_FLAG = DeflateBits(bytes.fromhex(
  "ecc9b11183301000414af902a8c0318d"
  "bc191914a04088c0e371ef4e7017bbd9"
  "cd5df55ac7ebf3ac2dfb3bce927ddde3"
  "28d9ce3b6adb22e3ff472f79ccd1ebb6"
  "8f782cdfe9"), "0111", # including end = 0111111
  len(b'uiuctf{binary search means searching a binary stream, right :D}\0')
)
TWO_FLAG = DeflateBits(bytes.fromhex(
  "ecc9d109c230140040477903b854a8af"
  "34501b495245c4dd7590bbdf3bebb9cc"
  "f55363d463c99efb3bb6f6c8985b99f1"
  "2a238e3663b6164b3b66afcfbc5de396"
  "eb5e66c6983dcb7d44e9f9efb67f2f97"), "011111", # including two literal 0s and then end = 0111111
  len(b'uiuctf{i sincerely hope that was not too contrived, deflate streams are cool}\0\0')
  # manually added an extra null compared to with-flag-two.gz.def
  # because this needs to be an even bit length otherwise it's obvious
)

# === DEFLATE TESTING ===
def test(chunk, fn="test"):
  # finish a copy
  c = chunk.copy()
  c.finish()
  with open(fn + ".deflate", "wb") as f:
    f.write(c.bytes)
  decomp = zlib.decompressobj(wbits=-zlib.MAX_WBITS).decompress(c.bytes)
  with open(fn + ".bin", "wb") as f:
    f.write(decomp)

# sanity checks for deflate validity
# assert(INIT_CHUNK.copy().bitlen() == 65641)
# assert(gen_match_chunk(1000).bitlen() == 2100)
# assert(gen_match_chunk(1001).bitlen() == 2102)
# assert(gen_match_chunk(32767).bitlen() == 65634)
# test(INIT_CHUNK.copy().concat(ONE_FLAG).concat(gen_last_chunk(12300)))
# test(INIT_CHUNK.copy().concat(TWO_FLAG).concat(gen_last_chunk(45600)))
# test(INIT_CHUNK.copy().concat(TWO_FLAG).concat(gen_last_chunk(10000)))

# === FLAG FILE TESTING ===

# generate the entire flag files for the small case
"""
if FILE_SIZE <= 0x40000:
  c = INIT_CHUNK.copy()
  flag_sent = False
  last_chunk = False
  while not last_chunk:
    next = gen_match_chunk(MAX_CHUNK)
    if not flag_sent and c.bitlen() + next.bitlen() > FLAG_ONE_LOC*8:
      flag_sent = True
      next = ONE_FLAG.copy()
    elif c.bitlen() + next.bitlen() >= FILE_SIZE*8 - 200:
      last_chunk = True
      next = gen_last_chunk(FILE_SIZE*8 - c.bitlen())
    c.concat(next)
  assert(flag_sent)
  c.finish()
  TEST_ONE = c # for inversion testing
  test(c, "test-out-flag-one")

  c = INIT_CHUNK.copy()
  flag_sent = False
  last_chunk = False
  i = MAX_CHUNK
  si = MAX_CHUNK
  while not last_chunk:
    i += 1
    if i > MAX_CHUNK:
      si += 1
      if si > MAX_CHUNK:
        si = 3
      i = si

    next = gen_match_chunk(i)
    if not flag_sent and c.bitlen() + next.bitlen() > FLAG_TWO_LOC*8:
      flag_sent = True
      next = TWO_FLAG.copy().concat(next)
    elif c.bitlen() + next.bitlen() >= FILE_SIZE*8 - 200:
      last_chunk = True
      next = gen_last_chunk(FILE_SIZE*8 - c.bitlen())
    c.concat(next)
  assert(flag_sent)
  c.finish()
  TEST_TWO = c # for inversion testing
  test(c, "test-out-flag-two")
# """

# === ONE INVERSION ===

MATCH_CHUNK = [None]*3 + [gen_match_chunk(num) for num in range(3, MAX_CHUNK+1)]
INIT_BITLEN = INIT_CHUNK.bitlen()

ONE_MATCH = MATCH_CHUNK[MAX_CHUNK]
ONE_MATCH_BITLEN = ONE_MATCH.bitlen()

ONE_FLAG_NO = (FLAG_ONE_LOC*8 - INIT_BITLEN) // ONE_MATCH_BITLEN
ONE_FLAG_OFFSET = INIT_BITLEN + ONE_FLAG_NO*ONE_MATCH_BITLEN
ONE_FLAG_BITLEN = ONE_FLAG.bitlen()

ONE_LAST_NO = (FILE_SIZE*8 - INIT_BITLEN - ONE_FLAG_BITLEN - 200) // ONE_MATCH_BITLEN
ONE_LAST_OFFSET = INIT_BITLEN + ONE_FLAG_BITLEN + ONE_LAST_NO*ONE_MATCH_BITLEN
ONE_LAST_BITLEN = FILE_SIZE*8 - ONE_LAST_OFFSET
ONE_LAST = gen_last_chunk(ONE_LAST_BITLEN)

"""
bitoffset = bit location in the deflate stream to start

invert will find the chunk that includes the bitoffset, and return the rest of the chunk
it returns at least one bit

remember, chunks are at most ~8200 bytes of output
"""
def one_invert(bitoffset):
  assert(bitoffset >= 0)
  assert(bitoffset < FILE_SIZE*8)
  if bitoffset < INIT_BITLEN:
    return INIT_CHUNK.copy().skipBits(bitoffset)
  elif bitoffset < ONE_FLAG_OFFSET:
    return ONE_MATCH.copy().skipBits((bitoffset - INIT_BITLEN) % ONE_MATCH_BITLEN)
  elif bitoffset < ONE_FLAG_OFFSET + ONE_FLAG_BITLEN:
    return ONE_FLAG.copy().skipBits(bitoffset - ONE_FLAG_OFFSET)
  elif bitoffset < ONE_LAST_OFFSET:
    return ONE_MATCH.copy().skipBits((bitoffset - INIT_BITLEN - ONE_FLAG_BITLEN) % ONE_MATCH_BITLEN)
  else:
    return ONE_LAST.copy().skipBits(bitoffset - ONE_LAST_OFFSET)

def test_invert(invert, TEST_GOOD, bitoffset):
  chunk = invert(bitoffset)
  assert(chunk.bitlen() > 0)
  good = TEST_GOOD.copy().skipBits(bitoffset)

  # print(bytes(good.bytes[:100]))
  # print(chunk.bytes[:100])
  # print()
  assert(good.bytes.startswith(chunk.bytes))
  # test trailing bits
  partialsize = len(chunk.partial)
  if partialsize > 0:
    b = int(chunk.partial, 2)
    if len(good.bytes) == len(chunk.bytes):
      # take partial from good
      c = int(good.partial, 2)
    else:
      # take entire byte from good
      c = good.bytes[len(chunk.bytes)]
    assert b == (((1 << partialsize) - 1) & c), (bitoffset, hex(b), hex(c))

# for r in [INIT_BITLEN, ONE_FLAG_OFFSET, ONE_FLAG_OFFSET + ONE_FLAG_BITLEN, ONE_LAST_OFFSET]:
  # for s in range(-10, 11):
    # print(r+s)
    # test_invert(one_invert, TEST_ONE, r+s)

# === TWO CONSTANTS ===

"""
gen_match_chunk(n).bitlen() is always n*2+100
seq has n=3, 4... 32767 sized chunks
"""

# find median root with numpy, then manually check a few integer values to round down correctly
# the polynomials are constructed from the integer series so an epsilon of 0.5 should be okay
def int_root(poly):
  roots = np.roots(poly)
  root = round(min(roots[roots>-0.5]))
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

# uhh the polynomials depend on on MAX_CHUNK and i am using wolfram alpha to get them so...
if MAX_CHUNK == 100:
  m = 0
elif MAX_CHUNK == 32767:
  m = 1
else:
  assert(False) # sorry

# just do math here without worrying about the flag chunk
def two_seq_invert(bitlen):
  # sum i=3 to 100 of sum of j=i to 100 of (2j+100) = 1141602
  # sum i=3 to 32767 of sum of j=i to 32767 of (2j+100) = 23506705809710
  # modulo for repeating the entire sequence
  mm = [1141602, 23506705809710][m]
  modulos = bitlen // mm
  modulo_offset = bitlen % mm

  # sum i=3 to x of sum of j=i to 100 of (2j+100) = -x^3/3 - 50 x^2 + (60451 x)/3 - 40098
  # sum i=3 to x of sum of j=i to 32767 of (2j+100) = -x^3/3 - 50 x^2 + (3230957419 x)/3 - 2153971410
  if m == 0:
    (row, rem) = int_root([-1/3, -50, 60451/3, -40098 - modulo_offset])
  else:
    (row, rem) = int_root([-1/3, -50, 3230957419/3, -2153971410 - modulo_offset])
  row += 1

  # decompose rem into col and offset using same strategy
  # sum of j=x to y of (2j+100) = y^2 + 101 y + 100 -x^2 - 99 x
  (col, rem) = int_root([1, 101, 100 - row*row - 99*row - rem])
  col += 1

  return ((modulos, row, col), rem)

def two_seq_convert(modulos, row, col):
  # same polynomials in reverse, just use the forward polynomials ( = summation)
  bitlen = ([1141602, 23506705809710][m])*modulos
  col -= 1
  bitlen += round(np.polyval([1, 101, 100 - row*row - 99*row], col))
  row -= 1
  if m == 0:
    bitlen += round(np.polyval([-1/3, -50, 60451/3, -40098], row))
  else:
    bitlen += round(np.polyval([-1/3, -50, 3230957419/3, -2153971410], row))
  return bitlen

TWO_FLAG_NO = two_seq_invert(FLAG_TWO_LOC*8 - INIT_BITLEN)[0]
TWO_FLAG_OFFSET = INIT_BITLEN + two_seq_convert(*TWO_FLAG_NO)
TWO_FLAG_BITLEN = TWO_FLAG.bitlen()

TWO_LAST_NO = two_seq_invert(FILE_SIZE*8 - INIT_BITLEN - TWO_FLAG_BITLEN - 200)[0]
TWO_LAST_OFFSET = INIT_BITLEN + TWO_FLAG_BITLEN + two_seq_convert(*TWO_LAST_NO)
TWO_LAST_BITLEN = FILE_SIZE*8 - TWO_LAST_OFFSET
TWO_LAST = gen_last_chunk(TWO_LAST_BITLEN)

def two_invert(bitoffset):
  assert(bitoffset >= 0)
  assert(bitoffset < FILE_SIZE*8)
  if bitoffset < INIT_BITLEN:
    return INIT_CHUNK.copy().skipBits(bitoffset)
  elif bitoffset < TWO_FLAG_OFFSET:
    ((_, _, col), rem) = two_seq_invert(bitoffset - INIT_BITLEN)
  elif bitoffset < TWO_FLAG_OFFSET + TWO_FLAG_BITLEN:
    return TWO_FLAG.copy().skipBits(bitoffset - TWO_FLAG_OFFSET)
  elif bitoffset < TWO_LAST_OFFSET:
    ((_, _, col), rem) = two_seq_invert(bitoffset - INIT_BITLEN - TWO_FLAG_BITLEN)
  else:
    return TWO_LAST.copy().skipBits(bitoffset - TWO_LAST_OFFSET)

  # get a match that's the right size
  return MATCH_CHUNK[col].copy().skipBits(rem)

# for r in [INIT_BITLEN, TWO_FLAG_OFFSET, TWO_FLAG_OFFSET + TWO_FLAG_BITLEN, TWO_LAST_OFFSET]:
  # for s in range(-10, 11):
    # print(r+s)
    # test_invert(two_invert, TEST_TWO, r+s)

# while True:
  # r = random.randint(0, TEST_TWO.bitlen())
  # print(r, TEST_TWO.bitlen())
  # test_invert(two_invert, TEST_TWO, r)

# check every byte offset (even byte offsets so it's fast...er):
"""
for r in range(0, TEST_ONE.bitlen()//8):
  r *= 8
  print(round(r/TEST_ONE.bitlen()*100), r)
  test_invert(one_invert, TEST_ONE, r)

for r in range(0, TEST_TWO.bitlen()//8):
  r *= 8
  print(round(r/TEST_TWO.bitlen()*100), r)
  test_invert(two_invert, TEST_TWO, r)
# """

# === CRC ===
# print(hex(zlib.crc32(TEST_ONE.bytes)))
# a = zlib.crc32(TEST_ONE.bytes[:0x11])
# b = zlib.crc32(TEST_ONE.bytes[0x11:])

# print(hex(a), hex(b), len(TEST_ONE.bytes[0x11:]))
# lol never mind

# === FUSE ===
import os, stat, errno, fuse
fuse.fuse_python_api = (0, 2)

FILE_NAME = ['haystack.bin.gz', 'haystack2.bin.gz'][DEPLOY_LEVEL]

class HaystackFS(fuse.Fuse):
  def getattr(self, path):
    st = fuse.Stat()
    if path == '/':
      st.st_mode = stat.S_IFDIR | 0o755
      st.st_nlink = 3
    elif path == '/' + FILE_NAME:
      st.st_mode = stat.S_IFREG | 0o444
      st.st_nlink = 1
      st.st_size = FILE_SIZE_DISK
      st.st_atime = 4842259636
      st.st_mtime = 4842259636
      st.st_ctime = 4842259636
    else:
      return -errno.ENOENT
    return st

  def readdir(self, path, offset):
    if path != '/':
      return -errno.ENOENT
    for r in  '.', '..', FILE_NAME:
      yield fuse.Direntry(r)

  def open(self, path, flags):
    if path != '/' + FILE_NAME:
      return -errno.ENOENT
    accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
    if (flags & accmode) != os.O_RDONLY:
      return -errno.EACCES

  def read(self, path, size, offset):
    # print("read", size, offset)
    if path == '/' + FILE_NAME:
      invert = [one_invert, two_invert][DEPLOY_LEVEL]
    else:
      return -errno.ENOENT

    buf = DeflateBits(bytes.fromhex("1f8b0800000000000203")[offset:]) # gzip header
    bitoffset = (offset - 10)*8 # bits
    while True:
      bithead = bitoffset + buf.bitlen()
      if bithead >= FILE_SIZE*8:
        # add gzip footer and break
        buf.concat(DeflateBits(bytes.fromhex("0000000000000000")))
        # could calculate crc using crc32_combine trick, and dsize, but ehhhh
        break
      if len(buf.bytes) >= size:
        # already enough bytes
        break

      # print("invert", bithead)
      buf.concat(invert(bithead))
    # print("ret", len(buf.bytes[:size]))
    return buf.bytes[:size]

def main():
  server = HaystackFS(version="%prog " + fuse.__version__,
    usage="\nHaystackFS, for all your haystack needs\n\n" + fuse.Fuse.fusage,
    dash_s_do='setsingle')

  server.parse(errex=1)
  server.main()

if __name__ == '__main__':
  main()
# """
