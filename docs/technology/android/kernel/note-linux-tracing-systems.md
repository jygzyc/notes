---
title: Linux内核监控与攻防应用笔记
slug: technology/android/kernel/discussion-18/
url: https://github.com/jygzyc/notes/discussions/18
date: 2024-05-30
authors: [jygzyc]
categories: 
  - 0101-Android
labels: ['010104-Kernel']
comments: true
---

<!-- note_linux_tracing_systems -->

## Kernel Tracing System 101

之前听说过很多内核中的监控方案，包括 strace，ltrace，kprobes，jprobe、uprobe、eBPF、tracefs、systemtab 等等，到底他们之间的的关系是什么，分别都有什么用呢。以及他们后续能否被用来作为攻防的输入。根据这篇文章[^1]中的介绍，我们可以将其分为三个部分：

- 数据源: 根据监控数据的来源划分，包括探针和断点两类
- 采集机制: 根据内核提供给用户态的原始事件回调接口进行划分
- 前端: 获取和解析监控事件数据的用户工具

![Fig1](https://raw.githubusercontent.com/jygzyc/notes-images/main/blog/note_linux_tracing_systems-2024-05-30-23-38-41.png)

在开始介绍之前，先来看看我们能在内核监控到什么？

- 系统调用
- Linux 内核函数调用（例如，TCP 堆栈中的哪些函数正在被调用？）
- 用户空间函数调用（`malloc` 是否被调用？）
- 用户空间或内核中的自定义“**事件**”

以上这些都是可能实现的，但是事实上追踪这些也是非常复杂的，下面就来一一进行说明。

### Data source：kprobe

简单来说，kprobe 可以实现动态内核的注入，基于中断的方法在任意指令中插入追踪代码，并且通过 pre_handler/post_handler/fault_handler 去接收回调。


[^1]: [Linux tracing systems & how they fit together](https://jvns.ca/blog/2017/07/05/linux-tracing-systems/)
[^2]: [Linux 内核监控在 Android 攻防中的应用](https://evilpan.com/2022/01/03/kernel-tracing/)
  
<script src="https://giscus.app/client.js"
    data-repo="jygzyc/notes"
    data-repo-id="R_kgDOJrOxMQ"
    data-mapping="number"
    data-term="18"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="top"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    crossorigin="anonymous"
    async>
</script>
