---
title: Android源码编译
slug: technology/android/rom/discussion-4/
number: 4
url: https://github.com/jygzyc/notes/discussions/4
created: 2024-04-19
updated: 2024-05-27
authors: [jygzyc]
categories: 
  - 0101-Android
labels: ['010101-ROM定制']
comments: false
---

<!-- android_source_compile -->
编译Android系统的时候遇到了环境不同，稳定性不同的问题，选择docker解决问题

> 以编译Google Pixel 3，lineageOS 21.0为例

## 下载源码

第一步，安装repo

```bash
mkdir ~/bin
PATH=~/bin:$PATH
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
```

第二步，配置git

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

由于其大小，一些存储库配置为 lfs 或大文件存储，需要安装git-lfs：

```bash
git lfs install # apt install git-lfs
```

第三步，初始化LineageOS存储库

```bash
repo init -u https://github.com/LineageOS/android.git -b lineage-21.0 --git-lfs
```

第四步，同步源码并准备，这里可以先参考[清华lineageOS 源代码镜像使用帮助](https://mirrors.tuna.tsinghua.edu.cn/help/lineageOS/)，先使用清华源同步，但是最后还是需要切回github同步一下，不然指定机型编译后会报错

```bash
repo sync

# after finished
source build/envsetup.sh
breakfast blueline
```

第五步，同步设备特定固件代码

方法一，先刷机再执行`device/google/blueline`目录下的`./extract-files.sh`

方法二，从OTA包中获取固件，此处可以参考 [Extracting proprietary blobs from LineageOS zip files](https://wiki.lineageos.org/extracting_blobs_from_zips)

## 定制镜像

`Dockerfile`文件如下

```dockerfile
FROM ubuntu:22.04

# Modify the sources.list for improving download speed 
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list

# Create environment
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -qq update
RUN apt-get -y install bc bison build-essential ccache cpio curl flex g++-multilib gcc-multilib 
RUN apt-get -y install git git-lfs gnupg gperf imagemagick libc6-dev libelf-dev libgl1-mesa-dev liblz4-tool
RUN apt-get -y install libncurses5 libncurses5-dev libsdl1.2-dev libssl-dev libx11-dev libxml2 libxml2-utils 
RUN apt-get -y install lzop lzip m4 make ncurses-dev patch pngcrush python3 python3-pip rsync schedtool 
RUN apt-get -y install squashfs-tools unzip x11proto-core-dev xsltproc zip zlib1g-dev openjdk-11-jdk
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install repo
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/bin/repo

# Turn on caching
ENV USE_CCACHE 1
ENV CCACHE_EXEC /usr/bin/ccache
ENV CCACHE_DIR=/ccache
RUN ccache -M 50G

# Mount source code directory
VOLUME /source
ENV WORKDIR /source
WORKDIR $WORKDIR
```

`docker-compose.yml`配置如下

```yml
version: "3"
services:
  android_builder:
    build: .
    command: /bin/bash
    tty: true
    stdin_open: true
    volumes:
      - /home/${USER}/android/lineage/:/source # SourceCode Directory
      - /home/${USER}/.ccache:/ccache # ccache directory
```

在执行前先配置好`ccache`的目录和源码目录，再使用``docker compose run --rm android_builder bash`启动

> 整理了一个项目 [dockers](https://github.com/jygzyc/dockers)

## 执行编译

```bash
source build/envsetup.sh
breakfast blueline # 若编译user系统，则执行 breakfast blueline user，下同

brunch blueline
```

## 参考文献

- [Docker - 从入门到实践](https://yeasy.gitbook.io/docker_practice)
- [Build LineageOS for Google Pixel 3](https://wiki.lineageos.org/devices/blueline/build)
