---
title: FANS：Fuzzing Android Native System Services via Automated Interface Analysis 笔记
slug: blog/discussion-24/
number: 24
url: https://github.com/jygzyc/notes/discussions/24
date:
  created: 2024-07-02
  updated: 2024-07-31
created: 2024-07-02
updated: 2024-07-31
authors: [ecool]
categories: ['论文笔记']
comments: true
---

<!-- note_fans -->

本文提出了一种基于自动化生成的模糊测试解决方案 FANS[^2] ，用于发现 Android 原生系统服务中的漏洞。FANS 首先收集目标服务中的所有接口，并发现深层嵌套的多层接口以进行测试。然后，它自动从目标接口的抽象语法树（AST）中提取接口模型，包括可行的事务代码、事务数据中的变量名称和类型。此外，它通过变量名称和类型知识推断 transactions 中的变量依赖性，并通过生成和使用关系推断接口依赖性。最后，它使用接口模型和依赖知识生成具有有效格式和语义的事务序列，以测试目标服务的接口。

<!-- more -->

## 摘要[^1]

将Fuzzing技术应用到Android Native system services 面临的问题有：

- android native系统服务通过特殊的进程间通信（IPC）机制，即binder，通过特定服务的接口被调用。因此Fuzzer 需要辨识所有接口，自动化地生成特定接口的测试用例
- 有效的测试用例应该满足每个接口的接口模型
- 测试用例也应该满足语义要求，包括变量依赖和接口依赖

本文研究内容如上述摘要所示：

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

![note_fans-003.png](https://bucket.lilac.fun/2024/07/note_fans-003.png)

### 依赖推断器

提取接口模型后，我们推断出两种依赖关系：

1. 接口依赖。即如何识别并生成多级接口，这还暗示了一个接口如何被其他接口调用
2. 变量依赖。事务中的变量之间存在依赖关系。以前的研究很少考虑这些依赖性

#### Interface Dependency

一般来说，接口之间有两种依赖关系，分别对应接口的生成和使用

- **生成依赖**。如果一个接口可以通过另一个接口检索到，我们可以说这两个接口之间存在生成依赖性。我们可以直接从服务管理器获取Android原生系统服务接口，即顶级接口（服务对象）。关于多级接口，我们发现上级接口会调用`writeStrongBinder`来序列化一个深层接口到`reply`中。通过这种方式，我们可以轻松地收集所有接口的生成依赖性

- **使用依赖**。如果一个接口被另一个接口使用，我们就说这两个接口之间存在使用依赖。我们发现，当接口A被另一个接口B使用时，B会调用`readStrongBinder`从数据包中反序列化A。因此，我们可以利用这种模式来推断使用依赖性

#### Variable Dependency

根据变量对是否在同一个事务中，存在两种类型的变量依赖关系，即事务内依赖关系和事务间依赖关系

- **事务内依赖**。在同一事务中，一个变量有时依赖于另一个变量。如[Input and Output Variable Extraction](#input-and-output-variable-extraction)一节所演示的，事务中的变量之间可能存在条件依赖、循环依赖和数组大小依赖。条件依赖是指一个变量的值决定另一个变量是否存在的情况。例如，条件语句示例代码中的`fd`条件性地依赖于`isFdValid`。循环依赖是指一个变量决定另一个变量被读取或写入的次数，如循环语句示例代码中的变量`size`和`key`。对于最后一个，当数组变量的大小由另一个变量指定。在生成这个数组变量时，应该指定大小。

- **事务间依赖**。一个变量有时依赖于不同事务中的另一个变量。换句话说，一个transaction中的输入可以通过另一个transaction中的输出来获得。我们提出下图中算法 1 来处理这种依赖性。
 ① 一个变量为输入，另一个为输出；② 这两个变量位于不同的事务中； ③ 输入变量的类型等于输出变量的类型；④ 要么输入变量类型是复杂的（不是原始类型），要么输入变量名和输出变量名相似。相似度度量算法可定制化处理

![note_fans-002.png](https://bucket.lilac.fun/2024/07/note_fans-002.png)

### Fuzzer 引擎

首先，fuzzer管理器会将fuzzer程序的二进制文件、接口模型和依赖同步到手机上，并在手机上启动fuzzer。然后Fuzzer将生成一个测试用例，即一个transaction及其相应的接口来模糊测试远程代码。同时，fuzzer管理器将定期同步手机上的崩溃日志。

## 实现

### 接口收集器

Python实现[接口收集器](#_3)与[Input and Output Variable Extraction](#input-and-output-variable-extraction)一节中提到的内容

### 接口模型提取器

当我们从 AST 中提取接口模型时，我们首先将编译命令转换为 cc1 命令，同时链接 Clang 插件，该插件用于遍历 AST 并提取粗略的接口模型。我们对 AST 进行近似切片，只保留与输入和输出变量相关的语句，省略其他语句。最后，我们对粗略模型进行后处理，以便Fuzzer引擎可以轻松使用它。接口模型以JSON格式存储。

### 依赖推断器

如上文描述，输入原为上一步得到的JSON

### Fuzzer 引擎

实现了一个简单的Fuzzer管理器，以便在多部手机上运行fuzzer，并在主机和手机之间同步数据。我们构建了整个 AOSP，并启用了 ASan。模糊器在 C++ 中作为终端可执行文件实现。由于一些Android原生系统服务在接收 RPC 请求时会检查调用者的权限，因此模糊器是在root权限下执行的。为了加速执行，当不需要`reply`中的输出时，我们通过将`transact`的`flag`参数标记为 1 来进行异步RPC。当我们确实需要`reply`中的输出时，例如依赖推断，我们会进行同步调用。最后，为了分析触发的崩溃，我们使用Android内置的 logcat 工具进行日志记录。此外，我们还将记录位于 `/data/tombstones/` 的本机崩溃日志

## 案例

> TODO：说明出现的案例

[^1]: [FANS: Fuzzing Android Native System Services via Automated Interface Analysis](https://www.usenix.org/conference/usenixsecurity20/presentation/liu)
[^2]: [Github: FANS: Fuzzing Android Native System Services](https://github.com/iromise/fans)
