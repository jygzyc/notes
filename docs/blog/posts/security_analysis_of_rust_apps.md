---
title: Rust语言应用安全性分析
slug: blog/discussion-33/
number: 33
url: https://github.com/jygzyc/notes/discussions/33
date:
  created: 2024-12-20
  updated: 2025-03-17
created: 2024-12-20
updated: 2025-03-17
authors: [yves]
categories: ['安全技术']
draft: true
comments: true
---

<!-- name: security_analysis_of_rust_apps -->

## Rust语言简介

### Rust语言简介

Rust 是由 Mozilla 主导开发的高性能编译型编程语言，遵循"安全、并发、实用"的设计原则。在过去几年中， Rust 编程语言以其独特的安全保障特性和高效的性能，成为了众多开发者和大型科技公司的新宠。许多大厂开始纷纷在自己的项目中引入 Rust ，比如 Cloudflare 的 pingora ， Android 中的 Binder 等等。[^1] [^2] [^3]

下面我们举一个例子来看看 Rust 程序

```

```

### Rust语言语法介绍



## Rust语言安全性概述

之所以人们对 Rust 那么充满兴趣，除了其强大的语法规则之外， Rust 提供了一系列的安全保障机制也让人非常感兴趣，其主要集中在以下几个方面：[^4]

- 内存安全： Rust 通过使用所有权系统和检查器等机制，解决了内存安全问题。它在编译时进行严格的借用规则检查，确保不会出现数据竞争、空指针解引用和缓冲区溢出等常见的内存错误。

- 线程安全： Rust 的并发模型使得编写线程安全的代码变得更加容易。它通过所有权和借用的机制，确保在编译时避免了数据竞争和并发问题，从而减少了运行时错误的潜在风险。

- 抽象层安全检测：Rust提供了强大的抽象能力，使得开发者能够编写更加安全和可维护的代码。通过诸如模式匹配、类型系统、trait和泛型等特性，Rust鼓励使用安全抽象来减少错误和提高代码的可读性。

Rust强大的编译器管会接管很多工作，从而尽可能的减少各种内存错误的诞生。

### 所有权系统（Ownership System）

Rust 编译器通过所有权系统跟踪每个值的所有者，确保在值被移动后原变量不可再用。编译器在类型检查阶段标记移动操作，并禁止后续使用已移动的变量。与 C++ 的 RAII 不同，Rust 的所有权规则是强制性的，任何违反规则的代码都会被拒绝。



### Rust源码解析

在具体分析Rust编译器代码前，让我们先看一下 Rust 语言的 MIR（Mid-level Intermediate Representation，中级中间表示），这是 Rust 编译器在编译过程中使用的一种中间表示形式。它介于高级抽象语法（HIR，High-level IR）和底层机器码（如 LLVM IR）之间，专门用于实现 Rust 的语义分析和优化，这和后面要讲的借用检查、生命周期验证和其他安全性相关的分析都是有关系的。

### MIR

以一个简单的函数为例，看一下源码与 MIR 之间的联系，使用`rustc --emit mir -o output.mir your_file.rs`能够将对应的Rust源码。

- 案例1：加法函数 

```rs
fn add(a: i32, b: i32) -> i32 {
    let c = a + b;
    if c > 0 {
        c
    } else {
        -c
    }
}
```

```rs
// 函数: add，下面是概念简化版本，实际情况更复杂
bb0: { // 基本块 0: 函数入口
    _3 = _1 + _2;          // _1 是 a, _2 是 b, _3 是 c（临时变量）
    _4 = _3 > 0;           // 检查 c > 0，_4 是布尔结果
    switchInt(_4) -> [true: bb1, false: bb2]; // 根据条件跳转
}

bb1: { // 基本块 1: c > 0 的分支
    _0 = _3;               // 返回值 _0 赋值为 c
    return;                // 返回
}

bb2: { // 基本块 2: c <= 0 的分支
    _0 = -_3;              // 返回值 _0 赋值为 -c
    return;                // 返回
}
```

- 案例2：简单的引用加法

```rs
fn foo(x: &i32) -> i32 {
    *x + 1
}
```

```rs
// 函数：foo，下面是真实情况生成的 MIR
fn foo(_1: &i32) -> i32 {
    debug x => _1;
    let mut _0: i32;
    let mut _2: i32;
    let mut _3: (i32, bool);

    bb0: {
        _2 = (*_1);
        _3 = CheckedAdd(_2, const 1_i32);
        assert(!move (_3.1: bool), "attempt to compute `{} + {}`, which would overflow", move _2, const 1_i32) -> [success: bb1, unwind continue];
    }

    bb1: {
        _0 = move (_3.0: i32);
        return;
    }
}
```

能看到， MIR 是基于 Basic Block 生成的，类似于 CFG 的形式，同时会去除很多高级语法糖，例如`for`循环会被展开成`while`循环，这样能够更专注于表达程序的语义，便于分析和优化。简单来说，MIR是 Rust 编译器内部用来“理解”和“加工”代码的一个桥梁。



#### 源码解析

我们在`compiler/rustc_borrowck/src/lib.rs`能找到检查的核心函数`do_mir_borrowck`,该函数通过分析 MIR，检查代码是否满足 Rust 的借用规则（例如不可变借用和可变借用的互斥性、生命周期的有效性等），并生成诊断信息或错误，函数的签名如下：

```rs
fn do_mir_borrowck<'tcx>(
    tcx: TyCtxt<'tcx>,
    input_body: &Body<'tcx>,
    input_promoted: &IndexSlice<Promoted, Body<'tcx>>,
    consumer_options: Option<ConsumerOptions>,
) -> (BorrowCheckResult<'tcx>, Option<Box<BodyWithBorrowckFacts<'tcx>>>)
```

下面分析一下这个函数是如何实现检查的，这里对关键代码进行说明

1. 初始化上下文

- 创建`BorrowckInferCtxt`推理上下文
- 处理`tainted_by_errors`标记，用于错误传播
- 收集局部变量调试信息到`local_names`，检测命名冲突

```rs
let mut local_names = IndexVec::from_elem(None, &input_body.local_decls);
for var_debug_info in &input_body.var_debug_info {
    if let VarDebugInfoContents::Place(place) = var_debug_info.value {
        if let Some(local) = place.as_local() {
            if let Some(prev_name) = local_names[local] && var_debug_info.name != prev_name {
                span_bug!(...); // 报告调试信息中的命名冲突
            }
            local_names[local] = Some(var_debug_info.name);
        }
    }
}
```

上述代码从 `var_debug_info` 中提取局部变量的名称，用于后续的错误报告和诊断。如果发现同一个局部变量有多个不同的名字，则触发编译器 bug（span_bug）

2. MIR预处理

- 克隆输入MIR主体和promoted表达式
- 用`replace_regions_in_mir`替换区域为推理变量
- 为`NLL`（非词法生命周期）分析做准备

```rs
let mut body_owned = input_body.clone();
let mut promoted = input_promoted.to_owned();
let free_regions = nll::replace_regions_in_mir(&infcx, &mut body_owned, &mut promoted);
let body = &body_owned; // no further changes
```

调用 `replace_regions_in_mir`，将 MIR 中的所有区域（region，例如生命周期）替换为新的推理变量。这是非词法生命周期（NLL，Non-Lexical Lifetimes）的基础步骤。

3. 数据流分析

- 构建`MoveData`跟踪值的移动路径
- 使用`MaybeInitializedPlaces`分析可能初始化位置
- 创建`BorrowSet`记录所有借用操作

```rs
let location_table = PoloniusLocationTable::new(body);
let move_data = MoveData::gather_moves(body, tcx, |_| true);
let flow_inits = MaybeInitializedPlaces::new(tcx, body, &move_data)
    .iterate_to_fixpoint(tcx, body, Some("borrowck"))
    .into_results_cursor(body);
let locals_are_invalidated_at_exit = tcx.hir_body_owner_kind(def).is_fn_or_closure();
let borrow_set = BorrowSet::build(tcx, body, locals_are_invalidated_at_exit, &move_data);
```

4. 计算非词法生命周期（NLL）

```rs
let nll::NllOutput { regioncx, opaque_type_values, polonius_input, polonius_output, opt_closure_req, nll_errors, polonius_diagnostics } =
    nll::compute_regions(&infcx, free_regions, body, &promoted, &location_table, flow_inits, &move_data, &borrow_set, consumer_options);
```

这里解释一下NLL，NLL（Non-Lexical Lifetimes，非词法生命周期） 是 Rust 编译器中的一个重要特性，目的是通过更精确的变量生命周期分析，放宽原有基于词法作用域（lexical scope）的借用检查规则，使 Rust 的内存安全检查更灵活，举个例子说明

```rs
fn main() {
    let mut x = 5;
    let y = &mut x; // y 的生命周期开始
    // ... 使用 y
    // 即使 y 不再被使用，其生命周期仍持续到代码块结束
} // y 的生命周期在此处结束
```

即使引用在代码块中间已不再使用，其生命周期仍延续到作用域结束，这其中可能导致不必要的借用冲突，NLL允许译器基于代码的实际控制流（而非词法作用域）判断引用的生命周期，如下所示

```rs
fn main() {
    let mut x = 5;
    let y = &mut x;  // y 的借用开始
    *y += 1;         // 最后一次使用 y
    let z = &mut x;  // NLL 允许此处借用：y 已不再使用
}
```

再举一个例子，NLL会识别单次循环中`item`的生命周期仅在单次循环内，允许安全借用

```rs
let mut data = vec![1, 2, 3];
for i in 0..data.len() {
    let item = &mut data[i]; // 旧版本会报错：多次可变借用
    *item += 1;
}
```

5. 





#### 实际案例

- 借用检查 案例1：编译器检测到 `r1` 和 `r2` 冲突，报错防止数据竞争

```rs
fn main() {
    let mut s = String::from("hello");
    let r1 = &s; // 不可变借用
    let r2 = &mut s; // 可变借用
    println!("{}, {}", r1, r2); // 编译错误
}
```

```sh
#实际报错
error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable
  --> src/main.rs:20:14
   |
19 |     let r1 = &s; // 不可变借用
   |              -- immutable borrow occurs here
here
```

- 借用检查 案例2：编译器发现 `v` 在 `r` 借用期间被修改，禁止使用 `r`，避免因容器重新分配内存导致的悬垂引用

```rs
fn main() {
    let mut v = vec![1, 2, 3];
    let r = &v[0];
    v.push(4); // 修改v
    println!("{}", r); // 编译错误
}
```

```sh
#实际报错
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
  --> src/main.rs:20:5
   |
19 |     let r = &v[0];
   |              - immutable borrow occurs here
20 |     v.push(4); // 修改v
   |     ^^^^^^^^^ mutable borrow occurs here
21 |     println!("{}", r); // 编译错误
   |                    - immutable borrow later used here
```

- 


## Rust语言安全性分析



## Rust应用安全性分析

## Rust语言逆向分析



// TODO

[^1]: [The Rust Programming Language](https://doc.rust-lang.org/book/)
[^2]: [深入浅出Rust内存安全：构建更安全、高效的系统应用](https://cloud.tencent.com/developer/article/2387511)
[^3]: [Rust 教程 | 菜鸟教程](https://www.runoob.com/rust/rust-tutorial.html)
[^4]: [SDC2024 议题回顾 | Rust 的安全幻影：语言层面的约束及其局限性](https://bbs.kanxue.com/thread-284170.htm)