# futuredisk writeup

by [kuilin](https://kuilin.net)

Futuredisk and futuredisk2 were two web challenges I submitted to [UIUCTF 2023](https://2023.uiuc.tf/). Here's my write-up of the solution.

I will be hosting these challenges on my personal CTFd at [ctf.kuilin.net](https://ctf.kuilin.net/) shortly after UIUCTF stops hosting them, so if you want to try them out, and the links below stop working, try replacing `-web.chal.uiuc.tf` with `.chal.ctf.kuilin.net`.

## futuredisk

I'm from the year 2123. Here's what I did:

* Mounted my 10 exabyte flash drive
* fallocate -l 8E haystack.bin
* dd if=flag.txt bs=1 seek=[REDACTED] conv=notrunc of=haystack.bin
* gzip haystack.bin
* Put haystack.bin.gz on my web server for you to download
* HTTP over Time Travel is a bit slow, so I hope 
it made it a little faster to download :)

https://futuredisk-web.chal.uiuc.tf/haystack.bin.gz

## futuredisk solution

We get a link. Naively clicking on the link reveals an 8 exabyte[^1] gzipped file[^2] whose download rate is rate limited at 4K/s[^3], so clearly, it cannot be downloaded in the 2-day CTF window even if you had the space for it or processed it as it was downloading.

[^1]: I use exabytes and EB to mean exbibytes and EiB here, in order to deliberately cause chaos in the fabric of reality.

[^2]: The challenge flavor text is a little wrong, here, because it indicates that haystack.bin is 8 EB before gzipping, but both files are actually exactly 8EB minus one byte after gzipping. The files are this size because one byte larger and the underlying FUSE mount doesn't like it.

[^3]: If your internet speed is lower than this, and as a result didn't realize it was a server-side rate limit, sorry.

Checking the response headers on the link, or navigating to the root of the website, reveals that nginx is serving the file, and the auto-generated nginx index HTML, the `Content-Length` response header, and the `ETag` response header all confirm that this file is indeed 8EB.

The response headers also specify `Accept-Ranges: bytes` which means we can actually partially download any range of the file with a `Content-Range` request header. Either by metagaming and considering how the infra might be hosted without a time machine[^4], or by trying to download the end of the file[^7] `curl -r 9223372036854775700- https://futuredisk-web.chal.uiuc.tf/haystack.bin.gz | xxd` and observing that it doesn't take forever, we can reason that the entire file can be seeked in constant time.

[^4]: The UIUCTF admins do actually have a time machine, but the Google Cloud Dedicated Interconnect we provisioned to connect it to our challenge hosting infrastructure was outside our budget.

[^7]: Per the gzip RFC, the end of the file should contain a CRC32 of the uncompressed input, and the truncated file size. I was originally planning on computing the CRC32 using either `crc32_combine` or brute force (it has a small state space) but did not have time to implement it, hence the zero CRC32. Mathematical solutions exist to this problem that exploit the linearity of CRC32, too.

Since the entire file can be seeked arbitrarily, and the challenge flavor text says that the flag is _somewhere_ within many, many null bytes, the next thought would be, can we somehow binary search the file.

Either by observing `cat /dev/zero | gzip | hexdump` or by reasoning about how gzip works on streams and has likely not that much state, we know that if you send zero bytes into gzip endlessly, the gzipped output will eventually repeat modulo some number of bytes. There is almost certainly enough zero bytes to reach this stable state from the start of haystack.bin.gz to the flag. Then, when the flag is emitted, the pattern will be disrupted, and since the flag's disruption is likely not exactly the same size as the gzipped nulls, the repeat modulo the same number of bytes will be different. Knowing this, we have a strategy to binary search for the flag.

More specifically, first we download bytes from the start of the file until we see the repeat, and then use that repeat to project forward to what we _expect_ a download of an arbitrary byte offset to contain. The actual data is mostly 0x55[^fivefive] interspersed with other data, so it's better to download that other data to get a better signature. Then, if we get what we expect, we're before the flag - if we don't, we're after or at the flag.

[^fivefive]: If you get into the nitty-gritty of the DEFLATE stream, this is because 0x55 is 0b01010101 which corresponds to four match instructions `01` in the bit stream. Each of these match instructions, after being decoded by the dynamic Huffman table at the start of each chunk, tells the decompressor to repeat the last 1 byte 258 times.

Finally, since DEFLATE streams are bit streams, the flag can appear at any bit offset. Once we get the first unexpected byte, we can brute force bit offsets into the data to try to inflate the flag. See my solve.py[^5] for code.

[^5]: The code is extraordinarily messy, both due to time constraints and due to me not knowing about `BitInputStream` and rolling my own. Sorry about that. If it helps, you can also cross-reference `solve.py` with `mount.py` which is the file that mounts the FUSE filesystem that nginx (stock, unmodified) reads the massive file from.

## futuredisk2

Like futuredisk, but a little worse.

https://futuredisk2-web.chal.uiuc.tf/haystack2.bin.gz

## futuredisk2 solution

As it says on the tin, this one is like futuredisk, but a little worse. If we download the beginning of the file, we see, after the first 2K which is identical to the first part:[^6]

```
00002000: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00002010: 0000 0000 0000 80d9 8303 0100 0000 0020  ...............
00002020: ffd7 4650 610f 0e04 0000 0000 80fc 5f1b  ..FPa........._.
00002030: 4115 f6e0 4000 0000 0000 c8ff b511 5485  A...@.........T.
00002040: 3d38 1000 0000 0000 f27f 6d04 5585 3d38  =8........m.U.=8
00002050: 1000 0000 0000 f27f 6d04 5515 f6e0 4000  ........m.U...@.
00002060: 0000 0000 c8ff b511 5455 610f 0e04 0000  ........TUa.....
00002070: 0000 80fc 5f1b 4155 55d8 8303 0100 0000  ...._.AUU.......
00002080: 0020 ffd7 4650 5555 d883 0301 0000 0000  . ..FPUU........
00002090: 20ff d746 5055 5561 0f0e 0400 0000 0080   ..FPUUa........
000020a0: fc5f 1b41 5555 15f6 e040 0000 0000 00c8  ._.AUU...@......
000020b0: ffb5 1154 5555 853d 3810 0000 0000 00f2  ...TUU.=8.......
000020c0: 7f6d 0455 5555 853d 3810 0000 0000 00f2  .m.UUU.=8.......
000020d0: 7f6d 0455 5555 15f6 e040 0000 0000 00c8  .m.UUU...@......
000020e0: ffb5 1154 5555 5561 0f0e 0400 0000 0080  ...TUUUa........
000020f0: fc5f 1b41 5555 5555 d883 0301 0000 0000  ._.AUUUU........
00002100: 20ff d746 5055 5555 55d8 8303 0100 0000   ..FPUUUU.......
00002110: 0020 ffd7 4650 5555 5555 610f 0e04 0000  . ..FPUUUUa.....
00002120: 0000 80fc 5f1b 4155 5555 5515 f6e0 4000  ...._.AUUUU...@.
00002130: 0000 0000 c8ff b511 5455 5555 5585 3d38  ........TUUUU.=8
00002140: 1000 0000 0000 f27f 6d04 5555 5555 5585  ........m.UUUUU.
00002150: 3d38 1000 0000 0000 f27f 6d04 5555 5555  =8........m.UUUU
00002160: 5515 f6e0 4000 0000 0000 c8ff b511 5455  U...@.........TU
00002170: 5555 5555 610f 0e04 0000 0000 80fc 5f1b  UUUUa........._.
00002180: 4155 5555 5555 55d8 8303 0100 0000 0020  AUUUUUU........
00002190: ffd7 4650 5555 5555 5555 d883 0301 0000  ..FPUUUUUU......
000021a0: 0000 20ff d746 5055 5555 5555 5561 0f0e  .. ..FPUUUUUUa..
000021b0: 0400 0000 0080 fc5f 1b41 5555 5555 5555  ......._.AUUUUUU
000021c0: 15f6 e040 0000 0000 00c8 ffb5 1154 5555  ...@.........TUU
000021d0: 5555 5555 853d 3810 0000 0000 00f2 7f6d  UUUU.=8........m
000021e0: 0455 5555 5555 5555 853d 3810 0000 0000  .UUUUUUU.=8.....
000021f0: 00f2 7f6d 0455 5555 5555 5555 15f6 e040  ...m.UUUUUUU...@
00002200: 0000 0000 00c8 ffb5 1154 5555 5555 5555  .........TUUUUUU
00002210: 5561 0f0e 0400 0000 0080 fc5f 1b41 5555  Ua........._.AUU
00002220: 5555 5555 5555 d883 0301 0000 0000 20ff  UUUUUU........ .
00002230: d746 5055 5555 5555 5555 55d8 8303 0100  .FPUUUUUUUU.....
00002240: 0000 0020 ffd7 4650 5555 5555 5555 5555  ... ..FPUUUUUUUU
00002250: 610f 0e04 0000 0000 80fc 5f1b 4155 5555  a........._.AUUU
```

[^6]: A genuine Damascus steel hexdump!

Clearly, this doesn't repeat as simply as the first part. What this pattern actually is can be ascertained by looking at the actual DEFLATE stream. I used [infgen](https://github.com/madler/infgen/tree/master) for developing and solving this challenge, but other tools exist.

Upon disassembling the DEFLATE stream, one sees that the file is comprised of concatenations[^8] of chunks:[^9]

[^8]: Remember, these are bit streams, so a concatenation of two bit streams may not be on a byte boundary.

[^9]: This is `infgen` output piped to `uniq -c`, so the first number is the number of occurences of the line, and the next number the actual bytes.

```
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
  12345 match 258 1             ! 0 1 - 32767 or some other number
      1 end                     ! 0
```

Where 12345 is variable, and it starts at 3 and increases by one every chunk. This means the length in bits of the $i$-th chunk is $2i+100$, so the length in bits of the first $y$ chunks is $\Sigma_{i=3}^{y+3}(2i+100)$ which is a quadratic polynomial, which we can invert with math.

However, if we assume this pattern holds, after starting a binary search for when the pattern starts to differ from what is expected, we don't see the flag. Instead, we see that after a block with 32767 match instructions, the next block has 4 match instructions, then 5, then 6... and if we seek forward yet again to a block with 32767  matches, the next block has 5 match instructions, then 6, and so on.

So, the next pattern we hypothesize is a triangular pattern. The $j$-th _row of chunks_ starts with $j+3$ (zero indexed $j$) and then goes $j+4$ and onwards, so if we consider the first $z$ rows of chunks, the total bit length of all the rows is $\Sigma_{j=3}^{z+3}\Sigma_{i=3}^{32767}(2i+100)$. For $z=32760$ which should be the last chunk, which starts and ends with 32767 match instructions, [a calculator](https://www.wolframalpha.com/input?i=sum+j%3D3+to+32767+of+%28sum+i%3Dj+to+32767+of+%282i%2B100%29%29) tells us this is equal to 23506705809710, and if we seek to that bit length we see that the pattern repeats again with 3, 4, 5, and so on.

Now, we have a modulo, so we can perform binary search. The final equation is a cubic polynomial, and the modulo is large, so we need a closed form for the inverse function. Roughly, the steps to invert a bit offset into an index for row of chunks, chunk inside that row, and remainder into that chunk is as follows:

* Modulo by 23506705809710
* Find the reasonable root to the cubic equation, round down
* Plug root back into cubic equation to get remainder, which is the bit offset into the row of chunks
* Find the reasonable root to the quadratic equation starting at the index, round down
* Plug root back into the quadratic equation to get remainder, which is the bit offset into the chunk
* Calculate the correct chunk as a bit stream, index into the chunk, and now we have bytes!

After implementing this and conducting another binary search, we find that the offset is a reasonable distance into the file, so it is probably the flag. Then, like the previous challenge, we can brute force bit offsets or manually pick at the bits to offset it correctly for it to be inflated into the flag.

See my solve2.py for code. In `mount.py`, I used a `MAX_CHUNK` of 100 instead of 32767 for testing, because then I can actually create a complete file and unzip it to ensure I didn't mess up the DEFLATE stream. I use numpy for the root-finding and I index the rows and cols (the rows of chunks and the bytes within said chunk) a little differently than in this write-up, but it comes out to the same thing.

## feedback

I've heard feedback that this probably shouldn't have been a web chal, and I agree, sorry about that, only the starting parts were vaguely webby.

The original form of this chal was more webbish - it didn't include a gzipped _file_, the idea was to have a custom web server that used gzip as its transfer encoding, and then a range request for a massive range, from zero to an arbitrary byte, would process quickly with a gzip checksum that can be compared to the checksum for the same-sized range after the flag.

But the problem with that is, the gzip checksum happens _after_ the content, so that wouldn't actually work, the client would have to download all the bytes first. Hence the current form of the challenge, much less webtacular.

