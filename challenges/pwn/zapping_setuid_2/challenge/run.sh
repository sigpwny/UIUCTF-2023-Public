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
  -virtfs local,multidevs=remap,path=/secret,security_model=none,mount_tag=flag,readonly=on \
  -drive file=/home/user/disk.img,format=raw,if=virtio,snapshot=on \
  -kernel /home/user/bzImage
