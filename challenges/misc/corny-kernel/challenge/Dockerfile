# Copyright 2021-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:22.04 as kernel-build

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y wget build-essential && \
    apt-get install -y gawk flex bison bc zstd && \
    apt-get install -y libncurses-dev libssl-dev libssl-dev libelf-dev libudev-dev libpci-dev libiberty-dev

RUN apt-get install -y gcc-$(gcc --version | grep -oP '([0-9]+)\.([0-9]+).([0-9]+)' | head -n1 | cut -d. -f1)-plugin-dev

RUN mkdir /kernel
RUN wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.3.8.tar.xz -O /kernel/linux.tar.xz
RUN tar -C /kernel -xf /kernel/linux.tar.xz

COPY kconfig /kernel/linux-6.3.8/.config

COPY 0001-ptp_kvm-Silence-initialization-warning.patch /tmp/
RUN patch -p1 -d /kernel/linux-6.3.8 < /tmp/0001-ptp_kvm-Silence-initialization-warning.patch

COPY pwnybuiltin.c pwnymodule.c /kernel/linux-6.3.8/kernel
RUN echo 'obj-y += pwnybuiltin.o' >> /kernel/linux-6.3.8/kernel/Makefile
RUN echo 'obj-m += pwnymodule.o' >> /kernel/linux-6.3.8/kernel/Makefile

RUN make -j$(nproc) -C /kernel/linux-6.3.8 && cp /kernel/linux-6.3.8/arch/x86/boot/bzImage /bzImage
RUN make -j$(nproc) -C /kernel/linux-6.3.8 modules_install INSTALL_MOD_STRIP=1 MODLIB=/modules

FROM busybox as initrd

RUN rm -f /init
COPY init /
COPY --from=kernel-build /modules/kernel/kernel/pwnymodule.ko.gz /root

FROM alpine as initrd-build

RUN apk add tar zstd

COPY --from=initrd / /initrd
RUN cd /initrd && find . -print0 | cpio -0ov -H newc | zstd -19 -T0 > /initrd.zst

FROM alpine as chroot

RUN apk add expect qemu-system-x86_64

RUN mkdir /home/user/

COPY run.sh /home/user/run.sh

FROM gcr.io/kctf-docker/challenge@sha256:d884e54146b71baf91603d5b73e563eaffc5a42d494b1e32341a5f76363060fb

COPY --from=chroot / /chroot
COPY --from=kernel-build /bzImage /chroot/home/user/bzImage
COPY --from=initrd-build /initrd.zst /chroot/home/user/initrd

COPY nsjail.cfg /home/user/

CMD kctf_setup && \
    chmod 666 /dev/kvm && \
    kctf_drop_privs \
    socat TCP-LISTEN:1337,reuseaddr,fork \
        EXEC:'kctf_pow nsjail --config /home/user/nsjail.cfg -- /home/user/run.sh'
