# 双系统相关配置

## 双系统下 Ubuntu 读写/挂载 Windows 中的硬盘文件 + 解决文件系统突然变成只读

!!! quote "Reference"

    [虤虤豆的博客](https://tiger.fail/archives/ubuntu-rw-windows-files.html)

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

!!! warning "First Of All"
    关闭Windows的快速启动

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

