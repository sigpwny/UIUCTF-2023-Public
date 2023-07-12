# Solution

This is a basic challenge aimed at teaching players how to load and unload a kernel module with the Linux kernel.

- untar the loadable kernel module file (pwnymodule.ko)
- `insmod pwnymodule.ko` to load driver into the kernel at runtime
- `rmmod pwnymodule` to remove pwnymodule from the kernel
- `lsmod` to view the status of currently loaded kernel modules
- `dmesg` to extract first and second half of the flag from kernel logs


