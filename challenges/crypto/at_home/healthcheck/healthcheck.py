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

# From Chapter 1 Exercise 4 of Koblitz - Algebraic Aspects of Cryptography

import os
from Crypto.Util.number import long_to_bytes

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "../challenge/chal.txt")
with open(filename) as f:
    # get given values
    vals = f.readlines()
    e = int(vals[0].split("=")[1])
    n = int(vals[1].split("=")[1])
    c = int(vals[2].split("=")[1])

    # compute modular inverse
    d = pow(e, -1, n)  # = e^-1 (mod n)

    # c = flag * e (mod n)
    # => c * e^-1  = flag * e * e^-1 = flag (mod n)
    flag = c * d % n

    # convert
    res = long_to_bytes(flag)
    if b'uiuctf{' not in res:
        exit(1)
    else:
        print(res)
        exit(0)

# should never get here
exit(1)
