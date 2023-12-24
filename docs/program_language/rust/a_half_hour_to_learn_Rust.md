# 半小时学习Rust

> 翻译自 [A half-hour to learn Rust](https://fasterthanli.me/articles/a-half-hour-to-learn-rust)

为了提高编程语言的流畅性，人们必须阅读大量编程语言的相关知识。但如果你不知道它的含义，你怎么能读这么多呢？
在本文中，我不会专注于一两个概念，而是尝试尽可能多地浏览 Rust 片段，并解释它们包含的关键字和符号的含义。
准备好了吗？冲！


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

如果这很难，可以用`_`来匹配所有模式：

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

这些被称为“孤立规则”。

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

Trait方法中的`self`参数可以使用引用，也可以使用不可变引用

```rust
impl std::clone::Clone for Number {
    fn clone(&self) -> Self {
        Self { ..*self }
    }
```