---
title: Bringing Balance to the Force Dynamic Analysis of the Android Application Framework 笔记
slug: technology/android/geek/discussion-10/
number: 10
url: https://github.com/jygzyc/notes/discussions/10
created: 2024-05-21
updated: 2025-01-21
authors: [jygzyc]
categories: [Android专栏]
labels: ['Android Geek']
draft: true
comments: true
---

<!-- name: note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework -->
《Bringing Balance to the Force Dynamic Analysis of the Android Application Framework》讨论了静态代码分析在解决 Android 应用框架安全问题上的局限，并说明了动态分析对于 Android 应用框架问题检测的可行性，提出了 DYNAMO 的解决方案。[^1] [^2]

<!-- more -->

## 概述

讨论了静态代码分析在解决 Android 应用框架安全问题上的局限性。它强调了动态分析在补充静态分析以提高安全评估的准确性和完整性方面的重要性。文章介绍了名为 DYNAMO 的解决方案，该方案对四个具有代表性的文献中的使用案例进行了动态分析。通过这样做，它验证、反驳并扩展了先前的静态分析解决方案的结果。此外，通过对结果的手动调查，提供了新的见解和专家知识，这些知识对于改进应用框架的静态和动态测试具有价值。
动态分析与静态分析相结合的重要性在于：  

- 动态分析可以弥补静态分析在处理庞大且复杂代码库时的局限性。
- 动态分析有助于提高依赖静态分析结果的不同安全应用（如恶意软件分类和最小权限应用）的性能。
- 通过动态分析，可以获得关于代码行为和潜在安全问题的更深入的了解。
- 动态分析有助于发现并解决静态分析中可能遗漏的安全问题。
- 将动态分析与静态分析相结合，可以更全面地评估应用框架的安全性，从而为用户提供更安全的体验。

因此，在安全研究领域，动态分析与静态分析的结合被认为是至关重要的，这种方法可以帮助提高 Android 应用框架的安全性，保护用户的隐私数据和系统完整性。

## 背景

**Android Framework API**

所有已注册的系统服务都能够在ServiceManager类中被找到，作者基于这一事实来提取系统API的入口点。

**Binder IPC**

Binder是安卓系统特有的进程间通信机制，底层原理是使用内核内存贡献来在进程间通信。对于一些比较敏感的底层系统API，安卓系统通过Binder封装后对外提供一些High-Level的API用于调用，在调用时则会进行权限检查。

**Permission**
  
安卓的权限管理可以分为3类：

- UID/PID检查: 只有指定UID的进程才能调用特定的API。例如，可以用于仅允许系统（getCallingUid() == 1000）或同一进程（getCallingPid() == currentPid）执行特定 API
- 跨用户检查：对于使用手机分身的情况，不同分身代表不同用户，不同用户之前权限有差异
- AppOps：权限申请(如相机权限)首先需要在Manifest中静态申请，而申请完成后的权限是否能够动态的调用则由AppOps进行管理
    
高级访问控制由低级的自主访问控制（DAC）和强制访问控制（MAC）补充。DAC 使用传统的 Unix 权限（基于组和 UID）来限制应用程序沙箱和进程，例如，防止绕过服务 API 直接访问系统服务和应用程序封装的资源，如私有用户数据或设备驱动程序。从 Android 5.0 开始，完全实施的 SELinux 被用于 MAC，以加强进程的隔离性和加强系统对特权提升的防御

## 简介

### 相关工作

**Permission Mapping**

Permission Mapping即权限映射，在本文中是指将Android Framework层提供的系统API以及调用该API时所需要申请的权限建立映射。
Permission Mapping的意义有：

1. 帮助开发者编写符合最小特权原则的app
2. 可以用于恶意软件检测或者识别过量申请权限的app
3. 可以识别安卓系统中自带的权限漏洞

**Vulnerability Detection in the Security Policy**

发现系统服务内访问控制执行的差异，例如，两个具有不同安全条件的 API 导致相同的功能或数据 sink。要进行此类分析，首先需要对系统 API 的安全策略进行建模。

1. 使用预定义的授权检查列表，例如 checkPermission 和 hasUserRestriction，但需要手动增量补充此列表以定义各个 API 的安全策略。
2. 为了消除对用户定义的授权检查列表的依赖，ACMiner引入了半自动和启发式驱动的方法来构建此列表。Centaur提出了与静态分析相结合的符号执行，以发现和验证不一致性。然而，Centaur 需要访问源代码，因此不能用于封闭源代码的 OEM 镜像。 
3. 其他研究分析了保护不当的参数敏感 API。利用这些 API 会干扰系统的状态或提高调用者的权限。与不一致性检测密切相关，ARF采用了静态分析和手动代码审查技术，发现了 Android 系统服务中权限重新分配的情况，例如，一种 API 调用另一种受保护的 API，并实施比直接调用目标 API 时更宽松的权限。

**Fuzzing for Vulnerability Detection**

可以使用有故障的载荷对系统 API 进行模糊测试，可能导致权限泄漏或拒绝服务；针对系统服务中处理不当的异常进行攻击，可能导致系统崩溃；FANS针对源码中的native服务进行Fuzz

### 动机

现有的工作基本上都是基于静态分析的，而静态分析尤其固有的缺陷，比如很难处理动态变量的值、IPC等。而目前的Permission Mapping结果几乎完全基于静态分析，这导致结果的不准确性，而对其他依赖于该结果的工作造成影响。因此作者认为有必要用动态测试的方法来重新审视这个结果。

## 设计与实现

### 设计

本文想要设计一个动态测试工具来为Android Framework层API建立权限映射，主要有以下几个Research Questions:

RQ1: 如何识别这些API的入口并触发它们。难点在于这些API分散在不同的Service之中，并且可能分别由Java或者Native代码实现。  
RQ2: 如何为这些API构建输入。  
RQ3: 如何衡量动态测试的覆盖率。  
RQ4: 如何检测出不同类型的权限管理。有些是集中管理的很好识别，有些代码甚至是inline的，不容易发现。  
RQ5: 如何构建反馈通道。即怎样将某个API的测试结果反馈给Fuzzer  
RQ6: 如何保留不同权限检查之间的关系和顺序。  

### 实现

DYNAMO 是一种灰盒测试解决方案，分为两个阶段来构建 API 的安全策略。第一阶段专注于通过运行不同输入集来测试 API，以提高代码覆盖率。在第二阶段，根据预定义的关联规则分析第一阶段的结果，以建模目标 API 的安全策略。下图展示了 DYNAMO 主要组件的概述以及针对单个 API 执行一次测试迭代的后序执行步骤。

*Testing Service*（TS）作为一个应用程序组件分发，安装在要测试的设备上。它负责生成输入，调用目标 API，并报告调用结果。

*Instrumentation Server*（IS）是一个后台进程，当前版本本质是 Frida-server，负责构建反馈通道，报告hook信息和调用栈。

*Testing Manager*（TM）的请求下还负责在运行时修改方法的行为。当前版本本质是 Frida Client，发送给TS进行API调用，并接收由IS中收集到的调用结果反馈，通过Analyser Module来分析覆盖率情况，控制当前的测试状态。

![note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework-01.png](https://bucket.lilac.fun/2024/06/note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework-01.png)

**Collecting Public APIs（RQ1）**

利用ServiceManager会维护所有注册的系统Service的这一事实，利用Java反射来从ServiceManager中获取所有能够找到的Service的Handle，并将其强转为对应Service的Proxy对象，在这些对象中就能找到这个Service的所有API的方法签名了

在测试这些API时，作者采用多台设备并行的方式进行，每台设备一次只测试一个API。

**Generating Input（RQ2）**

从API中提取签名后，会分配一个简短的预定义种子值列表，对于参数，分为两种类型处理，基本 Android 类型（如 Intent 和 URI）和复杂类型（如事件监听器和位图），基本类型可以由预定义的种子生成。而对于复杂类型，在 TS 端使用递归的方式构造，通过为其传入基本类型来调用其构造函数从而生成输入。

**Measuring Coverage（RQ3）**

作者使用了一个叫WALA的工具，来对每个API进行可达性分析，对于每个API可以得到一个有限的方法集合，调用API可以最终到达这些方法。通过Hook这些方法，当其被调用时打印调用栈，如果确实是由该API所触发并且调用者为TS时(用于排除噪声)，统计该Trace。最后覆盖率的计算公式为Unique Trace的数量比上集合中的方法数量。

**DYNAMO’s Testing Strategies (RQ4)**

对于如何检测不同类型的权限检测的问题(RQ4)，作者预定义了多种测试策略，每种策略旨在发现不同类型的安全检测。工作流程大致如下：

![note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework-02.png](https://bucket.lilac.fun/2024/06/note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework-02.png)

> 例如，一种策略可以专注于发现权限，而另一种策略则检测对调用方UID和PID的检查。每个策略都从一个由预定义种子生成的输入集列表开始，所有策略都采用相同的列表。对于每种策略，DYNAMO都会执行每一个输入集，并在安全检查失败时进行检测。当报告安全检查时，它们会在同一输入集的下一次迭代中反馈，DYNAMO指示IS绕过失败的检查，以检测同一执行路径上的其他检查。重复此过程，直到没有进一步的安全检查报告为止。所有策略结束后，TM将当前API标记为完成，并继续下一个待测试的API。通过这种反馈驱动的测试，DYNAMO探索了几个调用方上下文（即第三方应用程序、特权应用程序等），以触发和检测安全检查

作者举了一个例子来帮助理解，以AccessibilityManagerService的addClient API的简化版本为例

![note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework-03.png](https://bucket.lilac.fun/2024/06/note_bringing_balance_to_the_force_dynamic_analysis_of_the_android_application_framework-03.png)


若要执行此API，调用方必须符合以下条件之一：  
1）调用方必须在等于0或1000的UID下运行（第9行）。  
2） 调用程序必须在userId等于API第二个输入参数的上下文中运行（第13行）。  
3） 呼叫者必须被授予`INTERACT_ACROSS_USERS`（ACU）权限（第16行）。  
如果这些条件都不满足，就会引发`SecurityException`（第25行）。为了简化这个例子，我们只定义了一组由null和10组成的输入，分别作为第一和第二参数。在这个例子中选择10不是任意的，因为它对应于次要配置文件的userId（而0是主要配置文件的用户Id）。使用来自主配置文件和非特权上下文的这组输入调用API将导致调用方收到`SecurityException`，因为以上条件都不符合。

对于特定权限检查的情况(图中INTERACT_ACROSS_USERS)会有统一的函数完成(checkPermission函数)，通过hook就能知道是否触发了这种检查以及具体的参数类型。

对于inline检查UID的情况，作者通过Hook Binder.getCallingUid函数来不断变更自己的UID，如果发现某一次变更后通过了权限检查，则说明存在inline UID检查

**Instrumenting Targets（RQ5）**

作者使用了Frida动态Hook框架优点是能够兼容不同的系统，而无需修改安卓源码，能够满足对一些闭源的OEM厂商的测试需求。

**Modeling of Permission Mapping（RQ6）**

作者想要得到上图中List2中的结果作为输出，这可以使用RQ4中的方法来得到具体UID值的检查以及具体权限检查的两种情况，但是对于UID是否等于入参的情况，作者通过不断变更入参的方式来检查。

## 代码分析

从Github项目可以看到DYNAMO的源码[^3]

[^1]: [*Bringing Balance to the Force Dynamic Analysis of the Android Application Framework*](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_2B-1_23106_paper.pdf)

[^2]: [论文笔记:《Bringing Balance to the Force Dynamic Analysis of the Android Application Framework》](https://ashenone66.cn/2022/03/03/lun-wen-bi-ji-bringing-balance-to-the-force-dynamic-analysis-of-the-android-application-framework/)

[^3]: [Github - abdawoud/Dynamo](https://github.com/abdawoud/Dynamo)