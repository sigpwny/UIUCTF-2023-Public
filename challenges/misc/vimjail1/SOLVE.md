# Solution

**see vimjail2-5/SOLVE.md for unintended solves**

- can run functions using expression register (press ctrl-r, then equal sign (`=`) in insert mode)
- first, call `setfperm('/flag.txt', 'r--r--r--')` so that we can read the flag file
- finally, call `execute(':e /flag.txt')` to read it
- ignore the "Cannot make changes" warnings (they're only there to annoy you!)

