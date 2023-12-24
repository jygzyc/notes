# 备忘录笔记

## Docker

### Docker缓存清理

`docker system df`​​ 命令，类似于 Linux上的 df 命令，用于查看 Docker 的磁盘使用情况

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

### Podman 

在 Ubuntu 22.04 上安装 Podman,默认情况下，Podman 包包含在 Ubuntu 默认存储库中。您只需运行以下命令即可安装它：

```bash
apt install podman -y
```

默认情况下，Podman 注册表未配置为从 Web 下载和安装容器镜像。所以你需要先配置它。

`vim /etc/containers/registries.conf`添加以下行：

```conf
[registries.search]
registries=["registry.access.redhat.com", "registry.fedoraproject.org", "docker.io"]
```

完成后保存并关闭文件。

## Android


## Linux



## Others

## 参考文档

[Docker Build Cache 缓存清理 ](https://blog.51cto.com/u_1472521/5981360)
[如何在 Ubuntu 22.04 上安装 Podman](https://cn.linux-console.net/?p=3521)
