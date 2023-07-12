#! /bin/sh

qemu-system-x86_64 \
  -no-reboot \
  -cpu max \
  -net none \
  -serial stdio \
  -display none \
  -monitor none \
  -vga none \
  -snapshot \
  -drive file=disk.img,format=raw,if=virtio,snapshot=on \
  -kernel bzImage
