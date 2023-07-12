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
import itertools
import hashlib
from Crypto.Cipher import AES
import time
import pwnlib.tubes

def handle_pow(r):
    print(r.recvuntil(b'python3 '))
    print(r.recvuntil(b' solve '))
    challenge = r.recvline().decode('ascii').strip()
    p = pwnlib.tubes.process.process(['kctf_bypass_pow', challenge])
    solution = p.readall().strip()
    r.sendline(solution)
    print(r.recvuntil(b'Correct\n'))

# Sometimes we get harder numbers, so just to save time we'll set a time limit
attempts = 1
max_attempts = 5
time_limit = 5.00
while True:
    if attempts > max_attempts:
        print("Took too long...")
        exit(1)
    start = time.time()

    r = pwnlib.tubes.remote.remote('127.0.0.1', 1337)
    print(r.recvuntil(b'== proof-of-work: '))
    if r.recvline().startswith(b'enabled'):
        handle_pow(r)

    print("Getting Public Info...")
    r.recvlineS()
    r.recvlineS()
    int(r.recvlineS().split("=")[1])
    p = int(r.recvlineS().split("=")[1])
    A = int(r.recvlineS().split("=")[1])

    print("Choosing k...")

    # unique prime factorization
    # not too efficient
    print(f"Factoring {p - 1}")
    n = p - 1
    count = 0
    w = None
    for i in itertools.chain([2], itertools.count(3, 2)):
        if n <= 1 or (i >= 100000 and w != None):
            break
        if time.time() - start > time_limit:
            break

        fact = None
        while n % i == 0:
            fact = i
            n //= i

        if fact:
            print(f"    Prime factor: {fact}")
            count += 1
            w = fact
            if (fact >= 100 or count >= 3):
                break

    if time.time() - start > time_limit:
        print("Took too long, restarting...")
        attempts += 1
        r.close()
        continue

    print(f"Subgroup size = {w}")
    k = (p - 1) // w
    print(f"Using {k = }")
    Ak = pow(A, k, p)

    print("Sending...")
    r.sendline(bytes(str(k), "utf-8"))

    print("Receiving ciphertext...")
    r.recvlineS()
    c = long_to_bytes(int(r.recvlineS().split("=")[1]))

    print("Closing...")
    r.close()

    print("Searching for secrets...")
    # Have small subgroup, enumerate secrets
    # compute powers of Ak
    for i in range(1, w + 1):
        S_ = pow(Ak, i, p)

        # test current power
        key = hashlib.md5(long_to_bytes(S_)).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        m = cipher.decrypt(c)
        if b"uiuctf" in m:
            print(m)
            exit(0)

    print("Didn't find flag")
    exit(1)
