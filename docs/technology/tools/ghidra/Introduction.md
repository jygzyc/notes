# Ghidra入门

## 环境准备

先贴一段官网的简介

> Ghidra是一个由国家安全局研究局创建和维护的软件逆向工程（SRE）框架。该框架包括一套功能齐全的高端软件分析工具，使用户能够在包括Windows、macOS和Linux在内的各种平台上分析编译的代码。功能包括反汇编、汇编、反编译、绘图和脚本，以及数百个其他功能。Ghidra支持多种处理器指令集和可执行文件格式，可以在用户交互和自动模式下运行。用户还可以使用Java或Python开发自己的Ghidra扩展组件和/或脚本。

到[Github-Ghidra](https://github.com/NationalSecurityAgency/ghidra)上可以下载到最新版本的Ghidra，下载解压后，需要Java环境才能够正常运行，我目前能够下载到的最新版本是`10.4`，适配的Java版本是17，创建一个jre方便脱机开启。通过`jdeps`命令找到Ghidra的依赖

```sh
$ jdeps LaunchSupport.jar
LaunchSupport.jar -> java.base
LaunchSupport.jar -> java.desktop
   <unnamed>                                          -> ghidra.launch                                      LaunchSupport.jar
   <unnamed>                                          -> java.awt                                           java.desktop
   <unnamed>                                          -> java.io                                            java.base
   <unnamed>                                          -> java.lang                                          java.base
   <unnamed>                                          -> java.lang.invoke                                   java.base
   <unnamed>                                          -> java.text                                          java.base
   <unnamed>                                          -> java.util                                          java.base
   <unnamed>                                          -> java.util.function                                 java.base
   <unnamed>                                          -> javax.swing                                        java.desktop
   ghidra.launch                                      -> java.io                                            java.base
   ghidra.launch                                      -> java.lang                                          java.base
   ghidra.launch                                      -> java.text                                          java.base
   ghidra.launch                                      -> java.util                                          java.base
```

![image-1698078146079](images/Introduction/image-1698078146077.png) 

然后可以通过`jlink`创建minimal的环境，在你执行目录的环境下就能看到jre环境了

```sh
jlink --add-modules java.base,java.desktop --output jre --compress=2 --no-header-files --no-man-pages --strip-debug
```

接下来还要设置从当前jre启动，编写脚本

```bat
@echo off
set JAVA_HOME=%~dp0jre
call %~dp0ghidraRun.bat

echo Start successfully.

timeout /t 1 /nobreak >nul
```

完整目录结构如下

```txt
.
├── Extensions
├── GPL
├── Ghidra
├── LICENSE
├── bom.json
├── docs
├── ghidraRun
├── ghidraRun.bat
├── ghidraRunWithJre.bat // added 
├── jre
├── licenses
├── server
└── support
```

