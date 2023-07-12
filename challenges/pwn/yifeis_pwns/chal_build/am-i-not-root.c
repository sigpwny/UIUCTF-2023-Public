// SPDX-License-Identifier: Apache-2.0
/*
 * Copyright 2022-2023 Google LLC.
 */

#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <linux/mount.h>
#include <linux/securebits.h>
#include <sched.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef error
__attribute__((weak))
void error(int status, int errnum, const char *format, ...)
{
	va_list ap;

	fprintf(stderr, "%s: ", program_invocation_name);
	va_start(ap, format);
	vfprintf(stderr, format, ap);
	va_end(ap);
	if (errnum) {
		errno = errnum;
		fprintf(stderr, ": %m");
	}
	fprintf(stderr, "\n");

	if (status)
		exit(status);
}
#endif

static void wait_pid_terminate(pid_t pid)
{
	while (true) {
		int wstatus;
		pid_t w = waitpid(pid, &wstatus, WUNTRACED | WCONTINUED);

		if (w < 0) {
			if (errno == ERESTART || errno == EINTR)
				continue;
			error(1, errno, "waitpid");
		}

		if (WIFEXITED(wstatus) || WIFSIGNALED(wstatus))
		 	break;
	}
}

int main(int argc, char *argv[])
{
	int procfs_fd, sysfs_fd;
	pid_t child_pid;

	if (mount("", "/", NULL, MS_REC|MS_PRIVATE, NULL))
		error(1, errno, "mount");
	if (mount("", "/proc", NULL, MS_REMOUNT|MS_NOSUID|MS_NODEV|MS_NOEXEC, NULL))
		error(1, errno, "mount");

	// Mount tables changed here are locked by the child userns
	if (unshare(CLONE_NEWNS))
		error(1, errno, "unshare");

	// We dont want the jail to see the global /proc and /sys, so we could
	// either unmount it or overmount it. We cannot unmunt after
	// CLONE_NEWUSER because the mount becomes locked, and doing an
	// overmount after CLONE_NEWUSER is moot because that's reversible.
	// We'd do it before. However, doing either causes what's known as
	// "overmount protection". See explanation at:
	// https://bugs.chromium.org/p/chromium/issues/detail?id=1087937#c14
	// The relevant code is mount_too_revealing in fs/namespace.c
	// This will make it impossible to mount a new namespaced sysfs / procfs.
	// So instead of doing that, we do a weird dance here where we save
	// an fd for this mount. and use that to calm the kernel down.
	procfs_fd = syscall(SYS_open_tree, AT_FDCWD, "/proc", OPEN_TREE_CLONE|OPEN_TREE_CLOEXEC);
	if (procfs_fd < 0)
		error(1, errno, "open_tree");
	if (umount2("/proc", MNT_DETACH))
		error(1, errno, "umount2");

	sysfs_fd = syscall(SYS_open_tree, AT_FDCWD, "/sys", OPEN_TREE_CLONE|OPEN_TREE_CLOEXEC);
	if (sysfs_fd < 0)
		error(1, errno, "open_tree");
	if (umount2("/sys", MNT_DETACH))
		error(1, errno, "umount2");

	if (umount2("/mnt", MNT_DETACH))
		error(1, errno, "umount2");

	if (unshare(CLONE_NEWNS|CLONE_NEWUSER|CLONE_NEWPID|CLONE_NEWNET))
		error(1, errno, "unshare");

	child_pid = fork();
	if (child_pid < 0)
		error(1, errno, "unshare");
	if (child_pid) {
		wait_pid_terminate(child_pid);
		return 0;
	}

	if (syscall(SYS_move_mount, procfs_fd, "", AT_FDCWD, "/mnt", MOVE_MOUNT_F_EMPTY_PATH))
		error(1, errno, "move_mount");
	if (mount("proc", "/proc", "proc", MS_NOSUID|MS_NODEV|MS_NOEXEC, NULL))
		error(1, errno, "mount");
	if (umount2("/mnt", MNT_DETACH))
		error(1, errno, "umount2");

	if (syscall(SYS_move_mount, sysfs_fd, "", AT_FDCWD, "/mnt", MOVE_MOUNT_F_EMPTY_PATH))
		error(1, errno, "move_mount");
	if (mount("sysfs", "/sys", "sysfs", MS_NOSUID|MS_NODEV|MS_NOEXEC, NULL))
		error(1, errno, "mount");
	if (umount2("/mnt", MNT_DETACH))
		error(1, errno, "umount2");

#define WRITEFILE(path, data) do {					\
	int fd = open(path, O_WRONLY|O_CLOEXEC);			\
	if (fd < 0)							\
		error(1, errno, path);					\
	if (write(fd, data, sizeof(data) - 1) != sizeof(data) - 1)	\
		error(1, errno, "write");					\
	close(fd);							\
} while (0)

	WRITEFILE("/proc/self/uid_map", "0 0 1");
	WRITEFILE("/proc/self/setgroups", "deny");
	WRITEFILE("/proc/self/gid_map", "0 0 1");

	puts("Entering jail...");
	execl("/bin/bash", "-bash", "-i", NULL);
	error(1, errno, "execl");
}
