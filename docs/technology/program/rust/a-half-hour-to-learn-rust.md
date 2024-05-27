---
title: 半小时学习Rust
slug: technology/program/rustdiscussion-8/
url: https://github.com/jygzyc/notes/discussions/8
date: 2024-04-19
authors: [jygzyc]
categories: 
  - 0102-编程
labels: ['010204-Rust']
comments: true
---

<!-- a-half-hour-to-learn-rust -->
> 个人笔记：为了理解rust，添加了一些tip

为了提高编程语言的流畅性，人们必须阅读大量编程语言的相关知识。但如果你不知道它的含义，你怎么能读这么多呢？
在本文中，我不会专注于一两个概念，而是尝试尽可能多地浏览 Rust 片段，并解释它们包含的关键字和符号的含义。
准备好了吗？冲！[^1] [^2] （根据情况更新笔记）

`let`引入了一个变量绑定：

```rust
let x; // 声明 "x"
x = 42; // 将 42 分配给“x”
```

也可以写成一行：

```rust
let x = 42;
```

您可以使用`:`显式地指定变量的类型，这是类型注解：

```rust
let x: i32; // `i32` 是一个有符号的 32 位整数
x = 42;
// 有 i8、i16、i32、i64、i128 表示其他位数的有符号整数
// 还有 u8、u16、u32、u64、u128 表示无符号整数
```

这也可以写成一行：

```rust
let x: i32 = 42;
```

如果您声明一个变量并稍后对其进行初始化，在初始化之前编译器将阻止您使用它。

```rust
let x;
foobar(x); // error: borrow of possibly-uninitialized variable: `x`
x = 42;
```

下面这样做是完全没问题的：

```rust
let x;
x = 42;
foobar(x); // `x` 的类型可以推断出来
```

下划线`_`是一个特殊名称——或者更确切地说，是“缺乏名称”。`_`基本上意味着扔掉一些东西：

```rust
// *什么也没做*，因为 42 是一个常数
let _ = 42;

// 这调用了 `get_thing` 但丢弃了它的结果
let _ = get_thing();
```

以下划线“开头”的名称是常规名称，有一点特殊的是，编译器不会警告它们未被使用

```rust
// 我们最终可能会使用 `_x`，但我们的代码仍在编写中
// 我们现在只想摆脱编译器的警告。
let _x = 42；
```

可以引入具有相同名称的单独绑定，它会“隐藏”前一个变量绑定：

```rust
let x = 13;
let x = x + 3;
// 该行之后使用“x”仅引用第二个“x”，
// 第一个“x”不再存在。
```

Rust 有`tuple`——元组类型，您可以将其视为“固定长度的不同类型的集合”。

```rust
let pair = ('a', 17);
pair.0; // this is 'a'
pair.1; // this is 17
```

如果我们真的想给元组中变量增加类型注解，可以用`pair`：

```rust
let pair: (char, i32) = ('a', 17);
```

元组可以通过赋值的方式被“解构”(destructured)，这意味着它们被分解为各自的字段：

```rust
let (some_char, some_int) = ('a', 17);
// 现在，`some_char` 是 'a'，`some_int` 是 17
```

当函数返回元组类型时特别管用：

```rust
let (left, right) = slice.split_at(middle);
```

当然，在解构一个元组时，可以用 `_` 舍弃掉一部分字段：

```rust
let (_, right) = slice.split_at(middle);
```

分号表示语句的结尾：

```rust
let x = 3;
let y = 5;
let z = y + x;
```

这意味着语句可以写成多行：

```rust
let x = vec![1, 2, 3, 4, 5, 6, 7, 8]
    .iter()
    .map(|x| x + 3)
    .fold(0, |x, y| x + y);
```

（我们稍后会讨论这些代码的实际含义）。

`fn`用来声明一个函数。

下面是一个 void 函数：

```rust
fn greet() {
    println!("Hi there!");
}
```

下面是一个返回 32 位有符号整数的函数。使用箭头指示其返回类型：

```rust
fn fair_dice_roll() -> i32 {
    4
}
```

一对大括号声明一个块，它有自己的作用域：

```rust
// 这首先会打印“in”，然后是“out”
fn main() {
    let x = "out";
    {
        // 这是一个不同的“x”
        let x = "in";
        println!("{}", x);
    }
    println!("{}", x);
}
```

“块”也是表达式，意味着它们的计算结果为一个值。

```rust
// 这条语句
let x = 42;

// 和这条语句等价
let x = { 42 };
```

在一个块中，可以有多条语句：

```rust
let x = {
    let y = 1; // 第一个声明
    let z = 2; // 第二个声明
    y + z // 这是 *结尾*，即整个块的计算结果
};
```

这就是为什么“省略函数末尾的分号”与“返回这个值”相同，即，下面的两个函数是等效的：

```rust
fn fair_dice_roll() -> i32 {
    return 4;
}

fn fair_dice_roll() -> i32 {
    4
}
```

`if` 条件也可以是表达式：

```rust
fn fair_dice_roll() -> i32 {
    if feeling_lucky {
        6
    } else {
        4
    }
}
```

`match` 也是一个表达式：

```rust
fn fair_dice_roll() -> i32 {
    match feeling_lucky {
        true => 6,
        false => 4,
    }
}
```

“点”`.`通常用于访问值的字段：

```rust
let a = (10, 20);
a.0; // this is 10

let amos = get_some_struct();
amos.nickname; // this is "fasterthanlime"
```

或者调用方法：

```rust
let nick = "fasterthanlime";
nick.len(); // this is 14
```

“双冒号”`::`与此类似，但它的操作对象是命名空间。
在此示例中，`std`是一个 crate（相当于一个库），`cmp`是一个模块（相当于一个源文件），`min`是一个函数：  

```rust
let least = std::cmp::min(3, 8); // this is 3
```

`use`指令可用于将其他命名空间名称引入到当前：

```rust
use std::cmp::min;

let least = min(7, 1); // this is 1
```

在`use`指令中，大括号还有另一个含义：它们是一组名称（`glob`）。如果我们想用`use`同时导入`min`和`max`，那么可以： 

```rust
// this works:
use std::cmp::min;
use std::cmp::max;

// this also works:
use std::cmp::{min, max};

// this also works!
use std::{cmp::min, cmp::max};
```

通配符 `*` 允许您导入命名空间下所有名称：

```rust
// 这不仅将“min”和“max”引入代码中，而且并包括模块中的其他名称
use std::cmp::*;
```

类型也是命名空间，方法可以作为常规函数调用：

```rust
let x = "amos".len(); // this is 4
let x = str::len("amos"); // this is also 4
```

`str`是基本类型(primitive type)，但默认命名空间下也有许多非基本类型。

```rust
// `Vec` 是一个常规结构，而不是原始类型
let v = Vec::new();

// 这是和上述完全等价的代码，但具有访问到“Vec”的*完整*路径
let v = std::vec::Vec::new();
```

这是因为 Rust 会在每个模块的开头插入它：

```rust
use std::prelude::v1::*;
```

（这反过来又会导入其他许多符号，如`Vec`、`String`、`Option`和`Result`）。

结构体使用`struct`关键字声明：

```rust
struct Vec2 {
    x: f64, // 64 位浮点，又名“双精度”
    y: f64,
}
```

它们可以使用“结构体文字”进行初始化：

```rust
let v1 = Vec2 { x: 1.0, y: 3.0 };
let v2 = Vec2 { y: 2.0, x: 4.0 };
// the order does not matter, only the names do
```

有一个快捷方式可以从另一个结构体初始化剩余字段：

```rust
let v3 = Vec2 {
    x: 14.0,
    ..v2
};
```

这被称为“结构更新语法”（struct update syntax），只能发生在最后一个位置，并且不能后跟逗号。
请注意，“剩余字段”可以是“所有字段”：

```rust
let v4 = Vec2 { ..v3 };
```

结构体和元组一样，可以被解构。
下面是一个有效的`let`模式：

```rust
let (left, right) = slice.split_at(middle);
```

也可以这样：

```rust
let v = Vec2 { x: 3.0, y: 6.0 };
let Vec2 { x, y } = v;
// `x` is now 3.0, `y` is now `6.0`
```

还有这个：

```rust
let Vec2 { x, .. } = v;
// this throws away `v.y`
```

`let`模式可以用作`if`中的条件：

```rust
struct Number {
    odd: bool,
    value: i32,
}

fn main() {
    let one = Number { odd: true, value: 1 };
    let two = Number { odd: false, value: 2 };
    print_number(one);
    print_number(two);
}

fn print_number(n: Number) {
    if let Number { odd: true, value } = n {
        println!("Odd number: {}", value);
    } else if let Number { odd: false, value } = n {
        println!("Even number: {}", value);
    }
}

// this prints:
// Odd number: 1
// Even number: 2
```

`match`匹配也是一种模式，就像`if let`:

```rust
fn print_number(n: Number) {
    match n {
        Number { odd: true, value } => println!("Odd number: {}", value),
        Number { odd: false, value } => println!("Even number: {}", value),
    }
}

// this prints the same as before
```

`match`必须是详尽的，至少需要一个分支来进行匹配

```rust
fn print_number(n: Number) {
    match n {
        Number { value: 1, .. } => println!("One"),
        Number { value: 2, .. } => println!("Two"),
        Number { value, .. } => println!("{}", value),
        // if that last arm didn't exist, we would get a compile-time error
    }
}
```

如果这很麻烦，可以用`_`来匹配所有模式：

```rust
fn print_number(n: Number) {
    match n.value {
        1 => println!("One"),
        2 => println!("Two"),
        _ => println!("{}", n.value),
    }
}
```

您可以在自己的类型上声明方法：

```rust
struct Number {
    odd: bool,
    value: i32,
}

impl Number {
    fn is_strictly_positive(self) -> bool {
        self.value > 0
    }
}
```

并像往常一样使用它们：

```rust
fn main() {
    let minus_two = Number {
        odd: false,
        value: -2,
    };
    println!("positive? {}", minus_two.is_strictly_positive());
    // this prints "positive? false"
}
```

默认情况下，变量绑定是不可变的，这意味着它的变量值不能改变：

```rust
fn main() {
    let n = Number {
        odd: true,
        value: 17,
    };
    n.odd = false; // error: cannot assign to `n.odd`,
                   // as `n` is not declared to be mutable
}
```

而且它们不能被赋值更改：

```rust
fn main() {
    let n = Number {
        odd: true,
        value: 17,
    };
    n = Number {
        odd: false,
        value: 22,
    }; // error: cannot assign twice to immutable variable `n`
}
```

`mut`允许变量绑定可更改：

```rust
fn main() {
    let mut n = Number {
        odd: true,
        value: 17,
    }
    n.value = 19; // all good
}
```

`trait`是多种类型拥有的共同点：

```rust
trait Signed {
    fn is_strictly_negative(self) -> bool;
}
```

您可以实现：

- 为任意类型实现你自己定义的trait
- 为你的类型实现任意类型的trait
- 不允许为别人的类型实现别人的trait

这些被称为“孤立规则”(orphan rules)。

下面是自定义trait在自定义类型上的实现：

```rust
impl Signed for Number {
    fn is_strictly_negative(self) -> bool {
        self.value < 0
    }
}

fn main() {
    let n = Number { odd: false, value: -44 };
    println!("{}", n.is_strictly_negative()); // prints "true"
}
```

我们在外部类型（甚至是基本类型）上的实现的自定义trait：

```rust
impl Signed for i32 {
    fn is_strictly_negative(self) -> bool {
        self < 0
    }
}

fn main() {
    let n: i32 = -44;
    println!("{}", n.is_strictly_negative()); // prints "true"
}
```

自定义类型的外部trait：

```rust
// `Neg` 特性用于重载 `-`，
// 一元减运算符。
impl std::ops::Neg for Number {
    type Output = Number;

    fn neg(self) -> Number {
        Number {
            value: -self.value,
            odd: self.odd,
        }        
    }
}

fn main() {
    let n = Number { odd: true, value: 987 };
    let m = -n; // this is only possible because we implemented `Neg`
    println!("{}", m.value); // prints "-987"
}
```

`impl`块总是用来为类型实现方法，因此，在该块内，`Self`可以指代该类型:

```rust
impl std::ops::Neg for Number {
    type Output = Self;

    fn neg(self) -> Self {
        Self {
            value: -self.value,
            odd: self.odd,
        }        
    }
}
```

有些trait是“标记”——它们并不是说类型实现了某些方法，而是说可以用类型完成某些事情。
例如`i32`实现`Copy` trait(简单地讲，`i32`是可复制的)，所以下面的代码工作正常:

```rust
fn main() {
    let a: i32 = 15;
    let b = a; // `a` is copied
    let c = a; // `a` is copied again
}
```

这也是正常的：

```rust
fn print_i32(x: i32) {
    println!("x = {}", x);
}

fn main() {
    let a: i32 = 15;
    print_i32(a); // `a` is copied
    print_i32(a); // `a` is copied again
}
```

但`Number`类型没有实现`Copy`，所以下面的代码不起作用：

```rust
fn main() {
    let n = Number { odd: true, value: 51 };
    let m = n; // `n` is moved into `m`
    let o = n; // error: use of moved value: `n`
}
```

这也不行：

```rust
fn print_number(n: Number) {
    println!("{} number {}", if n.odd { "odd" } else { "even" }, n.value);
}

fn main() {
    let n = Number { odd: true, value: 51 };
    print_number(n); // `n` is moved
    print_number(n); // error: use of moved value: `n`
}
```

但如果采用不可变的引用`print_number`，就是可行的：

```rust
fn print_number(n: &Number) {
    println!("{} number {}", if n.odd { "odd" } else { "even" }, n.value);
}

fn main() {
    let n = Number { odd: true, value: 51 };
    print_number(&n); // `n` is borrowed for the time of the call
    print_number(&n); // `n` is borrowed again
}
```

如果变量被声明为可变的，则函数参数使用可变引用也可以工作:

```rust
fn invert(n: &mut Number) {
    n.value = -n.value;
}
fn print_number(n: &Number) {
    println!("{} number {}", if n.odd { "odd" } else { "even" }, n.value);
}
fn main() {
    // this time, `n` is mutable
    let mut n = Number { odd: true, value: 51 };
    print_number(&n);
    invert(&mut n); // `n is borrowed mutably - everything is explicit
    print_number(&n);
}
```

Trait 方法中的`self`参数可以使用引用，也可以使用不可变引用

```rust
impl std::clone::Clone for Number {
    fn clone(&self) -> Self {
        Self { ..*self }
    }
```

当调用trait的方法时，receiver隐式地被借用

```rust
fn main() {
    let n = Number { odd: true, value: 51 };
    let mut m = n.clone();
    m.value += 100;
    
    print_number(&n);
    print_number(&m);
}
```

强调一点，下面的代码是等价的:

```rust
let m = n.clone();

let m = std::clone::Clone::clone(&n);
```

像 `Copy` 这样的 Marker traits 是没有实现原对象trait方法的

```rust
// note: `Copy` requires that `Clone` is implemented too
impl std::clone::Clone for Number {
    fn clone(&self) -> Self {
        Self { ..*self }
    }
}

impl std::marker::Copy for Number {}
```

现在`Clone`仍然可以使用:

```rust
fn main() {
    let n = Number { odd: true, value: 51 };
    let m = n.clone();
    let o = n.clone();
}
```

但是`Number`的值不会被转移了

```rust
fn main() {
    let n = Number { odd: true, value: 51 };
    let m = n; // `m` is a copy of `n`
    let o = n; // same. `n` is neither moved nor borrowed.
}
```

一些`trait`太通用了，我们可以通过derive属性自动实现它们:

```rust
#[derive(Clone, Copy)]
struct Number {
    odd: bool,
    value: i32,
}

// this expands to `impl Clone for Number` and `impl Copy for Number` blocks.
```

函数可以是泛型的:

```rust
fn foobar<T>(arg: T) {
    // do something with `arg`
}
```

它们可以有多个“类型参数”，类型参数用在函数声明和函数体中，用来替代具体的类型:

```rust
fn foobar<L, R>(left: L, right: R) {
    // do something with `left` and `right`
}
```

类型参数通常有“约束”，所以你可以用它做一些额外的事情。

最简单的约束就是trait名称:

```rust
fn print<T: Display>(value: T) {
    println!("value = {}", value);
}

fn print<T: Debug>(value: T) {
    println!("value = {:?}", value);
}
```

类型参数约束可以有更长的语法：

```rust
fn print<T>(value: T)
where
    T: Display,
{
    println!("value = {}", value);
}
```

约束还可以变得更加复杂，比如要求类型参数要实现多种trait:

```rust
use std::fmt::Debug;

fn compare<T>(left: T, right: T)
where
    T: Debug + PartialEq,
{
    println!("{:?} {} {:?}", left, if left == right { "==" } else { "!=" }, right);
}

fn main() {
    compare("tea", "coffee");
    // prints: "tea" != "coffee"
}
```

泛型函数可以被当作一个命名空间，包含无穷多个不同具体类型的函数。

类似`crate`、`module`和`type`，泛型函数可以使用`::`导航:

```rust
fn main() {
    use std::any::type_name;
    println!("{}", type_name::<i32>()); // prints "i32"
    println!("{}", type_name::<(f64, char)>()); // prints "(f64, char)"
}
```

这被亲切地称之为[turbofish 语法](https://turbo.fish/)，因为`::<>`看起来像条鱼。:)

结构体也可以是泛型的:

```rust
struct Pair<T> {
    a: T,
    b: T,
}

fn print_type_name<T>(_val: &T) {
    println!("{}", std::any::type_name::<T>());
}

fn main() {
    let p1 = Pair { a: 3, b: 9 };
    let p2 = Pair { a: true, b: false };
    print_type_name(&p1); // prints "Pair<i32>"
    print_type_name(&p2); // prints "Pair<bool>"
}
```

标准库中的类型`Vec`(即分配在堆上的数组)就是泛型实现的:

```rust
fn main() {
    let mut v1 = Vec::new();
    v1.push(1);
    let mut v2 = Vec::new();
    v2.push(false);
    print_type_name(&v1); // prints "Vec<i32>"
    print_type_name(&v2); // prints "Vec<bool>"
}
```

谈到Vec，有个宏(macro)可以通过字面方式声明Vec变量:

> Tip：Rust中可以使用`!`定义一个宏，例如`println!`这样的宏；也可以使用上文中`#[derive]`这样的方式进行自定义


```rust
fn main() {
    let v1 = vec![1, 2, 3];
    let v2 = vec![true, false, true];
    print_type_name(&v1); // prints "Vec<i32>"
    print_type_name(&v2); // prints "Vec<bool>"
}
```

类似`name!()`、`name![]`、`name!{}`都是调用宏的方式，宏会被展开成正常的代码。

事实上，`println`就是一个宏:

```rust
fn main() {
    println!("{}", "Hello there!");
}
```

其展开代码和下面的代码功能一样:

```rust
fn main() {
    use std::io::{self, Write};
    io::stdout().lock().write_all(b"Hello there!\n").unwrap();
}
```

`panic`也是一个宏，用来直接停止代码执行并抛出错误信息，同时附带文件名和代码行号（需启用该功能）

```rust
fn main() {
    panic!("This panics");
}
// output: thread 'main' panicked at 'This panics', src/main.rs:3:5
```

有些方法也会出现`panic`。例如，`Option`类型可以包含某些内容，也可以不包含任何内容。如果对它调用`.unwrap()`，并且它不包含任何内容，则会执行`panic`宏：

```rust
fn main() {
    let o1: Option<i32> = Some(128);
    o1.unwrap(); // this is fine

    let o2: Option<i32> = None;
    o2.unwrap(); // this panics!
}

// output: thread 'main' panicked at 'called `Option::unwrap()` on a `None` value', src/libcore/option.rs:378:21
```

> Tip：Panic 是 Rust 中的一个错误处理机制，当程序遇到无法处理的错误时，它会立即终止当前线程的执行，并开始回溯(unwinding)过程。一般如下情况会出现 Panic:
>
> 1. 显式调用`panic!`宏。
> 2. 某些运行时检查失败，例如数组越界。 [^3]

`Option`并不是一个结构体，而是一个枚举类型(enum)，它包含两个值:

```rust
enum Option<T> {
    None,
    Some(T),
}

impl<T> Option<T> {
    fn unwrap(self) -> T {
        // enums variants can be used in patterns:
        match self {
            Self::Some(t) => t,
            Self::None => panic!(".unwrap() called on a None option"),
        }
    }
}

use self::Option::{None, Some};

fn main() {
    let o1: Option<i32> = Some(128);
    o1.unwrap(); // this is fine

    let o2: Option<i32> = None;
    o2.unwrap(); // this panics!
}

// output: thread 'main' panicked at '.unwrap() called on a None option', src/main.rs:11:27
```

`Result`也是一个枚举类型。它既可以包含某些结果，也可以包含一个error:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

如果包含error，unwrapped时也会触发`panic`。

变量绑定存在“生命周期”:

```rust
fn main() {
    // `x` doesn't exist yet
    {
        let x = 42; // `x` starts existing
        println!("x = {}", x);
        // `x` stops existing
    }
    // `x` no longer exists
}
```

类似地，引用同样存在生命周期:

```rust
fn main() {
    // `x` doesn't exist yet
    {
        let x = 42; // `x` starts existing
        let x_ref = &x; // `x_ref` starts existing - it borrows `x`
        println!("x_ref = {}", x_ref);
        // `x_ref` stops existing
        // `x` stops existing
    }
    // `x` no longer exists
}
```

引用的生命周期无法超过它借用的变量的生命周期:

```rust
fn main() {
    let x_ref = {
        let x = 42;
        &x
    };
    println!("x_ref = {}", x_ref);
    // error: `x` does not live long enough
}
```

一个变量可以不可变地引用多次:

```rust
fn main() {
    let x = 42;
    let x_ref1 = &x;
    let x_ref2 = &x;
    let x_ref3 = &x;
    println!("{} {} {}", x_ref1, x_ref2, x_ref3);
}
```

在借用的时候，变量不能被修改:

```rust
fn main() {
    let mut x = 42;
    let x_ref = &x;
    x = 13;
    println!("x_ref = {}", x_ref);
    // error: cannot assign to `x` because it is borrowed
}
```

当不可变地借用时，不能同时可变地的借用:

> Tip：即不能对一个变量同时创建不可变和可变的引用

```rust
fn main() {
    let mut x = 42;
    let x_ref1 = &x;
    let x_ref2 = &mut x;
    // error: cannot borrow `x` as mutable because it is also borrowed as immutable
    println!("x_ref1 = {}", x_ref1);
}
```

函数参数中的引用同样存在生命周期：

```rust
fn print(x: &i32) {
    // `x` is borrowed (from the outside) for the
    // entire time this function is called.
}
```


[^1]: [A half-hour to learn Rust](https://fasterthanli.me/articles/a-half-hour-to-learn-rust)
[^2]: [Rust半小时教程](https://colobu.com/2020/03/05/A-half-hour-to-learn-Rust/)
[^3]: [深入探索 Rust 中的 Panic 机制](https://juejin.cn/post/7314144983018782761)<script src="https://giscus.app/client.js"
    data-repo="jygzyc/notes"
    data-repo-id="R_kgDOJrOxMQ"
    data-mapping="number"
    data-term="8"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="top"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    data-loading="lazy"
    crossorigin="anonymous"
    async>
</script>
