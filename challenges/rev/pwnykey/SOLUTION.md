1. pwnykey is a devicescript bytecode rev challenge. it consists of:
  1. a webserver for users to interface with (submit a key) and invoke the devicescript program
  2. a devicescript bytecode file, which retrieves data (the key) from the webserver and returns success or false
2. So, the goal is to find a valid key that passes the checks in the devicescript bytecode!
3. The first thing you can try is running the official devicescript disassembler to disassemble it.. but you'll notice that it mostly fails:
```
// img size 12416
// 14 globals

proc main_F0(): @1120
  locals: loc0,loc1,loc2
   0:     CALL prototype_F1{F1}() // 270102
???oops: Op-decode: can't find jump target 10; 0c // 0df90007
   7:     RETURN undefined // 2e0c
   9:     JMP 39 // 0d1e
???oops: Op-decode: stack underflow; 4c // 4c
???oops: Op-decode: stack underflow; 250003 // 250003
???oops: Op-decode: can't find jump target 22; 0c // 0df90007
  19:     RETURN undefined // 2e0c
???oops: Op-decode: can't find jump target 51; 0c // 0d1e
  23:     CALL ???oops op126(62, ret_val()) // 7ece2c04
???oops: Op-decode: can't find jump target 34; 0c // 0df90007
  31:     RETURN undefined // 2e0c
???oops: Op-decode: can't find jump target 72; 0c // 0d27
???oops: Op-decode: stack underflow; 02 // 02
???oops: Op-decode: stack underflow; 253303 // 253303
???oops: Op-decode: can't find jump target 46; 0c // 0df90007
  43:     RETURN undefined // 2e0c
  45:     JMP 89 // 0d2c
```
4. hm, weird... but it clearly runs fine, so what is going on?
5. there are a few ways to proceed here, but one way is to start disassembling the bytecode "by hand", following the spec.
6. if you do so, you'll notice that it fails on the first jmp instruction, but the jmp appears to be perfectly valid? also, this instruction sequence is appearing throughout the bytecode
  1. JMP +7, UNDEFINED, RETURN, JMP
7. it turns out that the disassembler simply performs a linear sweep disassemble. it does not follow jmp targets, so it is failing on undersanding this last (fake) jmp instruction! the execution follows the jmp+7, and these "undefined, return, jmp" bytes are not real instructions.
8. this is a fairly common obfuscation technique: e.g. https://github.com/defuse/gas-obfuscation
9. so, to get a proper disassembly, we can.... 1) patch/rewrite the disassembler to either follow jmp targets 2) patch the disassembler to ignore this recurring byte sequence 3) patch the bytecode itself and NOP out the "bad instruction" sequence
10. from here, we get a disassembly, and it becomes a more standard reversing chall: 
  1. check 1: check if first group of 5 chars equals a static int array
  2. check 2: check if sum of numbers in block 2 and block 3 = 134, and the product = 12534912000
  3. check 3: some prng run with initial state in block 4 - checks that the output after 420 iterations equals a static int array. we can brute-force this

now, you can put together a valid pwnykey :)
