FROM alpine

RUN apk add git bash python3

RUN git clone https://github.com/novnc/noVNC.git /root/noVNC -b v1.4.0 \
	&& git clone https://github.com/novnc/websockify /root/noVNC/utils/websockify -b v0.11.0 \
	&& cp /root/noVNC/vnc.html /root/noVNC/index.html \
	&& rm -rf /root/noVNC/.git \
	&& rm -rf /root/noVNC/utils/websockify/.git \
	&& apk del git

ENTRYPOINT /root/noVNC/utils/novnc_proxy --file-only --vnc localhost:5903 --listen 8080
