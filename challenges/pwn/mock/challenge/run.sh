#! /bin/sh

cp /mnt/OVMF_VARS.fd /tmp/OVMF_VARS_copy.fd

/home/user/qemu-system-x86_64 \
  -no-reboot \
  -enable-kvm \
  -m 8192 \
  -cpu Penryn,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check \
  -machine q35 \
  -usb -device usb-kbd -device usb-tablet \
  -smp 1,cores=1,sockets=1 \
  -device usb-ehci,id=ehci \
  -device nec-usb-xhci,id=xhci \
  -global nec-usb-xhci.msi=off \
  -global ICH9-LPC.acpi-pci-hotplug-with-bridge-support=off \
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
  -drive if=pflash,format=raw,readonly=on,file=/mnt/OVMF_CODE.fd \
  -drive if=pflash,format=raw,file=/tmp/OVMF_VARS_copy.fd \
  -smbios type=2 \
  -device ich9-ahci,id=sata \
  -drive id=MacHDD,if=none,snapshot=on,file=/mnt/mock_kernel_final_SERVER.qcow2,format=qcow2 \
  -device ide-hd,bus=sata.4,drive=MacHDD \
  -netdev user,id=net0,restrict=on,hostfwd=tcp::2223-:22 \
  -device e1000-82545em,netdev=net0,id=net0 \
  -serial mon:stdio \
  -device vmware-svga \
  -display none \
  -vnc 127.0.0.1:3,password=off \
  -k en-us
