/* I'm adding CFIs because for some reason without it gcc generates empty
  .eh_frame, which then causes an empty segment and zapps-crt0.c does't
  handle that */
.globl _start
.section .text,"ax",@progbits
.type _start, @function
_start:
.cfi_startproc
    xor %rdi,%rdi
    mov $105,%al
    syscall
    xor %rsi,%rsi
    push %rsi
    mov $0x6873612f2f2f2f2f,%rsi
    push %rsi
    push %rsp
    pop %rdi
    xor %rsi,%rsi
    push %rsi
    push %rdi
    push %rsp
    pop %rsi
    xor %rdx,%rdx
    push %rdx
    mov $0x68732f2f6e69622f,%rdi
    push %rdi
    push %rsp
    pop %rdi
    mov $59,%al
    cdq
    syscall
.cfi_endproc
