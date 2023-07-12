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

# docker buildx build . --target release --output type=local,dest=..

FROM ubuntu:22.04 as zapps-build

# Build zapps in a glibc environment; wouldn't it be fun to run a foreign libc
# as if nothing is out of the ordinary?
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y build-essential

RUN mkdir /zapps
COPY zapps-src /zapps/src
RUN make -C /zapps/src
RUN mv /zapps/src/relative /zapps/build

FROM alpine as disk

RUN apk add git build-base linux-headers bash
RUN apk add coreutils util-linux procps strace gdb

RUN rm -rf /usr/share/apk

RUN rm /sbin/init
RUN mkdir /home/user
RUN adduser --home /home/user --gecos '' --shell /bin/bash --disabled-password --no-create-home --uid 1000 user
RUN chown user:user /home/user

COPY init_chal /home/user/

# Build virophage
COPY virophage.c /home/user/
RUN gcc -g -Os -static-pie -fPIE -ffreestanding -nostartfiles /home/user/virophage.c -o /home/user/virophage
RUN chmod 4755 /home/user/virophage

# Build am-i-not-root
COPY am-i-not-root.c /home/user/
RUN gcc -g -Os /home/user/am-i-not-root.c -o /home/user/am-i-not-root

COPY --from=zapps-build /zapps /usr/lib/zapps
RUN chmod 4755 /usr/lib/zapps/build/exe /usr/lib/zapps/build/exe

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
RUN make -j$(nproc) -C /kernel/linux-6.3.8 && cp /kernel/linux-6.3.8/arch/x86/boot/bzImage /bzImage

COPY 0001-fs-namespace-Allow-unpriv-OPEN_TREE_CLONE.patch /tmp/
COPY 0002-fs-namespace-Allow-generic-loopback-mount-without-re.patch /tmp/
COPY 0003-fs-namespace-Check-userns-instead-of-mntns-in-mnt_ma.patch /tmp/
RUN patch -p1 -d /kernel/linux-6.3.8 < /tmp/0001-fs-namespace-Allow-unpriv-OPEN_TREE_CLONE.patch
RUN patch -p1 -d /kernel/linux-6.3.8 < /tmp/0002-fs-namespace-Allow-generic-loopback-mount-without-re.patch
RUN patch -p1 -d /kernel/linux-6.3.8 < /tmp/0003-fs-namespace-Check-userns-instead-of-mntns-in-mnt_ma.patch
RUN make -j$(nproc) -C /kernel/linux-6.3.8 && cp /kernel/linux-6.3.8/arch/x86/boot/bzImage /bzImage-zapp-setuid-2

FROM alpine as handout-build

RUN apk add tar zstd btrfs-progs

RUN ls /sbin/mkfs.btrfs

COPY --from=disk / /disk

RUN mkdir -p /handout/run
COPY --from=kernel-build /bzImage /bzImage-zapp-setuid-2 /handout/run/

COPY run.sh /handout/run/run.sh
RUN cp /handout/run/run.sh /handout/run/run-zapp-setuid-2.sh && \
    sed -i 's/bzImage/bzImage-zapp-setuid-2/' /handout/run/run-zapp-setuid-2.sh
COPY init /disk/sbin/init
RUN /sbin/mkfs.btrfs -r /disk --shrink /handout/run/disk.img

COPY . /handout/chal_build
COPY handout-readme /handout/README

RUN tar --mtime="@0" --sort=name -cf - handout | zstd -19 -T0 > /handout.tar.zst

FROM scratch as release
COPY --from=handout-build /handout.tar.zst /
