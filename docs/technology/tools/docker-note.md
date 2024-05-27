---
title: docker使用记录
slug: technology/tools/discussion-14/
url: https://github.com/jygzyc/notes/discussions/14
date: 2024-05-27
authors: [jygzyc]
categories: 
  - 0104-工具
labels: []
comments: true
---

<!-- docker-note -->

## docker安装

```bash
$ curl -fsSL get.docker.com -o get-docker.sh
```

执行这个命令后，脚本就会自动的将一切准备工作做好，并且把 Docker 的稳定(stable)版本安装在系统中。

之后我们启动docker

```bash
$ sudo systemctl enable docker
$ sudo systemctl start docker
```

默认情况下，docker 命令会使用 Unix socket 与 Docker 引擎通讯。而只有 root 用户和 docker 组的用户才可以访问 Docker 引擎的 Unix socket。出于安全考虑，一般 Linux 系统上不会直接使用 root 用户。因此，更好地做法是将需要使用 docker 的用户加入 docker 用户组，或者安装rootless的docker[^1]

```bash
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
# 或者使用脚本变为rootless模式
$ sudo apt-get install -y uidmap # 前置条件
$ dockerd-rootless.sh
```

新建终端测试

```bash
$ docker run --rm hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
719385e32844: Pull complete 
Digest: sha256:dcba6daec718f547568c562956fa47e1b03673dd010fe6ee58ca806767031d1c
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

## Docker缓存清理

`docker system df`​​ 命令，类似于 Linux上的 df 命令，用于查看 Docker 的磁盘使用情况[^2]

```bash
$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          3         0         3.463GB   3.463GB (100%)
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     19        0         578.8MB   578.8MB
```

TYPE 列出了 Docker 使用磁盘的 4 种类型：

|     类型      | 说明                                                                                |
| :-----------: | :---------------------------------------------------------------------------------- |
|    Images     | 所有镜像占用的空间，包括拉取下来的镜像，和本地构建的。                              |
|  Containers   | 运行的容器占用的空间，表示每个容器的读写层的空间。                                  |
| Local Volumes | 容器挂载本地数据卷的空间。                                                          |
|  Build Cache  | 镜像构建过程中产生的缓存空间（只有在使用 BuildKit 时才有，Docker 18.09 以后可用）。 |

清理 Build Cache缓存命令：

```bash
docker builder prune
```

另外，命令 `​​docker system prune`​​ 可以用于清理磁盘，删除关闭的容器、无用的数据卷和网络，以及dangling镜像（即无tag的镜像）

[^1]: [Run the Docker daemon as a non-root user (Rootless mode)](https://docs.docker.com/engine/security/rootless/)
[^2]: [Docker Build Cache 缓存清理 ](https://blog.51cto.com/u_1472521/5981360)
  
<script src="https://giscus.app/client.js"
    data-repo="jygzyc/notes"
    data-repo-id="R_kgDOJrOxMQ"
    data-mapping="number"
    data-term="14"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="top"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    data-loading="lazy"
    crossorigin="anonymous"
    async>
</script>
