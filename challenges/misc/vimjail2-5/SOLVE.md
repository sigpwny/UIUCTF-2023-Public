# Solution

- use expression register (ctrl-r =)
- use arrow keys and backspace to form subsequence of the given string ("excuse me...") into `execute(':q')`
  - it looks like very few people noticed this, but there are only 25 letters blocked (`q` is not blocked!)

## Unintended solves

A collection of unintended solves (in no particular order)

### Using expression register

The following all use the expression register (`<c-r>=`)

- `<c-f>execute(":e /flag.txt")`
  - if you press ctrl-f in expression register mode, you get to the command line window, which allows you to edit the expression register like a buffer
  - from there, you can type out the command directly
- using tab
- using tab to complete in expression register mode, you can keep pressing it until you get `execute(` and then type out the rest `":q")`
- some teams used the tab completion to get `execute(":e flag.txt")`, where each character is built up by completing until you get a function with that character, and deleting the rest
- `"<c-v><esc>:"`
  - in the expression register, types quote ctrl-v esc colon quote
  - this creates a string with 2 characters, the escape character and the colon
  - vim inserts this into the current buffer (this is what the expression register does), but the escape gets interpreted as the key to exit insert mode
  - the colon drops you into command mode, where you can exit vim or read the flag
- `eval(readfile('flag.txt')[0])`
  - we can't `readfile` directly into the current buffer, since `modifiable` is set to off
  - but what if we evaluate it instead?
  - know that the flag format is `uiuctf{...}`, this generates an error message along the lines of `E121: Undefined variable: inner_flag_value_...`, where `inner_flag_value_...` is the part of the flag inside the brackets
- `eval(readfile(glob('flag.t*t'))[0])`
  - although alphabetic keys are blocked in vimjail2, you can still type them with `<c-q>` or `<c-v>` followed by the key
  - for some reason, this doesn't work for the key `x`, which is needed to type `flag.txt`
  - one team worked around this by using the `glob` function and replacing the `x` with `*`
- one team used the big string in viminfo as intended but used it to call `setreg(1, "flag.txt")` and then `setreg(1, readfile("flag.txt"))`, using `<c-r>1` to get the flag
- user input
  - `eval(tolower(input("")))` then `EVAL(LIST2STR(BLOB2LIST(0Z6576616C286576616C28227265616466696C65285C22666C61672E7478745C222922295B305D29)))`
    - the `0Z...` syntax is a blob literal
    - this runs `eval(eval("readfile(\"flag.txt\")")[0])`
  - `eval(list2str(split(input("HI"))))` then `105 110 112 117 116 40 114 101 97 100 102 105 108 101 40 34 47 102 108 97 103 46 116 120 116 34 41 91 48 93 41`
    - the `list2str2` turns the numbers into characters
    - this runs `input(readfile("/flag.txt")[0])` to print the flag as an `input` prompt

### Other keys

These solves use different keys to exit insert mode

- `ctrl-printscr`
  - I was not able to test this because my keyboard didn't have a printscr key
  - the full solve is `ctrl-printscr` followed by `<cr><c-o>:e flag.txt`
  - to get around the fact that you can't type alphabetic characters in vimjail2, one solution is to use `<c-q>` or `<c-v>` as shown above, but if you only need one character, you can `<tab>` complete until you get a command that starts with that character and backspace to get just the character
