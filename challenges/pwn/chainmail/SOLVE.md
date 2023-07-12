# Chainmail

This challenge consisted of a buffer overflow vulnerability related to `gets` in C and accounting for a stack alignment complication. If you are completely unfamiliar with how memory layout looks for C programs or what the "stack" is, or just need a quick refrefresher before going into this writeup, this might be of use: [https://www.geeksforgeeks.org/memory-layout-of-c-program/](https://www.geeksforgeeks.org/memory-layout-of-c-program/). 

## Analyzing the Code

We are given a compiled C binary and the source code for the challenge. In the source code, we can see two functions, a `main` function that drives the program:

```c
int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    char name[64];
    printf("Hello, welcome to the chain email generator! Please give the name of a recipient: ");
    gets(name);
    printf("Okay, here's your newly generated chainmail message!\n\nHello %s,\nHave you heard the news??? Send this email to 10 friends or else you'll have bad luck!\n\nYour friend,\nJim\n", name);
    return 0;
}
```

And a `give_flag` function that is never called in the program:

```c
void give_flag() {
    FILE *f = fopen("/flag.txt", "r");
    if (f != NULL) {
        char c;
        while ((c = fgetc(f)) != EOF) {
            putchar(c);
        }
    }
    else {
        printf("Flag not found!\n");
    }
    fclose(f);
}
```

The main code defines a 64 character buffer, then the `gets` function is utilized to take user input for a name. This is where the vulnerability lies. The `gets` function takes input up until a newline with no other stopping indications, so if that newline doesn't come before the user fills up the buffer, nothing is stopping the user from changing values on the stack. We are going to use this quirk to change the next place the program goes after it returns from the `gets` function by overwriting the value used to tell the program where to return after a function is done running.

# Payload Crafting

There's a few common Linux commands you can use to find the location of the `get_flag` function in the compiled program, including but not limited to `objdump`, `nm`, and `readelf`. Feel free to pick your favorite, I personally went with `nm` for this writeup:

```bash
$ nm chal | grep give_flag
0000000000401216 T give_flag
```

Okay, so now we know `give_flag` is at location 0x0000000000401216. We can replace the current location the program should return to (currently the location of the `main` function) with this new location we found instead. When we craft our input we can fill the 64 character buffer with nonsense, plus 8 more characters to overwrite the base pointer, which is normally one of the values used to keep track of where the program is at. Then, we can insert our `give_flag` location value. We should be done, right? 

Almost, I promise. 

If you were to craft a payload with only this in mind, you probably would run into a segmentation fault still. This is because when we modify the stack, we accidentally unaligned it in the process! The stack is meant to be aligned to 16 bytes, so when that doesn't happen, the program might behave unexpectedly. There's a few ways you can go about solving this, one being to modify the location we found to an aligned value instead, and another is to include a `ret` instruction in your payload before the location of `get_flag`, which you can find the location of in a similar way to how you found the last location we looked for. Either should get you the flag!

# Wrapup

A working payload should be avaliable in the healthcheck folder of this challenge. It uses the Python library pwntools, which if you're new to pwn and plan to continue down this path I would highly recommend. If you have questions about how that payload works or anything in this writeup, feel free to reach out! I hope you had fun solving this challenge and that I introduced at least one person to binary exploitation in a positive way :D