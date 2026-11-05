# syntax=docker/dockerfile:1
FROM ubuntu:22.04
RUN --mount=type=secret,id=ca,required=true,mode=0444 \
    sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g; s|http://security.ubuntu.com|https://security.ubuntu.com|g' /etc/apt/sources.list && \
    apt-get -o Acquire::https::CaInfo=/run/secrets/ca update && \
    DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::https::CaInfo=/run/secrets/ca install -y --no-install-recommends \
      libwebkit2gtk-4.0-37 libjpeg-turbo8 libsecret-1-0 libusb-1.0-0 \
      libxext6 libx11-6 libxkbcommon0 libxxf86vm1 libsm6 libgtk-3-0 \
      xvfb xauth x11-utils openjdk-17-jre-headless ca-certificates && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /workspace/GarminShemah
RUN --mount=type=secret,id=ca,required=true,mode=0444 \
    apt-get -o Acquire::https::CaInfo=/run/secrets/ca update && \
    DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::https::CaInfo=/run/secrets/ca install -y --no-install-recommends x11-apps && \
    rm -rf /var/lib/apt/lists/*
