// SPDX-License-Identifier: Apache-2.0
/*
 * Copyright 2023 Google LLC.
 */

#define _GNU_SOURCE

#include <elf.h>
#include <linux/fcntl.h>
#include <linux/mount.h>
#include <linux/personality.h>
#include <linux/sched.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>

#define STDIN_FILENO 0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2
#define noreturn __attribute__((noreturn))

static int _vp_errno;

typedef unsigned int target_ulong;

static inline
long _vp_syscall(long n, ...)
{
	long a, b, c, d, e, f;
	long ret;
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

	if (ret < 0)
		_vp_errno = -ret;
	return ret;
}

static inline
bool IS_ERR(const void *ptr)
{
	return (long)ptr < 0;
}

static inline noreturn
void _vp_sys_exit(int status)
{
	_vp_syscall(SYS_exit_group, status);
	for (;;)
		__asm__ __volatile__ ("ud2");
}

static inline
int _vp_sys_open(const char *pathname, int flags, mode_t mode)
{
	return _vp_syscall(SYS_open, pathname, flags, mode);
}
static inline
int _vp_sys_close(int fd)
{
	return _vp_syscall(SYS_close, fd);
}
static inline
ssize_t _vp_sys_read(int fd, void *buf, size_t count)
{
	return _vp_syscall(SYS_read, fd, buf, count);
}
static inline
ssize_t _vp_sys_write(int fd, const void *buf, size_t count)
{
	return _vp_syscall(SYS_write, fd, buf, count);
}
static inline
int _vp_sys_unshare(int flags)
{
	return _vp_syscall(SYS_unshare, flags);
}
static inline
int _vp_sys_mount(const char *source, const char *target,
		  const char *filesystemtype, unsigned long mountflags,
		  const void *data)
{
	return _vp_syscall(SYS_mount, source, target, filesystemtype,
			   mountflags, data);
}
static inline
int _vp_sys_setuid(uid_t uid)
{
	return _vp_syscall(SYS_setuid, uid);
}
static inline
int _vp_sys_personality(unsigned long persona)
{
	return _vp_syscall(SYS_personality, persona);
}
static inline
int _vp_sys_execve(const char *pathname, char *const argv[],
		   char *const envp[])
{
	return _vp_syscall(SYS_execve, pathname, argv, envp);
}

static inline
size_t _vp_strlen(const char *s)
{
	size_t len = 0;
	while (s[len])
		len++;
	return len;
}

static
char *_vp_itoa_10(int n, char *buffer_end)
{
	char *ptr = buffer_end;
	bool is_neg = n < 0;

	if (is_neg)
		n = -n;

	*ptr = '\0';
	if (!n)
		*(--ptr) = '0';
	while (n) {
		*(--ptr) = '0' + n % 10;
		n /= 10;
	}

	if (is_neg)
		*(--ptr) = '-';

	return ptr;
}

#define WRITE_STRING_LITERAL(fd, message) do { \
	_vp_sys_write(fd, message, sizeof(message) - 1); \
} while (0)

static
void _vp_error(int status, int errnum, const char *message)
{
	_vp_sys_write(STDERR_FILENO, message, _vp_strlen(message));

	if (errnum) {
		/* ULLONG_MAX is only 20 chars in DEC */
		#define MAXNUMLEN 30
		char buf[MAXNUMLEN];
		char *error_str = _vp_itoa_10(errnum, &buf[MAXNUMLEN-1]);

		WRITE_STRING_LITERAL(STDERR_FILENO, ": errno ");
		_vp_sys_write(STDERR_FILENO, error_str, _vp_strlen(error_str));
	}

	WRITE_STRING_LITERAL(STDERR_FILENO, "\n");
	if (status)
		_vp_sys_exit(status);
}

static target_ulong virophage_request_phage(void)
{
	target_ulong result = 0;

	WRITE_STRING_LITERAL(STDOUT_FILENO, "Please enter a number in hex: ");

	while (true) {
		char c;
		int r;

		r = _vp_sys_read(STDIN_FILENO, &c, 1);
		if (!r)
			break;
		if (r < 0)
			_vp_error(1, _vp_errno, "read(stdin)");

		if (c == '\n')
			break;
		else if (c >= '0' && c <= '9')
			result = (result << 4) | (c - '0');
		else if (c >= 'a' && c <= 'f')
			result = (result << 4) | (c - 'a' + 10);
		else if (c >= 'A' && c <= 'F')
			result = (result << 4) | (c - 'A' + 10);
		/* else junk, ignore */
	}

	WRITE_STRING_LITERAL(STDOUT_FILENO, "You entered: 0x");
	for (int shift = 28; shift >= 0; shift -= 4) {
		unsigned char c = (result >> shift) & 0xf;

		c += c < 10 ? '0' : 'A' - 10;
		_vp_sys_write(STDOUT_FILENO, &c, 1);
	}
	WRITE_STRING_LITERAL(STDOUT_FILENO, "\n");

	return result;
}
static void virophage_write_virus(const char *path)
{
	/* load_elf_phdrs wants at least one segment, else it errors */
	target_ulong phage = virophage_request_phage();

	struct {
		Elf32_Ehdr ehdr;
		Elf32_Phdr phdr;
	} data = {
		.ehdr = {
			.e_ident = {
				ELFMAG0, ELFMAG1, ELFMAG2, ELFMAG3,
				ELFCLASS32, ELFDATA2LSB, EV_CURRENT,
				ELFOSABI_SYSV
			},
			.e_type = ET_EXEC,
			.e_machine = EM_386,
			.e_version = EV_CURRENT,
			.e_entry = phage,
			.e_ehsize = sizeof(Elf32_Ehdr),
			.e_phentsize = sizeof(Elf32_Phdr),
			.e_phnum = 1,
		},
		.phdr = {
			.p_type = PT_NULL,
		},
	};
	int fd, r;

	data.ehdr.e_phoff = (void *)&data.phdr - (void *)&data;

	fd = _vp_sys_open(path, O_WRONLY | O_CREAT | O_EXCL, 0500);
	if (fd < 0)
		_vp_error(1, _vp_errno, "open(virus)");

	r = _vp_sys_write(fd, &data, sizeof(data));
	if (r < 0)
		_vp_error(1, _vp_errno, "write(virus)");
	if (r != sizeof(data))
		_vp_error(1, 0, "write(virus): bad size written");

	_vp_sys_close(fd);
}

static int virophage_main(int argc, char **argv, char **envp)
{
	/* Do stuff in a private tmpfs so there's no way for adversary to
	   mess with the files we create */
	if (_vp_sys_unshare(CLONE_NEWNS) < 0)
		_vp_error(1, _vp_errno, "unshare(CLONE_NEWNS)");
	if (_vp_sys_mount("none", "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0)
		_vp_error(1, _vp_errno, "mount(/, MS_REC | MS_PRIVATE)");
	if (_vp_sys_mount("tmpfs", "/tmp", "tmpfs", MS_NOSUID | MS_NODEV, NULL))
		_vp_error(1, _vp_errno, "mount(/tmp)");

	virophage_write_virus("/tmp/virus");

	if (_vp_sys_setuid(0) < 0)
		_vp_error(1, _vp_errno, "setuid(0)");
	if (_vp_sys_personality(ADDR_NO_RANDOMIZE) < 0)
		_vp_error(1, _vp_errno, "personality(ADDR_NO_RANDOMIZE)");

	WRITE_STRING_LITERAL(STDOUT_FILENO, "execve...\n");
	_vp_sys_execve("/tmp/virus", argv, envp);
	_vp_error(1, _vp_errno, "execve(virus)");

	return 1;
}

void virophage_start_main(void **stack)
{
	void *argv, *envp;
	unsigned int i;
	int argc;

	argc = (uintptr_t)*stack++;

	argv = (void *)stack;
	for (i = 0; i < argc; i++)
		stack++;
	stack++;

	envp = stack;

	_vp_sys_exit(virophage_main(argc, argv, envp));
}

__asm__ (
	".globl _start\n"
	".section .text,\"ax\",@progbits\n"
	".type _start, @function\n"
	"_start:\n"
	"	mov %rsp, %rdi\n"
	"	call virophage_start_main\n"
	"	hlt\n"
);
