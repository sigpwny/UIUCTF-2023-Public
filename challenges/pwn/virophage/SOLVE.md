# Virophage

by YiFei Zhu

This challenge explores the bare minimum of a pwnable.

> This challenge is inspired by TSJ CTF 2022's
> ["virus" challenge](https://github.com/XxTSJxX/TSJ-CTF-2022/tree/main/Pwn/Virus).
>
> I thought a virus could be even tinier, but I there's a catch: are viruses
> alive or dead? What separates living organisms from lifeless objects? Can
> viruses [infect other viruses](https://en.wikipedia.org/wiki/Virophage)?
>
> **Note: This challenge has not been solved by the author.**
> [Have fun!](https://xkcd.com/356/)
>
> `$ socat file:$(tty),raw,echo=0 tcp:virophage.chal.uiuc.tf:1337`

## The Inspiration

I was sent the virus challenge from `TSJ CTF 2022` a long time back. The
challenge was to exploit this binary:
```
Disassembly of section .text:

0000000000401000 <.text>:
  401000:	54                   	push   %rsp
  401001:	5e                   	pop    %rsi
  401002:	80 f2 60             	xor    $0x60,%dl
  401005:	0f 05                	syscall
  401007:	c3                   	ret
```
... and that's it.

When I saw this challenge, I thought of two questions. If we want to make a
pwnable as tiny as possible, could we live:
* without any code, given that there are already code in the VDSO which will
always be mapped?
* without the read syscall, given that the argument, the environment, and the
auxiliary vector is all on the stack?

## The Terminology

I used the term "virophage". In biology, this is a virus that infects other
viruses. Here, it is a "virus" and a "phage". The "virus" is the tiniest ELF
with no segments, and the "phage" is the ELF entry point being patched into the
"virus". In other words, the "phage" infecting/modifying the "virus".

## The Making of

I coded this challenge, with the intended solution being a ROP within the VDSO,
using the stack as the initial stack at the program entry point. I disabled
linking to any libcs because I did not want libcs messing with argument or
environment arrays, or interpreting them in any way.

I also disabled ASLR since one only gets one attempt at setting the entry point
of the "virus", and ASLR would make it almost impossible that the entry point
just happens to be inside VDSO. This disabling is achieved using:

```C
if (_vp_sys_personality(ADDR_NO_RANDOMIZE) < 0)
        _vp_error(1, _vp_errno, "personality(ADDR_NO_RANDOMIZE)");
```

Initially, the "virus" was a 64 bit ELF. The difference between the deployed
version and the original 64 bit version is this:
```diff
--- 32-bit/virophage.c
+++ 64-bit/virophage.c
@@ -25,8 +25,6 @@

 static int _vp_errno;

-typedef unsigned int target_ulong;
-
 static inline
 long _vp_syscall(long n, ...)
 {
@@ -178,9 +176,9 @@ void _vp_error(int status, int errnum, const char *message)
                _vp_sys_exit(status);
 }

-static target_ulong virophage_request_phage(void)
+static unsigned long virophage_request_phage(void)
 {
-       target_ulong result = 0;
+       unsigned long result = 0;

        WRITE_STRING_LITERAL(STDOUT_FILENO, "Please enter a number in hex: ");

@@ -206,7 +204,7 @@ static target_ulong virophage_request_phage(void)
        }

        WRITE_STRING_LITERAL(STDOUT_FILENO, "You entered: 0x");
-       for (int shift = 28; shift >= 0; shift -= 4) {
+       for (int shift = 60; shift >= 0; shift -= 4) {
                unsigned char c = (result >> shift) & 0xf;

                c += c < 10 ? '0' : 'A' - 10;
@@ -219,24 +217,24 @@ static target_ulong virophage_request_phage(void)
 static void virophage_write_virus(const char *path)
 {
        /* load_elf_phdrs wants at least one segment, else it errors */
-       target_ulong phage = virophage_request_phage();
+       unsigned long phage = virophage_request_phage();

        struct {
-               Elf32_Ehdr ehdr;
-               Elf32_Phdr phdr;
+               Elf64_Ehdr ehdr;
+               Elf64_Phdr phdr;
        } data = {
                .ehdr = {
                        .e_ident = {
                                ELFMAG0, ELFMAG1, ELFMAG2, ELFMAG3,
-                               ELFCLASS32, ELFDATA2LSB, EV_CURRENT,
+                               ELFCLASS64, ELFDATA2LSB, EV_CURRENT,
                                ELFOSABI_SYSV
                        },
                        .e_type = ET_EXEC,
-                       .e_machine = EM_386,
+                       .e_machine = EM_X86_64,
                        .e_version = EV_CURRENT,
                        .e_entry = phage,
-                       .e_ehsize = sizeof(Elf32_Ehdr),
-                       .e_phentsize = sizeof(Elf32_Phdr),
+                       .e_ehsize = sizeof(Elf64_Ehdr),
+                       .e_phentsize = sizeof(Elf64_Phdr),
                        .e_phnum = 1,
                },
                .phdr = {
```

## The Roadblock

I'm not a god pwner. I don't know tools to do pwn, so when I need to ROP, I
find gadgets manually, and just debug them with gdb (I'm very good at gdb).
However, I knew this ROP, if possible, will take way longer for myself to solve
than I had time for (I also needed to manage UIUCTF infra and write other
challenges, and a few of which I didn't even manage to complete in the end).

I sent this challenge to a pwn person in UIUCTF team. They found a stack pivot
in VDSO:

```
0x7ffff7ffd785      5d             pop rbp
0x7ffff7ffd786      f8             clc
0x7ffff7ffd787      c9             leave
0x7ffff7ffd788      c3             ret
```

But the stack pivot was not immediately useful because top of stack is argc.
However, a stack pivot must be performed before a ret because the entire
argument vector points to the stack, which, at the time, was non-executable.
Unless we can either unalign the stack, or perform a stack pivot, or somehow
jump over the massive chunk of auxiliary vectors, performing a ret means
jumping to non-executable memory and will immediately fault.

Hearing this, I was like, let's maybe change up the gadgets a bit. What if
instead of 64 bits, it's 32 bits? There are fewer registers, so hopefully more
pops at end of functions. This resulted in the challenge that got released.
We did not end up with much more time to try very hard on this challenge.

## The Surprise

```
[11:16 PM] [BOT] Clippy:
Congratulations to team Project osu!lazer for the 1st solve on challenge Virophage!
```

**How did they solve it?**

The stack was RWX.

**WHAT?!**

## The Realization

Immediately after knowing the stack was RWX, I tested myself. Indeed, the stack
is RWX. And indeed, the stack of the 64 bit virophage is RW and not executable.

How come?

My immediate thought was the lack of a `PT_GNU_STACK`, which normally declares
whether the program wants executable stack. I search in the kernel, nothing
other than the kernel could have performed the mapping of the stack so early.

The first hint comes in [load_elf_binary](https://elixir.bootlin.com/linux/v6.3.8/source/fs/binfmt_elf.c#L932):
```
switch (elf_ppnt->p_type) {
case PT_GNU_STACK:
        if (elf_ppnt->p_flags & PF_X)
                executable_stack = EXSTACK_ENABLE_X;
        else
                executable_stack = EXSTACK_DISABLE_X;
        break;
```

So what is the default of this `executable_stack` variable?

```
int executable_stack = EXSTACK_DEFAULT;
```

So what happens when it is left at default?

We see an [x86-specific code](https://elixir.bootlin.com/linux/v6.3.8/source/arch/x86/include/asm/elf.h#L289):
```
/*
 * An executable for which elf_read_implies_exec() returns TRUE will
 * have the READ_IMPLIES_EXEC personality flag set automatically.
 *
 * The decision process for determining the results are:
 *
 *                 CPU: | lacks NX*  | has NX, ia32     | has NX, x86_64 |
 * ELF:                 |            |                  |                |
 * ---------------------|------------|------------------|----------------|
 * missing PT_GNU_STACK | exec-all   | exec-all         | exec-none      |
 * PT_GNU_STACK == RWX  | exec-stack | exec-stack       | exec-stack     |
 * PT_GNU_STACK == RW   | exec-none  | exec-none        | exec-none      |
 *
 *  exec-all  : all PROT_READ user mappings are executable, except when
 *              backed by files on a noexec-filesystem.
 *  exec-none : only PROT_EXEC user mappings are executable.
 *  exec-stack: only the stack and PROT_EXEC user mappings are executable.
 *
 *  *this column has no architectural effect: NX markings are ignored by
 *   hardware, but may have behavioral effects when "wants X" collides with
 *   "cannot be X" constraints in memory permission flags, as in
 *   https://lkml.kernel.org/r/20190418055759.GA3155@mellanox.com
 *
 */
#define elf_read_implies_exec(ex, executable_stack)	\
        (mmap_is_ia32() && executable_stack == EXSTACK_DEFAULT)
```

TIL.

## The Exploit?

The arguments and environments may have unprintables and whitespaces; no
sanitization is done. With RWX, without ASLR, and without sanitization, the
exploitation is trivial and is left as an exercise to the reader.
