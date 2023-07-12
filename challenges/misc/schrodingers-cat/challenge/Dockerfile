FROM ubuntu:20.04 as chroot

RUN apt-get update -y && apt-get install -y python3 python3-pip

RUN /usr/sbin/useradd --no-create-home -u 1000 user

COPY requirements.txt /
RUN pip3 install -r requirements.txt

WORKDIR /home/user
COPY flag.txt /
COPY server.py .

FROM gcr.io/kctf-docker/challenge@sha256:d884e54146b71baf91603d5b73e563eaffc5a42d494b1e32341a5f76363060fb

COPY --from=chroot / /chroot

COPY nsjail.cfg /home/user/

CMD /bin/sh
CMD kctf_setup && \
    kctf_drop_privs \
    socat \
      TCP-LISTEN:1337,reuseaddr,fork \
      EXEC:"kctf_pow nsjail --config /home/user/nsjail.cfg -- /home/user/server.py"
