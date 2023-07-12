#! /bin/sh

qemu-system-x86_64 \
  -no-reboot \
  -machine accel=kvm:tcg \
  -cpu host \
  -net none \
  -serial stdio \
  -display none \
  -monitor none \
  -vga none \
  -snapshot \
  -initrd /home/user/initrd \
  -kernel /home/user/bzImage
