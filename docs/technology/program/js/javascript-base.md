---
title: JavaScript基础
slug: technology/program/js/discussion-7/
url: https://github.com/jygzyc/notes/discussions/7
date: 2024-04-19
authors: [jygzyc]
categories: 
  - 0102-编程
labels: ['010201-JavaScript']
comments: false
---

<!-- javascript_base -->
## Promise

> 转发自[Promise - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1022910821149312/1023024413276544)，学习自用

在JavaScript的世界中，所有代码都是单线程执行的。

由于这个“缺陷”，导致JavaScript的所有网络操作，浏览器事件，都必须是异步执行。异步执行可以用回调函数实现：

```js
function callback() {
    console.log('Done');
}
console.log('before setTimeout()');
setTimeout(callback, 1000); // 1秒钟后调用callback函数
console.log('after setTimeout()');
```

上述代码输出为

```bash
before setTimeout()
after setTimeout()
(等待1秒后)
Done
```

可见，异步操作会在将来的某个时间点触发一个函数调用。

我们先看一个最简单的Promise例子：生成一个0-2之间的随机数，如果小于1，则等待一段时间后返回成功，否则返回失败：

```js
function test(resolve, reject) {
    var timeOut = Math.random() * 2;
    log('set timeout to: ' + timeOut + ' seconds.');
    setTimeout(function () {
        if (timeOut < 1) {
            log('call resolve()...');
            resolve('200 OK');
        }
        else {
            log('call reject()...');
            reject('timeout in ' + timeOut + ' seconds.');
        }
    }, timeOut * 1000);
}
```

这个`test()`函数有两个参数，这两个参数都是函数，如果执行成功，我们将调用`resolve('200 OK')`，如果执行失败，我们将调用`reject('timeout in ' + timeOut + ' seconds.')`。可以看出，`test()`函数只关心自身的逻辑，并不关心具体的`resolve`和`reject`将如何处理结果。

有了执行函数，我们就可以用一个Promise对象来执行它，并在将来某个时刻获得成功或失败的结果：

```js
var p1 = new Promise(test);
var p2 = p1.then(function (result) {
    console.log('成功：' + result);
});
var p3 = p2.catch(function (reason) {
    console.log('失败：' + reason);
});
```

变量`p1`是一个Promise对象，它负责执行`test`函数。由于`test`函数在内部是异步执行的，当`test`函数执行成功时，我们告诉Promise对象：

```js
// 如果成功，执行这个函数：
p1.then(function (result) {
    console.log('成功：' + result);
});
```

当`test`函数执行失败时，我们告诉Promise对象

```js
p2.catch(function (reason) {
    console.log('失败：' + reason);
});
```

Promise对象可以串联起来，所以上述代码可以简化为：

```js
new Promise(test).then(function (result) {
    console.log('成功：' + result);
}).catch(function (reason) {
    console.log('失败：' + reason);
});
```

实际测试一下，看看Promise是如何异步执行的：

```js
new Promise(function (resolve, reject) {
    log('start new Promise...');
    var timeOut = Math.random() * 2;
    log('set timeout to: ' + timeOut + ' seconds.');
    setTimeout(function () {
        if (timeOut < 1) {
            log('call resolve()...');
            resolve('200 OK');
        }
        else {
            log('call reject()...');
            reject('timeout in ' + timeOut + ' seconds.');
        }
    }, timeOut * 1000);
}).then(function (r) {
    log('Done: ' + r);
}).catch(function (reason) {
    log('Failed: ' + reason);
});
```

执行结果为

```bash
Log:
start new Promise...
set timeout to: 0.9886794993641219 seconds.
call resolve()...
Done: 200 OK
```

可见Promise最大的好处是在异步执行的流程中，把执行代码和处理结果的代码清晰地分离了

Promise还可以做更多的事情，比如，有若干个异步任务，需要先做任务1，如果成功后再做任务2，任何任务失败则不再继续并执行错误处理函数。

要串行执行这样的异步任务，不用Promise需要写一层一层的嵌套代码。有了Promise，我们只需要简单地写：

```js
job1.then(job2).then(job3).catch(handleError);
```

其中，`job1`、`job2`和`job3`都是Promise对象。

除了串行执行若干异步任务外，Promise还可以并行执行异步任务。

试想一个页面聊天系统，我们需要从两个不同的URL分别获得用户的个人信息和好友列表，这两个任务是可以并行执行的，用`Promise.all()`实现如下

```js
var p1 = new Promise(function (resolve, reject) {
    setTimeout(resolve, 500, 'P1');
});
var p2 = new Promise(function (resolve, reject) {
    setTimeout(resolve, 600, 'P2');
});
// 同时执行p1和p2，并在它们都完成后执行then:
Promise.all([p1, p2]).then(function (results) {
    console.log(results); // 获得一个Array: ['P1', 'P2']
});
```

有些时候，多个异步任务是为了容错。比如，同时向两个URL读取用户的个人信息，只需要获得先返回的结果即可。这种情况下，用`Promise.race()`实现：

```js
var p1 = new Promise(function (resolve, reject) {
    setTimeout(resolve, 500, 'P1');
});
var p2 = new Promise(function (resolve, reject) {
    setTimeout(resolve, 600, 'P2');
});
Promise.race([p1, p2]).then(function (result) {
    console.log(result); // 'P1'
});
```

由于`p1`执行较快，Promise的`then()`将获得结果'P1'。`p2`仍在继续执行，但执行结果将被丢弃。

如果我们组合使用Promise，就可以把很多异步任务以并行和串行的方式组合起来执行。

## async函数

> 转发自[async函数 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1022910821149312/1536754328797217)，学习自用

我们说JavaScript异步操作需要通过Promise实现，一个Promise对象在操作网络时是异步的，等到返回后再调用回调函数，执行正确就调用`then()`，执行错误就调用`catch()`，虽然异步实现了，不会让用户感觉到页面“卡住”了，但是一堆`then()`、`catch()`写起来麻烦看起来也乱。

可以用关键字async配合await调用Promise，实现异步操作，但代码却和同步写法类似：

```js
async function get(url) {
    let resp = await fetch(url);
    return resp.json();
}
```

使用`async function`可以定义一个异步函数，异步函数和Promise可以看作是等价的，在`async function`内部，用`await`调用另一个异步函数，写起来和同步代码没啥区别，但执行起来是异步的。

也就是说：

```js
let resp = await fetch(url);
```

自动实现了异步调用，它和下面的Promise代码等价：

```js
let promise = fetch(url);
promise.then((resp) => {
    // 拿到resp
})
```

如果我们要实现`catch()`怎么办？用Promise的写法如下：

```js
let promise = fetch(url);
promise.then((resp) => {
    // 拿到resp
}).catch(e => {
    // 出错了
});
```

用await调用时，直接用传统的`try{ ... } catch`

```js
async function get(url) {
    try {
        let resp = await fetch(url);
        return resp.json();
    } catch (e) {
        // 出错了
    }
}
```

用async定义异步函数，用await调用异步函数，写起来和同步代码差不多，但可读性大大提高。

需要特别注意的是，`await`调用必须在`async function`中，不能在传统的同步代码中调用。那么问题来了，一个同步function怎么调用async function呢？

首先，普通function直接用await调用异步函数将报错：

```js
async function get(url) {
    let resp = await fetch(url);
    return resp.json();
}

function doGet() {
    let data = await get('/api/categories');
    console.log(data);
}

doGet();
```

执行结果为`SyntaxError: await is only valid in async functions and the top level bodies of modules`

如果把`await`去掉，调用实际上发生了，但我们拿不到结果，因为我们拿到的并不是异步结果，而是一个Promise对象：

```js
async function get(url) {
    let resp = await fetch(url);
    return resp.json();
}

function doGet() {
    let promise = get('/api/categories');
    console.log(promise);
}

doGet();
```

执行结果为`[object Promise]`

因此，在普通function中调用async function，不能使用await，但可以直接调用async function拿到Promise对象，后面加上`then()`和`catch()`就可以拿到结果或错误了：

```js
async function get(url) {
    let resp = await fetch(url);
    return resp.json();
}

function doGet() {
    let promise = get('/api/categories');
    promise.then(data => {
        // 拿到data
        document.getElementById('test-response-text').value = JSON.stringify(data);
    });
}

doGet();
```

因此，定义异步任务时，使用async function比Promise简单，调用异步任务时，使用await比Promise简单，捕获错误时，按传统的`try...catch`写法，也比Promise简单。只要浏览器支持，完全可以用`async`简洁地实现异步操作。
  
<script src="https://giscus.app/client.js"
    data-repo="jygzyc/notes"
    data-repo-id="R_kgDOJrOxMQ"
    data-mapping="number"
    data-term="7"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="top"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    crossorigin="anonymous"
    async>
</script>
