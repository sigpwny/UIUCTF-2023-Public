# Copyright 2023 Google LLC
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

FROM alpine as git-clone

RUN apk add git openssh-client

COPY uiuctf-2023-deploy-key /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa
RUN echo 'StrictHostKeyChecking no' > /root/.ssh/config

RUN git clone git@github.com:sigpwny/uiuctf-2023-ctfd-theme.git /uiuctf-2023-ctfd-theme && \
    git -C /uiuctf-2023-ctfd-theme checkout fb83df321cb9a0acebc8624673f59f908bdc1df8 && \
    rm -rf /uiuctf-2023-ctfd-theme/.git

RUN git clone https://github.com/sigpwny/ctfd-dynamic-challenges-mod /ctfd-dynamic-challenges-mod && \
    git -C /ctfd-dynamic-challenges-mod checkout 1c84dbe5b0d157a618e5ffa47d626c9f3c3fe0c4 && \
    rm -rf /ctfd-dynamic-challenges-mod/.git

RUN git clone https://github.com/sigpwny/ctfd-discord-webhook-plugin /ctfd-discord-webhook-plugin && \
    git -C /ctfd-discord-webhook-plugin checkout d6df2ab1a6a7980d8ee4d7f134987c8dd4b2531b && \
    rm -rf /ctfd-discord-webhook-plugin/.git

RUN git clone https://github.com/sigpwny/ctfd-discord-auth.git /ctfd-discord-auth && \
    git -C /ctfd-discord-auth checkout 4469ad8277deefc5d2f3351dd4820cabbdac8645 && \
    rm -rf /ctfd-discord-auth/.git

RUN git clone https://github.com/sigpwny/CTFd-scores-ctftime /ctfd-scores-ctftime && \
    git -C /ctfd-scores-ctftime checkout 8b07eaf1d17aed88c3b8f2ca82751cbe72a7ec4b && \
    rm -rf /ctfd-scores-ctftime/.git

FROM ctfd/ctfd:3.5.3

USER root

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y patch && \
    rm -rf /var/lib/apt/lists/*

COPY patches /patches

RUN for file in /patches/*.patch; do \
        patch -p1 -d /opt/CTFd/ < "$file"; \
    done;

COPY --from=git-clone /uiuctf-2023-ctfd-theme /opt/CTFd/CTFd/themes/uiuctf-2023-ctfd-theme
COPY --from=git-clone /ctfd-dynamic-challenges-mod /opt/CTFd/CTFd/plugins/dynamic_challenges_mod
COPY --from=git-clone /ctfd-discord-webhook-plugin /opt/CTFd/CTFd/plugins/discord_webhooks_plugin
COPY --from=git-clone /ctfd-discord-auth /opt/CTFd/CTFd/plugins/discord_auth
COPY --from=git-clone /ctfd-scores-ctftime /opt/CTFd/CTFd/plugins/ctfd-scores-ctftime

RUN python3 -m pip install -r /opt/CTFd/CTFd/plugins/discord_webhooks_plugin/requirements.txt

USER ctfd
