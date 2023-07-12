#!/usr/bin/python3

import subprocess
import numpy as np

# install nwsrx from here: http://www.kk5jy.net/nwsrx-v1/
# or get the demodulated tones from somewhere else (write your own demodulator, modify
# an existing one to strip the error-correction, cut-and-paste the SAME tones with Audacity
# or similar, etc)
nwsrx_decode = subprocess.run(["nwsrx","warning.wav"], capture_output = True).stdout

all_tones = nwsrx_decode.decode("ascii").splitlines()

# if you're bringing your own demodulated headers, put them here:
headers = all_tones[0:3]

# list of tuples: nth character from each header
headers_t = list(zip(*headers))

padded_flag = ""

for tup in headers_t:
    for c in tup:
        # the flag is in the errors, ie, characters that appear in just one out of three headers.
        # sometimes the error character equals the signal character, so all three are the same;
        # include those characters too
        if tup.count(c) == 3 or tup.count(c) == 1:
            padded_flag += c
            break

flag = padded_flag[padded_flag.index("U"):padded_flag.index("}")+1].lower()

print(flag)
