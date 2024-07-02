---
title: FANS: Fuzzing Android Native System Services via Automated Interface Analysis 笔记
slug: technology/android/security/discussion-24/
number: 24
url: https://github.com/jygzyc/notes/discussions/24
created: 2024-07-02
updated: 2024-07-02
authors: [jygzyc]
categories: 
  - 0101-Android
labels: ['010102-漏洞与安全']
comments: true
---

<!-- note_fans -->

## 摘要[^1]

将Fuzzing技术应用到Android Native system services 面临的问题有：

- android native系统服务通过特殊的进程间通信（IPC）机制，即binder，通过特定服务的接口被调用。因此Fuzzer 需要辨识所有接口，自动化地生成特定接口的测试用例
- 有效的测试用例应该满足每个接口的接口模型
- 测试用例也应该满足语义要求，包括变量依赖和接口依赖

本文研究内容如下：

- 本文提出了一种基于自动化生成的模糊测试解决方案 FANS[^2] ，用于发现 Android 原生系统服务中的漏洞。FANS 首先收集目标服务中的所有接口，并发现深层嵌套的多层接口以进行测试。然后，它自动从目标接口的抽象语法树（AST）中提取接口模型，包括可行的事务代码、事务数据中的变量名称和类型。此外，它通过变量名称和类型知识推断 transactions 中的变量依赖性，并通过生成和使用关系推断接口依赖性。最后，它使用接口模型和依赖知识生成具有有效格式和语义的 transactions 序列，以测试目标服务的接口。

## 设计

![note_fans-001.png](https://bucket.lilac.fun/2024/07/note_fans-001.png)

上图展示了我们的解决方案FANS的设计概述。首先，接口收集器(第3.3节)收集目标服务中的所有接口，包括顶级接口和多级接口。然后接口模型提取器(第3.4节)为这些接口中的每个候选事务提取输入和输出格式以及变量语义，即变量名和类型。提取器还收集与变量相关的结构、枚举和类型别名的定义。接下来，依赖推断器(第3.5节)推断接口依赖，以及事务内和事务间变量依赖。最后，基于上述信息，模糊引擎(第3.6节)随机生成事务，并调用相应的接口来模糊本地系统服务。fuzzer引擎还有一个管理器，负责同步主机和被测手机之间的数据。

## 实现




[^1]: [FANS: Fuzzing Android Native System Services via Automated Interface Analysis](https://www.usenix.org/conference/usenixsecurity20/presentation/liu)
[^2]: [Github: FANS: Fuzzing Android Native System Services](https://github.com/iromise/fans)
