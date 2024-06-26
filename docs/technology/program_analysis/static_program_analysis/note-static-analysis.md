---
title: 静态分析笔记
slug: technology/program_analysis/static_program_analysis/discussion-23/
number: 23
url: https://github.com/jygzyc/notes/discussions/23
created: 2024-06-26
updated: 2024-06-26
authors: [jygzyc]
categories: 
  - 0105-程序分析
labels: ['010501-静态程序分析']
comments: true
---

<!-- note_static_analysis -->

> 本文是基于南京大学《软件分析》课程的个人笔记[^1][^2]，仅供自用

## 一、程序的表示

### 1 概述

- Definition 1.1:  **静态分析（Static Analysis）** 是指在实际运行程序 $P$ 之前，通过分析静态程序 $P$ 本身来推测程序的行为，并判断程序是否满足某些特定的 性质（Property） $Q$

> Rice定理（Rice Theorem）：对于使用 递归可枚举（Recursively Enumerable） 的语言描述的程序，其任何 非平凡（Non-trivial） 的性质都是无法完美确定的。

由上可知不存在完美的程序分析，要么满足完全性（Soundness），要么满足正确性（Completeness）。Sound 的静态分析保证了完全性，妥协了正确性，会过近似（Overapproximate）程序的行为，因此会出现假阳性（False Positive）的现象，即误报问题。现实世界中，Sound的静态分析居多，因为误报可以被暴力排查，而Complete的静态分析存在漏报，很难排查。

![note_static_analysis-001.jpg](https://bucket.lilac.fun/2024/06/note_static_analysis-001.jpg)

Static Analysis: ensure (or get close to) soundness, while making good trade-offs between analysis precision and analysis speed.

两个词概括静态分析：抽象，过近似

过近似上文已经提到过了，这里说明一下抽象，即将具体值转化为符号值。例如将如下表左侧具体值转化为右侧抽象符号

| 具体值 | 抽象值 |
| :---: | :---: | 
| v = 1000 | + |
| v = -1 | - |
| v = 0 | 0 | 
| v = x ? 1 : -1 | （丅）unknown | 
| v = w / 0 | （丄）undefined | 

接下来就可以设计转移方程（ Transfer functions），即在抽象值上的操作

![note_static_analysis-002.png](https://bucket.lilac.fun/2024/06/note_static_analysis-002.png)

再看一个例子，体会一下 Sound 的，过近似的分析原则：

```bash
x = 1;
if input then
    y = 10;
else
    y = -1;
z = x + y;
```

我们会发现，在进入 2-5 行的条件语句的时候， $y$ 的值可能为 $10$ ，也可能为 $-1$ ，于是，我们最终会认为y的抽象值为 $\top$ ，最终 $z$ 的抽象值也就为 $\top$ ，这样，我们的分析就是尽可能全面的，虽然它并不精确。

### 2 中间表示

![note_static_analysis-003.jpg](https://bucket.lilac.fun/2024/06/note_static_analysis-003.jpg)

静态分析一般发生在 IR 层

考虑下面一小段代码：

```bash
do i = i + 1; while (a[i] < v);
```

![note_static_analysis-004.jpg](https://bucket.lilac.fun/2024/06/note_static_analysis-004.jpg)

## 二、数据流分析与应用

## 三、指针分析与应用

## 四、技术拓展

> TODO

- [^1]: [南京大学《软件分析》课程](https://www.bilibili.com/video/BV1b7411K7P4)
- [^2]: [静态分析：基于南京大学软件分析课程的静态分析基础教程](https://static-analysis.cuijiacai.com/01-intro/)