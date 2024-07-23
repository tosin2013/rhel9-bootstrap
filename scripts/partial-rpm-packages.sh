#!/bin/bash

sudo dnf -y install \
  bzip2-devel \
  libffi-devel \
  openssl-devel \
  make \
  zlib-devel \
  perl \
  ncurses-devel \
  sqlite \
  sqlite-devel \
  git \
  wget \
  curl \
  nano \
  vim \
  unzip \
  ansible-core \
  bind-utils \
  tar \
  util-linux-user \
  gcc \
  podman \
  skopeo \
  buildah \
  crun \
  slirp4netns \
  fuse-overlayfs \
  containernetworking-plugins \
  iputils \
  iproute \
  runc \
  tmux

sudo dnf -y groupinstall "Development Tools"

if [ ! -f ~/.tmux/.tmux.conf.local ];
then 
    cd ~
    git clone https://github.com/gpakosz/.tmux.git
    ln -s -f .tmux/.tmux.conf
    cp .tmux/.tmux.conf.local .
fi
