// SPDX-License-Identifier: MIT OR Apache-2.0
/*
 * Copyright 2022-2023 Google LLC.
 */

#include <elf.h>
#include <fcntl.h>
#include <limits.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>

#define ZAPPS_DEBUG 0

#define PT_ZAPPS_INTERP 0xa26d1ecc

#define STDERR_FILENO 2
#define noreturn __attribute__((noreturn))
#define __section_zapps __attribute__((section(".text.zapps")))

#define PAGE_SIZE 4096
#define PAGE_OFF(x) ((x)&(PAGE_SIZE-1))
#define PAGE_DOWN(x) ((x)&-PAGE_SIZE)
#define PAGE_UP(x) PAGE_DOWN((x) + PAGE_SIZE - 1)

extern void _start(void);

static inline __section_zapps
long _zapps_syscall(long n, ...)
{
    long a, b, c, d, e, f;
    unsigned long ret;
    va_list ap;

    va_start(ap, n);
    a = va_arg(ap, long);
    b = va_arg(ap, long);
    c = va_arg(ap, long);
    d = va_arg(ap, long);
    e = va_arg(ap, long);
    f = va_arg(ap, long);
    va_end(ap);

    register long r10 __asm__("r10") = d;
    register long r8 __asm__("r8") = e;
    register long r9 __asm__("r9") = f;
    __asm__ __volatile__ (
        "syscall" :
        "=a"(ret) :
        "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8), "r"(r9) :
        "rcx", "r11", "memory"
    );
    return ret;
}
static inline __section_zapps
bool IS_ERR(const void *ptr)
{
	return (long)ptr < 0;
}

static inline noreturn __section_zapps
void _zapps_sys_exit(int status)
{
    _zapps_syscall(SYS_exit_group, status);
    for (;;)
        __asm__ __volatile__ ("ud2");
}

static inline __section_zapps
int _zapps_sys_open(const char *pathname, int flags)
{
    return _zapps_syscall(SYS_open, pathname, flags);
}
static inline __section_zapps
int _zapps_sys_close(int fd)
{
    return _zapps_syscall(SYS_close, fd);
}
static inline __section_zapps
ssize_t _zapps_sys_read(int fd, void *buf, size_t count)
{
    return _zapps_syscall(SYS_read, fd, buf, count);
}
static inline __section_zapps
ssize_t _zapps_sys_write(int fd, const void *buf, size_t count)
{
    return _zapps_syscall(SYS_write, fd, buf, count);
}
static inline __section_zapps
ssize_t _zapps_sys_pwrite64(int fd, const void *buf, size_t count, off_t offset)
{
    return _zapps_syscall(SYS_pwrite64, fd, buf, count, offset);
}
static inline __section_zapps
off_t _zapps_sys_lseek(int fd, off_t offset, int whence)
{
    return _zapps_syscall(SYS_lseek, fd, offset, whence);
}
static inline __section_zapps
ssize_t _zapps_sys_readlink(
    const char *restrict pathname, char *restrict buf, size_t bufsiz)
{
    return _zapps_syscall(SYS_readlink, pathname, buf, bufsiz);
}
static inline __section_zapps
void *_zapps_sys_mmap(
    void *addr, size_t length, int prot, int flags, int fd, off_t offset)
{
    return (void *)_zapps_syscall(SYS_mmap, addr, length, prot, flags, fd, offset);
}
static inline __section_zapps
int _zapps_sys_mprotect(void *addr, size_t len, int prot)
{
    return _zapps_syscall(SYS_mprotect, addr, len, prot);
}

static inline __section_zapps
size_t _zapps_strlen(const char *s)
{
    size_t len = 0;
    while (s[len])
        len++;
    return len;
}
static inline __section_zapps
char *_zapps_strncat(char *dest, const char *src, size_t n)
{
    size_t dest_len = _zapps_strlen(dest);
    size_t i;

    for (i = 0 ; i < n && src[i] != '\0' ; i++)
        dest[dest_len + i] = src[i];
    dest[dest_len + i] = '\0';

    return dest;
}
static inline __section_zapps
char *_zapps_strrchr(const char *s, char c)
{
    const char *end = s + _zapps_strlen(s);
    while (end >= s) {
        if (*end == c)
            return (char *)end;
        end--;
    }
    return NULL;
}

static inline __section_zapps
void *_zapps_memset(void *s, int c, size_t n)
{
    unsigned char *p = s;
    unsigned char *end = s + n;
    while (p < end)
        *p++ = c;

    return s;
}

static noreturn __section_zapps
void _zapps_die(const char *message)
{
#if ZAPPS_DEBUG
    _zapps_sys_write(STDERR_FILENO, message, _zapps_strlen(message));
#else
    char shortmsg[] = "Zapps: Failed\n";
    _zapps_sys_write(STDERR_FILENO, shortmsg, sizeof(shortmsg) - 1);
#endif

    _zapps_sys_exit(1);
}

static __section_zapps
unsigned long *_zapps_getauxval_ptr(Elf64_auxv_t *auxv, unsigned long type)
{
    for (; auxv->a_type; auxv++)
        if (auxv->a_type == type)
            return &auxv->a_un.a_val;

    _zapps_die("Zapps: Fatal: missing one or more auxiliary vector values\n");
}

__section_zapps
void *_zapps_main(void **stack)
{
    char ld_rel[] = "/ld-linux-x86-64.so.2";
    Elf64_Phdr *self_phdr, *self_phdr_end;
    Elf64_Word p_type_interp = PT_INTERP;
    uintptr_t page_filesz, page_memsz;
    ssize_t exe_path_len;
    char ld[PATH_MAX+1];
    size_t max_map = 0;
    void *ld_base_addr;
    unsigned long argc;
    Elf64_auxv_t *auxv;
    Elf64_Ehdr ld_ehdr;
    Elf64_Phdr ld_phdr;
    int ld_fd, mem_fd;
    unsigned int i;
    void *ptr;
    int prot;

    argc = (uintptr_t)*stack++;
    /* argv */
    for (i = 0; i < argc; i++)
        stack++;
    stack++;

    /* envp */
    while (*stack++);

    auxv = (void *)stack;

    exe_path_len = _zapps_sys_readlink((char []){"/proc/self/exe"}, ld, PATH_MAX);
    if (exe_path_len < 0 || exe_path_len >= PATH_MAX)
        _zapps_die("Zapps: Fatal: failed to readlink /proc/self/exe\n");

    ld[exe_path_len] = '\0';
    *_zapps_strrchr(ld, '/') = '\0';
    _zapps_strncat(ld, ld_rel, sizeof(ld) - 1);

    ld_fd = _zapps_sys_open(ld, O_RDONLY | O_CLOEXEC);
    if (ld_fd < 0)
        _zapps_die("Zapps: Fatal: failed to open ld.so\n");

    if (_zapps_sys_read(ld_fd, &ld_ehdr, sizeof(ld_ehdr)) != sizeof(ld_ehdr))
        _zapps_die("Zapps: Fatal: failed to read EHDR from ld.so\n");

    if (_zapps_sys_lseek(ld_fd, ld_ehdr.e_phoff, SEEK_SET) != ld_ehdr.e_phoff)
        _zapps_die("Zapps: Fatal: failed to seek to PHDR in ld.so\n");
    for (i = 0; i < ld_ehdr.e_phnum; i++) {
        if (_zapps_sys_read(ld_fd, &ld_phdr, sizeof(ld_phdr)) != sizeof(ld_phdr))
            _zapps_die("Zapps: Fatal: failed to read PHDR from ld.so\n");

        if (ld_phdr.p_type != PT_LOAD)
            continue;

        if (max_map < ld_phdr.p_vaddr + ld_phdr.p_memsz)
            max_map = ld_phdr.p_vaddr + ld_phdr.p_memsz;
    }

    ld_base_addr = _zapps_sys_mmap(NULL, max_map, PROT_NONE,
                                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (IS_ERR(ld_base_addr))
        _zapps_die("Zapps: Fatal: failed to reserve memory for ld.so\n");

    if (_zapps_sys_lseek(ld_fd, ld_ehdr.e_phoff, SEEK_SET) != ld_ehdr.e_phoff)
        _zapps_die("Zapps: Fatal: failed to seek to PHDR in ld.so\n");
    for (i = 0; i < ld_ehdr.e_phnum; i++) {
        if (_zapps_sys_read(ld_fd, &ld_phdr, sizeof(ld_phdr)) != sizeof(ld_phdr))
            _zapps_die("Zapps: Fatal: failed to read PHDR from ld.so\n");

        if (ld_phdr.p_type != PT_LOAD)
            continue;

        prot = (ld_phdr.p_flags & PF_R ? PROT_READ : 0) |
           (ld_phdr.p_flags & PF_W ? PROT_WRITE : 0) |
           (ld_phdr.p_flags & PF_X ? PROT_EXEC : 0);

        if (IS_ERR(_zapps_sys_mmap(
            (void *)PAGE_DOWN((uintptr_t)ld_base_addr + ld_phdr.p_vaddr),
            ld_phdr.p_filesz + PAGE_OFF(ld_phdr.p_vaddr),
            prot, MAP_PRIVATE | MAP_FIXED, ld_fd,
            ld_phdr.p_offset - PAGE_OFF(ld_phdr.p_vaddr))
        ))
            _zapps_die("Zapps: Fatal: failed to map ld.so\n");

        if (ld_phdr.p_filesz >= ld_phdr.p_memsz)
            continue;

        /* BSS stage 1: clear memory after filesz */
        ptr = ld_base_addr + ld_phdr.p_vaddr + ld_phdr.p_filesz;
        _zapps_memset(ptr, 0, PAGE_UP((uintptr_t)ptr) - (uintptr_t)ptr);

        page_filesz = PAGE_UP((uintptr_t)ptr);
        page_memsz = PAGE_UP((uintptr_t)ld_base_addr + ld_phdr.p_vaddr +
                             ld_phdr.p_memsz);
        if (page_filesz >= page_memsz)
            continue;

        /* BSS stage 2: map anon pages after last filesz page */
        if (IS_ERR(_zapps_sys_mmap(
            (void *)page_filesz, page_memsz - page_filesz,
            prot, MAP_PRIVATE | MAP_FIXED | MAP_ANONYMOUS, -1, 0)
        ))
            _zapps_die("Zapps: Fatal: failed to map BSS in ld.so\n");
    }

    _zapps_sys_close(ld_fd);

    *_zapps_getauxval_ptr(auxv, AT_BASE) = (uintptr_t)ld_base_addr;
    *_zapps_getauxval_ptr(auxv, AT_ENTRY) = (uintptr_t)&_start;

    /* Patch our own PHDR for so PT_ZAPPS_INTERP is back to PT_INTERP.
       Without this glibc ld.so complains:
       Inconsistency detected by ld.so: rtld.c: 1291: rtld_setup_main_map:
       Assertion `GL(dl_rtld_map).l_libname' failed! */
    self_phdr = (void *)*_zapps_getauxval_ptr(auxv, AT_PHDR);
    self_phdr_end = self_phdr + *_zapps_getauxval_ptr(auxv, AT_PHNUM);

    mem_fd = _zapps_sys_open((char []){"/proc/self/mem"}, O_RDWR | O_CLOEXEC);
    if (mem_fd < 0)
        _zapps_die("Zapps: Fatal: failed to open /proc/self/mem\n");

    for (; self_phdr < self_phdr_end; self_phdr++) {
        if (self_phdr->p_type != PT_ZAPPS_INTERP)
            continue;

        _zapps_sys_pwrite64(mem_fd, &p_type_interp, sizeof(p_type_interp), (uintptr_t)&self_phdr->p_type);
    }

    _zapps_sys_close(mem_fd);

    return ld_base_addr + ld_ehdr.e_entry;
}

__asm__ (
    ".globl _zapps_start\n"
    ".section .text.zapps,\"ax\",@progbits\n"
    ".type _zapps_start, @function\n"
    "_zapps_start:\n"
    "    mov %rsp, %rdi\n"
    "    call _zapps_main\n"
    "\n"
    "/* clean registers in case some libc might assume 0 initialized */\n"
    "    xor %ebx, %ebx\n"
    "    xor %ecx, %ecx\n"
    "    xor %edx, %edx\n"
    "    xor %ebp, %ebp\n"
    "    xor %ebp, %ebp\n"
    "    xor %esi, %esi\n"
    "    xor %edi, %edi\n"
    "    xor %r8, %r8\n"
    "    xor %r9, %r9\n"
    "    xor %r10, %r10\n"
    "    xor %r11, %r11\n"
    "    xor %r12, %r12\n"
    "    xor %r13, %r13\n"
    "    xor %r14, %r14\n"
    "    xor %r15, %r15\n"
    "\n"
    "/* jmp into ld.so entry point */\n"
    "    cld\n"
    "    /* jmp *%rax */\n"
    "    push %rax\n"
    "    xor %eax, %eax\n"
    "    ret\n"
);
