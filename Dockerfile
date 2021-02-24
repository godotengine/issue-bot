FROM fedora:33

LABEL maintainer="Hein-Pieter van Braam-Stewart <hp@prehensile-tales.com>"

RUN dnf -y install python3-websocket-client python3-requests && \
    dnf clean all

COPY bot.py /root/bot.py
WORKDIR /root

CMD /root/bot.py
