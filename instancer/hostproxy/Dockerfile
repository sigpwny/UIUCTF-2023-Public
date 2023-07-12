# Copyright 2022 Google LLC
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

FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y nginx libnginx-mod-http-lua

COPY nginx.conf /etc/nginx/nginx.conf
COPY proxy.lua /srv/proxy.lua

# https://serverfault.com/a/638855
CMD echo "resolver $(awk 'BEGIN{ORS=" "} $1=="nameserver" {print $2}' /etc/resolv.conf) valid=10s;" > /etc/nginx/resolvers.conf && \
    nginx
