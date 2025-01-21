---
title: Python基础知识点
slug: technology/development/python/discussion-25/
number: 25
url: https://github.com/jygzyc/notes/discussions/25
created: 2024-07-22
updated: 2025-01-21
authors: [jygzyc]
categories: [开发专栏]
labels: ['Python相关']
draft: false
comments: true
---

<!-- name: python_base -->

## import相关知识点

### 背景

**module**本身是一个Python object（命名空间），保存在内存中，在这个Python object内还可以包含很多其它的Python object。在实际应用中，一个module通常对应一个`.py`文件，通过`import`导入的过程，能够从一个文件里生成一个module。

**package**就是一种特殊的module，比较而言，只是多了一个`__path__`，在操作系统层级，package往往对应一个文件夹，所以一个package中既可以有subpackage也可以有module。无论有没有`__init__.py`，这个文件夹都可以作为package被Python使用。

### module examples

`import`会获取到字符串，然后根据这个名字去找

- 同级文件夹下，优先搜索当前路径（`sys.path`可以看到第一个路径就是当前目录，按顺序寻找，找到之后不再检索，所以注意命名冲突的问题）

```py
####
#.
#├── example.py
#└── test.py
####

## example.py
import test
print(test)
```

- 使用 `import ... as ...` 将module保存为另一个名字
- 只需要module里的某一个object，使用`from ... import ...`

### package examples

#### Absolute import

```
####
#.
#├── example.py
#├── mypackage
#│   └── mymodule.py
#└── test.py
####

## example.py
import mypackage
print(mypackage)
```

- 如果package中存在`__init__.py`，就会最优先执行其中的代码
- 如果package中存在module，就需要使用`package.module`的方式引入，例如上述结构，引入时就需要`import mypackage.mymodule`，实际上这是一个赋值。即`mypackage`全局变量指向`mypackage`包，`mypackage.mymodule`指向`mypackage.mymodule`模块，都可以打印出来，而直接`import mypackage`并不能找到`mymodule`。
- 当使用`import mypackage.mymodule as m`时，`mypackage`全局变量就不存在了，而`m`指向`mypackage.mymodule`模块

#### relative import

一个package内不同module之间的引用更适合relative import。原因：package可能会改名；package内部路径很深，需要知道信息过多。

原理：**每一个relative import都是先找到它的绝对路径再import的，它会通过module的package变量去计算绝对路径**

以如下目录为例：

```
.
├── example.py
├── mypackage
│   ├── mymodule.py
│   ├── subpackage
│   │   └── submodule.py
│   └── util.py
└── test.py
```

```py
# example.py
import mypackage.mymodule
print(mypackage.mymodule.__package__) # 结果为 mypackage
```

```py
# mymodule.py
from .util import f # .util 会被转化为 mypackage.util 
```

也正因如此，如果直接运行`python mypackage/mymodule.py`会报错，mymodule被当作main module 加载进来，不属于任何一个package。换言之，relative import只能在package里面的module中使用，并且被导入时需要跟随package一起被导入，单独尝试运行一个package里面的module会导致relative import出错。

```py
# submodule.py
from ..util import f # 从上级目录中导入module
```

