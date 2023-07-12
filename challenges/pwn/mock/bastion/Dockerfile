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

# mkdir -p etc/ssh
# ssh-keygen -A -f .
# mv etc/ssh/ssh_host_* .
# rm -r etc
# ssh-keygen -c -C 'mock-bastion' -f ssh_host_ecdsa_key
# ssh-keygen -c -C 'mock-bastion' -f ssh_host_ed25519_key
# ssh-keygen -c -C 'mock-bastion' -f ssh_host_rsa_key

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y openssh-server && \
    rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' --uid 1000 user

COPY pam_sshd /etc/pam.d/sshd
COPY sshd_config /etc/ssh/

COPY ssh_host_*_key ssh_host_*_key.pub /etc/ssh/
RUN chmod 600 /etc/ssh/ssh_host_*_key /etc/ssh/ssh_host_*_key.pub

RUN chmod 700 /etc/ssh/
RUN mkdir -p /run/sshd

CMD /usr/sbin/sshd -D -e
