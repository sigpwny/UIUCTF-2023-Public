# Fast Calculator Solution

## Solution Summary

This challenge was largely inspired by 
[this post](https://simonbyrne.github.io/notes/fastmath/), describing the 
pitfalls of the `fast-math` compiler optimization. The main takeaway from the 
post is that by simply including the `-ffast-math` in your gcc command, your 
compiled code could be optimized with assumptions that deviate from IEEE 
floating point standards: specifically that `-0.0`, `inf`, and `nan` could 
never occur in the code, so any checks for those values get optimized out.

## Challenge

The only file provided for this challenge was [calc](./challenge/calc).

When we first run the provided `calc` binary, we get the following prompt:

```
Welcome to the fastest, most optimized calculator ever!
Example usage:
  Add:       1 + 2
  Subtract:  10 - 24
  Multiply:  34 * 8
  Divide:    20 / 3
  Modulo:    60 % 9
  Exponent:  2 ^ 12

If you enter the correct secret operation, I might decrypt the flag for you! ^-^

Enter your operation: 
```

If we enter in some operation, we'll notice that the result is always a 
floating point value:

```
Enter your operation: 1+2
Result: 3.000000
Enter your operation: 4/3
Result: 1.333333
```

At first glance, it seems like all we need to do is figure out the correct 
operation to enter and we can decrypt the flag! So let's load it into Ghidra 
and check it out.

Note: the reason Ghidra analysis takes much longer than usual is because the 
program was statically linked. This was a bit of an oversight on my part.

```c
// main() ...
puts("If you enter the correct secret operation, I might decrypt the flag for you! ^-^\n");
do {
  while( true ) {
    *(undefined8 *)((long)puVar8 + -0xb88) = 0x401e3a;
    printf("Enter your operation: ");
    while( true ) {
      *(undefined8 *)((long)puVar8 + -0xb88) = 0x401e87;
      iVar4 = __isoc99_scanf(" %lf %c %lf",&local_2350,&local_2369,&local_2348);
      if (iVar4 == 3) break;
      do {
        *(undefined8 *)((long)puVar8 + -0xb88) = 0x401e42;
        iVar4 = getchar();
      } while (iVar4 != 10);
      *(undefined8 *)((long)puVar8 + -0xb88) = 0x401e5b;
      printf("Enter your operation: ");
    }
    if ((((local_2369 == '+') || (local_2369 == '-')) || (local_2369 == '*')) ||
        (((local_2369 == '/' || (local_2369 == '%')) || (local_2369 == '^')))) break;
    *(undefined8 *)((long)puVar8 + -0xb88) = 0x401edd;
    puts("Invalid operation!");
  }
  local_2318 = (int)local_2369;
  local_2310 = local_2350;
  local_2308 = local_2348;
  *(undefined8 *)((long)puVar8 + -0xb90) = local_2348;
  *(undefined8 *)((long)puVar8 + -0xb98) = local_2310;
  *(ulong *)((long)puVar8 + -0xba0) = CONCAT44(uStack8980,local_2318);
  *(undefined8 *)((long)puVar8 + -0xba8) = 0x401f2d;
  calculate();
  local_2330 = __format;
  *(undefined8 *)((long)puVar8 + -0xb88) = 0x401f5d;
  printf(__format,"Result: %lf\n");
  if ((double)local_2330 == 8573.8567) { // Interesting check!
    *(undefined8 *)((long)puVar8 + -0xb88) = 0x401f88;
    puts("\nCorrect! Attempting to decrypt the flag...");
    // ...
  }
} while (true);
```

Above, we can see that there is a check if the result of `calculate()` is 
equal to `8573.8567`. So let's do a simple operation to pass that check:

```
Enter your operation: 8573.8567 + 0
Result: 8573.856700

Correct! Attempting to decrypt the flag...
I calculated 368 operations, tested each result in the gauntlet, and flipped 119 bits in the encrypted flag!
Here is your decrypted flag:

uiuctf{This is a fake flag. You are too fast!}

Enter your operation:
```

Oops, looks like it won't be that simple. We'll have to dig deeper into 
what happens during flag decryption, probably starting with this "gauntlet."

```c
undefined4 gauntlet(undefined8 param_1)
{
  char cVar1;
  
  cVar1 = isNegative(param_1);
  if (((cVar1 == '\0') && (cVar1 = isNotNumber(param_1), cVar1 == '\0')) &&
     (cVar1 = isInfinity(param_1), cVar1 == '\0')) {
    return 0;
  }
  return 1;
}
```

So it seems that `gauntlet()` returns 1 if the provided parameter is negative, 
is not a number, or is infinity, and 0 otherwise. Let's take a closer look at 
where `gauntlet()` is being called:

```c
  for (local_2364 = 0; iVar4 = local_2364, local_2364 < (int)local_235c;
      local_2364 = local_2364 + 1) {
    // ...
    calculate();
    *(undefined8 *)(puVar9 + lVar1 + -8) = 0x4020b1;
    cVar3 = gauntlet(extraout_XMM0_Qa);
    if (cVar3 != '\0') {
      local_2358 = local_2364;
      if (local_2364 < 0) {
        local_2358 = local_2364 + 7;
      }
      local_2358 = local_2358 >> 3;
      uVar6 = (uint)(local_2364 >> 0x1f) >> 0x1d;
      local_2354 = (local_2364 + uVar6 & 7) - uVar6;
      local_2320[local_2358] =
            local_2320[local_2358] ^ (byte)(1 << (7U - (char)local_2354 & 0x1f));
      local_2368 = local_2368 + 1;
    }
  }
```

This `gauntlet()` is clearly changing the state of some variables if it 
returns 0. We also see the `calculate()` function getting called before it, 
and the functions are called in a loop.

It may take a few more bits of interpreting the code but eventually you could 
come to one of the following conclusions.

### Conclusion 1

The original operation we input is only used once, and that is for the 
`8573.8567` check. There is no other means of input, so the program is 
just computing the same loop of operations every time, statically.

Digging deeper into the `gauntlet()` function, we see that `isNotNumber()` and 
`isInfinity()` are both completely broken and just return 0!

```c
bool isNegative(double param_1)
{
  return param_1 < 0.0;
}

undefined8 isNotNumber(void)
{
  return 0;
}

undefined8 isInfinity(void)
{
  return 0;
}
```

It is less obvious, but `isNegative()` is also broken - with IEEE, `-0.0` is a 
valid float. At this point you may suspect a compiler optimization 
"broke" the code, resulting in the fake flag.

### Conclusion 2

Interpreting the recurring hints and theme of "fast", simply `grep` the 
strings of the binary for "fast":

```
strings ./calc | grep "fast"
```

You'll find multiple references to "fast math" as well as the original 
compiler options!

```
GNU C17 11.3.0 -mtune=generic -march=x86-64 -O0 -ffast-math -fasynchronous-unwind-tables -fstack-protector-strong -fstack-clash-protection -fcf-protection
```

From here, you could look into `fast-math` and immediately see all the 
problems it can cause!

### Fixing `fast-math`

Once the trick has been figured out, there are a few ways you could complete 
the challenge.

1. Rewrite the entire program in another language which supports IEEE floating
point operations.

2. Manually patch the program to properly calculate the operations.

I'm a lazy challenge author, so I didn't do either of the above to test and 
just compiled a version without the `fast-math` flag.

3. Blackmail the challenge author into releasing the challenge source, then 
recompile the program without the `fast-math` flag.

As part of the challenge source, I've also included the Python script used to 
generate the operations which will allow the decryption process to print a 
different message based on whether the source was compiled with `fast-math` or 
not. Enjoy :)
