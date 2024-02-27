# 内核编译与KernelSU集成

## 内核编译

### 确认手机信息

在Android终端执行`getprop | grep device`，并寻找形似 `ro.xx.device` 这一行，里面的内容即为你的手机代号，这里我的手机是Google Pixel 3 ，型号如下所示

![image-20230604002803199](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604002803199.png)

之后需要获取设备架构，执行`uname -m`，这里我的设备显示是`aarch64`

最后一步是获取当前设备的内核版本，执行`uname -r`，这里我的设备显示是 `4.9.337-NekoMiya+`

### 同步内核源码

#### 直接同步内核源码

先找到Pixel3的内核源码，由于这里用的是PixelExperience，所以到Github上能找到源码的目录 [PixelExperience-Devices/kernel_google_bluecross: Dependency of Google Pixel 3 (blueline), Google Pixel 3 XL (crosshatch) (github.com)](https://github.com/PixelExperience-Devices/kernel_google_bluecross)

如果想编译AOSP的内核，那么可以查看Google的官方指导[构建内核  | Android 开源项目  | Android Open Source Project](https://source.android.com/docs/setup/build/building-kernels?hl=zh-cn)

分支的话有4个，这里选最新的 `thirteen-plus`

#### 通过repo获取内核源码

由于我这边也需要编译整机代码，加上工具链本身也比较复杂，所以这里就一并都使用`repo`同步下来了。

![image-20230604040736034](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604040736034.png)

### 编译

由于我这边直接使用了repo，所以执行`make bootimage`，最后可以在指定的目录中找到`boot.img`

![image-20230604053658885](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604053658885.png)

## KernelSU

这里我们参考官方的教程，链接为[如何为非 GKI 内核集成 KernelSU](https://kernelsu.org/zh_CN/guide/how-to-integrate-for-non-gki.html)，并使用 `kprobe` 集成

### Kprobe配置

先进入到内核源码目录下，在根目录新建分支，这里命名为`kernelsu`

```bash
git checkout -b kernelsu # 此处新建一个分支，方便之后进行同步和更改
```

建立完成后执行如下命令

```bash
curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/main/kernel/setup.sh" | bash -
```

![image-20230604041106417](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604041106417.png)

接着检查内核是否开启了`kprobe`，在`arch/arm64/configs/b1c1_defconfig`中添加如下配置

```
# KPROBE config
CONFIG_KPROBES=y
CONFIG_HAVE_KPROBES=y
CONFIG_KPROBE_EVENTS=y
```

![image-20230604045632803](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604045632803.png)

### 修改文件

- 修改`build.config.bluecross`

在`build.config.bluecross`中注释掉`POST_DEFCONFIG_CMDS`这一行，否则编译会报错

![image-20230604041459869](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604041459869.png)

- 修改`fs/exec.c`中的do_execveat_common

![image-20230604053323694](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604053323694.png)

```c
// kernelsu add
extern int ksu_handle_execveat(int *fd, struct filename **filename_ptr, 
			void *argv,
            void *envp, 
			int *flags);
// kernelsu end

/*
 * sys_execve() executes a new program.
 */
static int do_execveat_common(int fd, struct filename *filename,
			      struct user_arg_ptr argv,
			      struct user_arg_ptr envp,
			      int flags)
{
	char *pathbuf = NULL;
	struct linux_binprm *bprm;
	struct file *file;
	struct files_struct *displaced;
	int retval;

	// kernelsu add
	ksu_handle_execveat(&fd, &filename, &argv, &envp, &flags);
	// kernelsu end

	if (IS_ERR(filename))
		return PTR_ERR(filename);
...
```

- 修改`fs/open.c`，找到faccessat的系统调用定义并修改

![image-20230604050614525](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604050614525.png)

```c
// kernelsu add
extern int ksu_handle_faccessat(int *dfd, const char __user **filename_user, 
			int *mode,
            int *flags);
// kernelsu end

/*
 * access() needs to use the real uid/gid, not the effective uid/gid.
 * We do this by temporarily clearing all FS-related capabilities and
 * switching the fsuid/fsgid around to the real ones.
 */
SYSCALL_DEFINE3(faccessat, int, dfd, const char __user *, filename, int, mode)
{
	const struct cred *old_cred;
	struct cred *override_cred;
	struct path path;
	struct inode *inode;
	struct vfsmount *mnt;
	int res;
	unsigned int lookup_flags = LOOKUP_FOLLOW;

	// kernelsu add
	ksu_handle_faccessat(&dfd, &filename, &mode, NULL);
	// kernelsu end

	if (mode & ~S_IRWXO)
...
```

- 修改`fs/read_write.c`中的vfs_read

![image-20230604043617929](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604043617929.png)

```c
// kernelsu add
extern int ksu_handle_vfs_read(struct file **file_ptr, char __user **buf_ptr,
            size_t *count_ptr, loff_t **pos);
// kernelsu end

ssize_t vfs_read(struct file *file, char __user *buf, size_t count, loff_t *pos)
{
	ssize_t ret;

	// kernelsu add
    ksu_handle_vfs_read(&file, &buf, &count, &pos);
    // kernelsu end
	if (!(file->f_mode & FMODE_READ))
...
```

- 修改`fs/stat.c`中的vfs_fstatat（Pixel 3中适配的旧版本内核没有`vfs_statx`函数）

![image-20230604044525839](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604044525839.png)

```c
// kernelsu add
extern int ksu_handle_stat(int *dfd, const char __user **filename_user, int *flags);
// kernelsu end

int vfs_fstatat(int dfd, const char __user *filename, struct kstat *stat,
		int flag)
{
	struct path path;
	int error = -EINVAL;
	unsigned int lookup_flags = 0;

	// kernelsu add
	ksu_handle_stat(&dfd, &filename, &flag);
	// kernelsu end
...
```

- 打开 KernelSU内置的安全模式，修改`drivers/input/input.c`中的`input_handle_event` 方法

![image-20230604044930297](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604044930297.png)

```c
// kernelsu add
extern int ksu_handle_input_handle_event(unsigned int *type, 
					unsigned int *code, 
					int *value);
// kernelsu end

static void input_handle_event(struct input_dev *dev,
			       unsigned int type, unsigned int code, int value)
{
	int disposition = input_get_disposition(dev, type, code, &value);

	// kernelsu add
	ksu_handle_input_handle_event(&type, &code, &value);
	// kernelsu end
	if (disposition != INPUT_IGNORE_EVENT && type != EV_SYN)
		add_input_randomness(type, code, value);
...
```

编译的过程就和上面的步骤是一样的

## 结果验证

使用`adb reboot bootloader`重启到`bootloader`，将编译好的`boot.img`使用`fastboot flash boot boot.img`刷到手机里，启动手机，安装KernelSU管理器，即可看到KernelSU正常工作

![image-20230604053409933](images/%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91%E4%B8%8EKernelSU%E9%9B%86%E6%88%90/image-20230604053409933.png)

接下来就可以快乐玩耍了！

## 内核同步

在上述内核修改结束后，可以将定制的内核文件同步到自己的github上，方便以后的更新，修改和编译

```bash
$ git remote add kernelsu git@github.com:jygzyc/kernel_google_bluecross_KernelSU.git # 添加远程分支
$ git add .
$ git commit -m "KernelSU Adaptation"
$ git push -u kernelsu kernelsu:thirteen-plus # 首次将kernelsu分支推到远程kernelsu仓库的thirteen-plus分支
```

之后如果内核代码更新，那么就需要合并处理

```bash
$ git fetch pixel-devices thirteen-plus # 从远程仓库pixel-devices拉取thirteen-plus的代码

$ git checkout kernelsu  # 切换到本地分支
$ git merge # 将远程分支合并到本地分支

$ git push kernelsu kernelsu:thirteen-plus # 将kernelsu分支推到远程kernelsu仓库的thirteen-plus分支
```

## 参考文献

[Android从零开始的内核编译 - 掘金 (juejin.cn)](https://juejin.cn/post/7211713478179864613)

[如何为非 GKI 内核集成 KernelSU | KernelSU](https://kernelsu.org/zh_CN/guide/how-to-integrate-for-non-gki.html)

[AOSP编译保姆级教程（三）-KernelSU (qq.com)](https://mp.weixin.qq.com/s/kV8yjm_XCIVUparqo8efUQ)
