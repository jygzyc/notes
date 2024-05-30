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

## Kernel Tracing 101

之前听说过很多内核中的监控方案，包括 strace，ltrace，kprobes，jprobe、uprobe、eBPF、tracefs、systemtab 等等，到底他们之间的的关系是什么，分别都有什么用呢。以及他们后续能否被用来作为攻防的输入。根据这篇文章[^1]中的介绍，我们可以将其分为三个部分：

- 数据: 根据监控数据的来源划分
- 采集: 根据内核提供给用户态的原始事件回调接口进行划分
- 前端: 获取和解析监控事件数据的用户工具




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
    data-loading="lazy"
    crossorigin="anonymous"
    async>
</script>
