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

FROM ubuntu:22.04 as tar-extract

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y zstd

RUN mkdir /home/user/
COPY handout.tar.zst /home/user/
RUN tar -C /home/user/ -xf /home/user/handout.tar.zst

FROM alpine as chroot

RUN apk add expect qemu-system-x86_64

RUN mkdir /home/user/

COPY --from=tar-extract /home/user/handout/run/disk.img /home/user/disk.img

RUN mkdir /secret

FROM gcr.io/kctf-docker/challenge@sha256:d884e54146b71baf91603d5b73e563eaffc5a42d494b1e32341a5f76363060fb

COPY --from=chroot / /chroot
COPY --from=tar-extract /home/user/handout/run/bzImage /chroot/home/user/bzImage

COPY nsjail.cfg /home/user/
COPY run.sh /chroot/home/user/run.sh
COPY bootscript.exp /chroot/home/user/bootscript.exp

COPY flag /chroot/secret

CMD kctf_setup && \
    chmod 666 /dev/kvm && \
    kctf_drop_privs \
    socat TCP-LISTEN:1337,reuseaddr,fork \
        EXEC:'kctf_pow nsjail --config /home/user/nsjail.cfg -- /home/user/bootscript.exp'
