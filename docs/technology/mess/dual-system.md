---
title: 双系统配置合集
slug: technology/mess/discussion-11/
url: https://github.com/jygzyc/notes/discussions/11
date: 2024-05-27
authors: [jygzyc]
categories: 
  - 0199-折腾
labels: []
comments: true
---

<!-- dual_system -->

## Windows关闭快速启动

控制面板 -> 电源选项 -> 选择电源按钮的功能 -> 更改当前不可用的设置 -> 取消启用快速启动

## 双系统下 Ubuntu 读写/挂载 Windows 中的硬盘文件 + 解决文件系统突然变成只读[^1]

查看所有盘符

```bash
$ sudo fdisk -l
...
设备                  起点       末尾       扇区   大小 类型
/dev/nvme0n1p1        2048     206847     204800   100M EFI 系统
/dev/nvme0n1p2      206848     239615      32768    16M Microsoft 保留
/dev/nvme0n1p3      239616  564531199  564291584 269.1G Microsoft 基本数据
/dev/nvme0n1p4   564531200  566231039    1699840   830M Windows 恢复环境
/dev/nvme0n1p5   566231040 2453667839 1887436800   900G Microsoft 基本数据
/dev/nvme0n1p6  2453667840 2663397375  209729536   100G Microsoft 基本数据
/dev/nvme0n1p7  2663397376 2665398271    2000896   977M Linux 文件系统
/dev/nvme0n1p8  2665398272 2785398783  120000512  57.2G Linux 文件系统
/dev/nvme0n1p9  3875028992 3907028991   32000000  15.3G Linux swap
/dev/nvme0n1p10 2785398784 3875028991 1089630208 519.6G Linux 文件系统
```

我们的目标是挂载 `/dev/nvme0n1p6`，先创建目录

`sudo mkdir /mnt/sync`

 **必须要先关闭Windows的快速启动**

- 临时挂载

```bash
sudo mount /dev/nvme0n1p6 /mnt/sync
```

- 永久挂载（推荐）

首先获取 `/dev/nvme0n1p6` 的 UUID

```bash
sudo blkid /dev/nvme0n1p6
/dev/nvme0n1p6: LABEL="sync" BLOCK_SIZE="512" UUID="72523FXXXXXXXXXX" TYPE="ntfs" PARTLABEL="Basic data partition" PARTUUID="290ebe9b-XXXX-XXXX-XXXX-6ab7efXXXXXX"
```

可以发现在输出结果中可以发现一段 `UUID="XXXXXXXXXXX"` 的内容，右键选中复制下来

接着就来修改系统文件 `/etc/fstab`（`sudo vim /etc/fstab`），把如下内容添加进去，照着上面添加就好

```txt
UUID=XXXXXXXXXX   /mnt/sync   ntfs  defaults   0   2
```

保存之后执行 `mount -a`

如果文件系统显示read-only，那么以下处理方式通用

```bash
apt-get install ntfs-3g # 先安装 ntfs-3g
ntfsfix /dev/nvme0n1p6 # 再修复即可
```

如果显示 `target is busy`，就先杀掉占用

```bash
fuser -m -u /dev/nvme0n1p6 # 获取占用
kill xxx # 干掉
umount /dev/nvme0n1p6
mount /dev/nvme0n1p6 /mnt/sync # 重新挂载
```

如果不行就`ntfsfix /dev/nvme0n1p6`修复一下再挂载

## Ubuntu下输入法安装

搜索了一下，最后决定使用中州韵输入法，安装起来也比较简单，[官网链接](https://rime.im)

直接使用 `apt-get install ibus-rime` 即可安装

## mihomo clash 服务创建[^2]

- 下载二进制可执行文件 [releases](https://github.com/MetaCubeX/mihomo/releases)
- 将下载的二进制可执行文件重名名为 `mihomo` 并移动到 `/usr/local/bin/`
- 以守护进程的方式，运行 `mihomo`。

使用以下命令将 Clash 二进制文件复制到 /usr/local/bin, 配置文件复制到 /etc/mihomo:

```bash
cp mihomo /usr/local/bin
cp config.yaml /etc/mihomo
```

创建 systemd 配置文件 `/etc/systemd/system/mihomo.service`:

```
[Unit]
Description=mihomo Daemon, Another Clash Kernel.
After=network.target NetworkManager.service systemd-networkd.service iwd.service

[Service]
Type=simple
LimitNPROC=500
LimitNOFILE=1000000
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE CAP_SYS_TIME CAP_SYS_PTRACE CAP_DAC_READ_SEARCH CAP_DAC_OVERRIDE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE CAP_SYS_TIME CAP_SYS_PTRACE CAP_DAC_READ_SEARCH CAP_DAC_OVERRIDE
Restart=always
ExecStartPre=/usr/bin/sleep 1s
ExecStart=/usr/local/bin/mihomo -d /etc/mihomo
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
```

使用以下命令重新加载 systemd:

```bash
systemctl daemon-reload
```

启用 mihomo 服务：

```bash
systemctl enable mihomo
```

[^1]: [虤虤豆的博客](https://tiger.fail/archives/ubuntu-rw-windows-files.html)
[^2]: [虚空终端 Docs](https://wiki.metacubex.one/)<script src="https://giscus.app/client.js"
    data-repo="jygzyc/notes"
    data-repo-id="R_kgDOJrOxMQ"
    data-mapping="number"
    data-term="11"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="top"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    data-loading="lazy"
    crossorigin="anonymous"
    async>
</script>
