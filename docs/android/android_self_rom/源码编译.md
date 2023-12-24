# Android源码编译

编译Android系统的时候遇到了环境不同，稳定性不同的问题，选择docker解决问题

> 以编译Google Pixel 3，lineageOS 20.0为例

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
repo init -u https://github.com/LineageOS/android.git -b lineage-20.0 --git-lfs
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

## docker安装

由于我需要对制作好的image进行上传，所以这里就采用官方源进行安装了

```bash
$ curl -fsSL get.docker.com -o get-docker.sh
```

执行这个命令后，脚本就会自动的将一切准备工作做好，并且把 Docker 的稳定(stable)版本安装在系统中。

之后我们启动docker

```bash
$ sudo systemctl enable docker
$ sudo systemctl start docker
```

默认情况下，docker 命令会使用 Unix socket 与 Docker 引擎通讯。而只有 root 用户和 docker 组的用户才可以访问 Docker 引擎的 Unix socket。出于安全考虑，一般 Linux 系统上不会直接使用 root 用户。因此，更好地做法是将需要使用 docker 的用户加入 docker 用户组

```bash
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
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

## 定制镜像

执行`git clone https://github.com/jygzyc/PersonalDocker.git`，在`android/`目录下执行`docker buildx build . -t android:v1`

> 需要说明的是，docker中不推荐使用ccache，因为ccache会访问主机的部分目录，这时候可能会出现权限拒绝的问题，在资源足够的情况下不需要使用ccache

构建完成后按照`README.md`即可执行bash

## 执行编译

```bash
source build/envsetup.sh
breakfast blueline # 若编译user系统，则执行 breakfast blueline user，下同

brunch blueline
```

## 参考文献

- [Docker - 从入门到实践](https://yeasy.gitbook.io/docker_practice)
- [Build LineageOS for Google Pixel 3](https://wiki.lineageos.org/devices/blueline/build)
- [PersonalDocker](https://github.com/jygzyc/PersonalDocker/)