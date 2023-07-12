# To build, run:
# DOCKER_BUILDKIT=1 docker build . --target release --output type=local,dest=.

FROM --platform=linux/amd64 ubuntu:22.04 AS build

RUN apt-get update -y && apt-get install -y build-essential
RUN apt-get install -y python3

WORKDIR /root

COPY Makefile .
COPY chal.c .
COPY assembler.py .
COPY highlevel.py .
COPY program.py .

RUN make

FROM scratch AS release

COPY --from=build /root/chal /chal
COPY --from=build /root/program /program
