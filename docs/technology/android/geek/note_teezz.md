---
title: TEEzz：Fuzzing Trusted Applications on COTS Android Devices 笔记
slug: technology/android/geek/discussion-27/
number: 27
url: https://github.com/jygzyc/notes/discussions/27
created: 2024-08-01
updated: 2025-03-17
authors: [jygzyc]
categories: [Android专栏]
labels: ['Android Geek']
draft: true
comments: true
---

<!-- name: note_teezz -->

安全和隐私敏感的智能手机应用程序使用可信执行环境（TEE）来保护敏感操作免受恶意代码的侵害。按照设计，TEE 拥有对整个系统的特权访问权限，但几乎无法洞察其内部运作情况。此外，现实世界的 TEE 在与可信应用程序 (TA) 通信时强制执行严格的格式和协议交互，这阻碍了有效的自动化测试。对此，开发了TEEzz，这是第一个 TEE 感知模糊测试框架，即观察TA的执行情况，推断API字段类型和消息依赖性。[^1]

<!-- more -->

## 简介



## 预处理



## 系统设计

## 实现

## 结果评估

[^1]: [TEEzz: Fuzzing Trusted Applications on COTS Android Devices](http://hexhive.epfl.ch/publications/files/23Oakland.pdf)
