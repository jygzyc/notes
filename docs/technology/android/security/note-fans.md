---
title: FANS：Fuzzing Android Native System Services via Automated Interface Analysis 笔记
slug: technology/android/security/discussion-24/
number: 24
url: https://github.com/jygzyc/notes/discussions/24
created: 2024-07-02
updated: 2024-07-04
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

- 本文提出了一种基于自动化生成的模糊测试解决方案 FANS[^2] ，用于发现 Android 原生系统服务中的漏洞。FANS 首先收集目标服务中的所有接口，并发现深层嵌套的多层接口以进行测试。然后，它自动从目标接口的抽象语法树（AST）中提取接口模型，包括可行的事务代码、事务数据中的变量名称和类型。此外，它通过变量名称和类型知识推断 transactions 中的变量依赖性，并通过生成和使用关系推断接口依赖性。最后，它使用接口模型和依赖知识生成具有有效格式和语义的事务序列，以测试目标服务的接口。

## 设计

![note_fans-001](https://bucket.lilac.fun/2024/07/note_fans-001.png)

上图展示了我们的解决方案FANS的设计概述。首先， _接口收集器_ (原文3.3节)收集目标服务中的所有接口，包括顶级接口和多级接口。然后 _接口模型提取器_ (原文3.4节)为这些接口中的每个候选事务提取输入和输出格式以及变量语义，即变量名和类型。提取器还收集与变量相关的结构、枚举和类型别名的定义。接下来，_依赖推断器_ (原文3.5节)推断接口依赖，以及事务内和事务间变量依赖。最后，基于上述信息，_fuzzer引擎_ (原文3.6节)随机生成事务，并调用相应的接口来fuzz本地系统服务。fuzzer引擎还有一个 _管理器_ ，负责同步主机和被测手机之间的数据。

### 接口收集器

顶层或多层接口都有分派事务的`onTransact`方法。因此，我们可以利用这个特性来识别接口。不过，我们并不直接扫描AOSP代码库中的 C/C++ 文件来获取`onTransact`方法。相反，我们检查在 AOSP 编译命令中作为源出现的每个 C/C++ 文件，以便我们可以收集在编译期间由AIDL工具动态生成的接口，否则这些接口将被忽略。

### 接口模型提取器

#### Design Choices

- 从服务端代码提取：在 Android 中，客户端应用程序通过 RPC 接口 `transact` 调用目标事务，服务端使用 `onTransact` 方法处理 RPC。利用这个我们可以提取所有可能的transactions，使用服务端分析更加准确

- 从AST表示中提取：先将AIDL文件转为 C++ 文件（单纯分析AIDL漏 C++ 信息，且现有AIDL to C++ 工具；当然也可以转化为IR），然后使用AST提取接口模型（能够保留原始类型）

#### Transaction Code Identification

`onTransact`函数通过控制流分派指定处理的事务与对应`code`，编译后常转变为`switch-case`形式，通过 AST 识别`case`节点，就可以轻松的分析出接口的所有事务，并识别出相关的常量transaction `code`

#### Input and Output Variable Extraction

识别出事务codes以后，需要提取每一个transaction反序列化输入中的 `data` parcel数据。此外，由于我们想推断事务的内部依赖，我们也需要提取事务的输出，即序列化的`reply` parcel 数据

事务中使用的变量有三种可能的类别：

- Sequential Variables。这种类型的变量没有任何前提条件
- Conditional Variables。这种类型的变量取决于一些条件。如果不满足这些条件，变量可能为空，或者不出现在数据中，甚至与满足条件时的类型不同
- Loop Variables。这种类型的变量在循环甚至嵌套循环中被反序列化

这三类变量恰好对应程序中的三类语句，即顺序语句、条件语句和循环语句。因此，我们将主要在AST中处理这类语句。

- 顺序语句：下面是主要 7 种顺序语句

```c++
// checkInterface
CHECK_INTERFACE(IMediaExtractorService, data, reply);
// readXXX
String16 opPackageName = dara.readString16();
pid_t pid = data.readInt32();
// read(a, sizeof(a) * num)
effect_descriptor_t desc = [];
data.read(&desc, sizeof(desc));
// read(a)
Rect sourceCrop(Rect::EMPTY_RECT);
data.read(sourceCrop);
// readFromParcel
aaudio::AAudioStreamRequest request;
request.readFromParcel(&data);
// callLocal
callLocal(data, reply, &ISurfaceComposerClient::createSurface);
// function call
setSchedPolicy(data);
```

- 条件语句：形式较多，包括`switch`和`if`语句等，下面展示了`if`语句的一种情况

```c++
int32_t isFdValid = data.readInt32();
int fd = -1;
if (isFdValid) {
    fd = data.readFileDescriptor();
}
```

- 循环语句：形式较多，例如`while`和`for`语句等，以下以`for`语句案例为例，我们将会记录`key`读取的次数，并将`key`，`fd`，`value`作为Loop Variables

```c++
const int size = data.readInt32();
for(int index = 0; index < size; ++index){
    ...
    const String8 key(data.readString8());
    if(key == String8("FileDescriptorKey")){
        ...
        int fd = data.readFileDescriptor();
        ...
    } else {
        const String8 value(data.readString8());
        ...
    }
}
```

- 返回语句：当一条路径返回错误代码时，其存在漏洞的概率就会减小，生成测试用例也会更少。以如下代码为例，生成时`numBytes`尽量不要大于`MAX_BINDER_TRANSACTION_SIZE`

```c++
const uint32_t numBytes = data.readInt32();
if(numBytes > MAX_BINDER_TRANSACTION_SIZE){
    reply->writeInt32(BAD_VALUE);
    return DRM_NO_ERROR;
}
```

#### Type Definition Extraction

除了提取事务中的输入和输出变量，我们还提取类型定义。它有助于丰富变量语义，以便生成更好的输入。有三种类型需要分析:

- Structure-like Definition：这种类型包括联合和结构
- Enumeration Definition：提取所有给定的(常量)枚举值
- Type Alias：`typedef`语句

### 依赖推断器

提取接口模型后，我们推断出两种依赖关系：（1）接口依赖关系。即如何识别并生成多级接口。它还暗示了一个接口如何被其他接口使用。 (2)变量依赖。事务中的变量之间存在依赖关系。以前的研究很少考虑这些依赖性



## 实现




[^1]: [FANS: Fuzzing Android Native System Services via Automated Interface Analysis](https://www.usenix.org/conference/usenixsecurity20/presentation/liu)
[^2]: [Github: FANS: Fuzzing Android Native System Services](https://github.com/iromise/fans)
