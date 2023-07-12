#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from Crypto.Util.number import long_to_bytes
from random import randint
import pwnlib.tubes

def handle_pow(r):
    print(r.recvuntil(b'python3 '))
    print(r.recvuntil(b' solve '))
    challenge = r.recvline().decode('ascii').strip()
    p = pwnlib.tubes.process.process(['kctf_bypass_pow', challenge])
    solution = p.readall().strip()
    r.sendline(solution)
    print(r.recvuntil(b'Correct\n'))

r = pwnlib.tubes.remote.remote('127.0.0.1', 1337)
print(r.recvuntil(b'== proof-of-work: '))
if r.recvline().startswith(b'enabled'):
    handle_pow(r)


print("Getting public info...")
r.recvlineS()
r.recvlineS()
g = int(r.recvlineS().split("=")[1])
p = int(r.recvlineS().split("=")[1])
A = int(r.recvlineS().split("=")[1])

print("Getting ciphertext...")
r.recvlineS()
c1_ = int(r.recvlineS().split("=")[1])
c2_ = int(r.recvlineS().split("=")[1])

print("Generating ciphertext...")
r.recvlineS()
known = int.from_bytes(b"knownplaintext", "big")
k = randint(2, p - 1)
c1_ = pow(g, k, p)
c2_ = pow(A, k, p)
c2_ = (known * c2_) % p
print("Sending...")
r.sendline(bytes(str(c1_), "utf-8"))
r.sendline(bytes(str(c2_), "utf-8"))

print("Decrypting...")
r.recvlineS()
m = int(r.recvlineS().split("=")[1])
r.close()
plain = pow(known, -1, p)
plain = (m * plain) % p
plain = long_to_bytes(plain)

if b'uiuctf{' not in plain:
    exit(1)
else:
    print(plain)

r.close()

exit(0)
