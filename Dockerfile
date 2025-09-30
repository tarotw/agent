# Base librechat images
ARG VERSION=v0.8.0-rc3
FROM ghcr.io/danny-avila/librechat:${VERSION}

USER root
RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community docker kubectl
RUN apk add --no-cache git curl
# Install Libsecret etc
RUN  apk add libsecret libsecret-dev

# Copy and install the k8s-run.sh script for dynamic pod name generation
COPY k8s-run.sh /usr/local/bin/k8s-run.sh
RUN chmod +x /usr/local/bin/k8s-run.sh

USER node
