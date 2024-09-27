---
title: GlobalConfusion—TrustZone Trusted Application 0-Days by Design 笔记
slug: blog/discussion-30/
number: 30
url: https://github.com/jygzyc/notes/discussions/30
date:
  created: 2024-09-24
  updated: 2024-09-27
created: 2024-09-24
updated: 2024-09-27
authors: [ecool]
categories: ['论文笔记']
comments: true
---

<!--note_globalconfusion-->

## 摘要

受信任执行环境（TEE）构成了移动设备安全架构的支柱。GlobalPlatform Internal Core API是事实上的标准，它统一了现实世界中各种实现的碎片化场景，为不同的TEE提供了兼容性。

Hexlive研究表明，这个API标准容易受到设计弱点的影响。这种弱点的表现形式导致真实世界用户空间应用程序（称为可信应用TA）中出现关键类型的混淆错误。设计弱点的核心在于一个开放式失败设计，它将对不信任数据的类型检查留给了TA开发者（这个检查是可选的）。API并不强制执行这个容易被遗忘的检查，而在大多数情况下，这会导致任意的读写利用。为了检测这些类型混淆错误，他们设计并实现了GPCheck，这是一个静态二进制分析系统，能够审查现实世界的TA。

## 简介


