# ART与安全攻防应用简介

> 在日常的 Android 应用安全分析中，经常会遇到一些对抗，比如目标应用加壳、混淆、加固，需要进行脱壳还原；又或者会有针对常用注入工具的检测，比如 frida、Xposed 等，这时候为了取证分析，或者是绕过检测，就需要对Android ART虚拟机进行了解和定制。

## Java VM

Java 本身是 Java 虚拟机来执行的，而 Android 代码也是用 Java 代码编写的，运行时也会有一个解析字节码的虚拟机。和标准的 JVM 不同，Android 中实际会将 Java 代码编译为 Dalvik 字节码，运行时解析的也是用自研的虚拟机实现。Dalvik虚拟机使用空间换时间的策略，加快应用的启动速度。

App应用进程是通过zygote进程fork出来的，子进程会继承父进程的进程空间，对于只读部分可以直接使用，而数据段也可以通过 COW(Copy-on-write) 共享 (内核不会复制进程的整个地址空间，而是只复制其页表，fork 之后的父子进程的地址空间指向同样的物理内存页)，通过查看 zygote 与其子进程的 `/proc/self/maps` 可以发现大部分系统库的映射都是相同的。这样做能够节省移动端本就宝贵的物理内存。




## ART流程分析与梳理

### Dalvik

在ART之前，首先需要了解Dalvik。Dalvik虚拟机与Java虚拟机的最显著区别是它们分别具有不同的类文件格式以及指令集。Dalvik虚拟机使用的是dex（Dalvik Executable）格式的类文件，而Java虚拟机使用的是class格式的类文件。一个dex文件可以包含若干个类，而一个class文件只包括一个类。由于一个dex文件可以包含若干个类，因此它就可以将各个类中重复的字符串和其它常数只保存一次，从而节省了空间，这样就适合在内存和处理器速度有限的手机系统中使用。一般来说，包含有相同类的未压缩dex文件稍小于一个已经压缩的jar文件。

APP 应用进程实际上是通过 zygote 进程 fork 出来的。这样的好处是子进程继承了父进程的进程空间，对于只读部分可以直接使用，而数据段也可以通过 COW(Copy On Write) 进行延时映射。查看 zygote 与其子进程的`/proc/self/maps`可以发现大部分系统库的映射都是相同的，这就是 fork 所带来的好处。










## ArtMethod结构

从Android 5.0（Lollipop）开始，ART取代了之前的Dalvik虚拟机作为Android的主要运行时环境。当分析到JNI函数时，一般都会通过`RegisterNatives`函数来确认JNI函数的地址，从而进行下一步的分析；更进一步，也存在非正常流程的JNI函数的绑定，那么我们怎么来追踪JNI函数的执行流程呢，此时就要提到`ArtMethod`的结构了

```c

```

## 参考文档

[Dalvik](https://blog.csdn.net/Luoshengyang/article/details/8852432)
[ArtHook](https://github.com/mar-v-in/ArtHook)
[我为Dexposed续一秒——论ART上运行时 Method AOP实现 ](https://weishu.me/2017/11/23/dexposed-on-art/)
[ART 在 Android 安全攻防中的应用](https://evilpan.com/2021/12/26/art-internal/)
[在Android N上对Java方法做hook遇到的坑](http://rk700.github.io/2017/06/30/hook-on-android-n/)
[Frida Internal - Part 3: Java Bridge 与 ART hook](https://evilpan.com/2022/04/17/frida-java/#native-api)
[android逆向奇技淫巧十三：定制art内核（一）：跟踪jni函数注册和调用，绕过反调试](https://www.cnblogs.com/theseventhson/p/14952092.html)
[android逆向奇技淫巧十四：定制art内核（二）：VMP逆向----仿method profiling跟踪jni函数执行](https://www.cnblogs.com/theseventhson/p/14961107.html)