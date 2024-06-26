---
title: Android Intent安全那些事儿
slug: technology/android/security/discussion-22/
number: 22
url: https://github.com/jygzyc/notes/discussions/22
created: 2024-06-25
updated: 2024-06-26
authors: [jygzyc]
categories: 
  - 0101-Android
labels: ['010102-漏洞与安全']
comments: true
---

<!-- intent_security -->

## 前言

Intent是Android程序中不同组件传递数据的一种方式，翻译为意图，Intent既可以用在`startActivity`方法中来启动Activity，也可以用在`sendBroadcast`中来发送携带Intent的广播，甚至可以使用`startService(Intent)` 或者 `bindService(Intent, ServiceConnection, int)` 来和后台Service进行交互。总而言之，Intent是Android不同组件之间交互的一个桥梁，同时也能够在不同的应用之间进行数据的交互。其中，Intent又分为显示Intent和隐式Intent。

- 显式Intent：通过组件名指定启动的目标组件，比如`startActivity(new Intent(A.this,B.class));` 每次启动的组件只有一个。这是一种较为安全的调用方式

- 隐式Intent：不指定组件名，而指定Intent的Action，Data或Category，当我们启动组件时，会去匹配`AndroidManifest.xml`相关组件的`intent-filter`，逐一匹配出满足属性的组件，当不止一个满足时，会弹出一个让我们选择启动哪个的对话框。**这种调用方式会间接导致很多问题**

## 背景知识

### Activity相关

让我们先来了解一下可能涉及到的函数接口

- `public void startActivityForResult (Intent intent,  int requestCode)`

这个方法本质上与`public void startActivityForResult (Intent intent,  int requestCode， Bundle options)`相同，用来在启动Activity结束后返回结果，其中第一个参数`intent`是你需要发送的Intent，第二个参数`requestCode`，当其大于或等于0时，Activity启动后的结果将被归还到`onActivityResult`方法中；而当其小于0时，该方法本质上就等同于`startActivity(Intent)`，即启动的Activity将不再被作为子Activity，不会返回数据。

- `public final void setResult (int resultCode， Intent data)`

调用此方法可设置Activity返回调用方的result。第一个参数resultCode有三种常量，分别为`RESULT_CANCELED`（值为0），`RESULT_FIRST_USER`（值为1）和`RESULT_OK`（值为-1）。第二个参数`data`在Android 2.3以上版本可以被赋予`Intent.FLAG_GRANT_READ_URI_PERMISSION`和/或`Intent.FLAG_GRANT_WRITE_URI_PERMISSION` 标志。这将授予接收结果的Activity对Intent中特定 URI 的访问权限，且访问将一直保留到Activity结束。

- `protected void onActivityResult(int requestCode, int resultCode, Intent data)`

这个方法在启动的Activity退出时调用。其中第一个参数`requestCode`用来提供给`onActivityResult`确认数据是从哪个Activity返回的，其实就是在`startActivityForResult`中设置的`requestCode`。第二个参数`resultCode`是由子Activity通过其`setResult(Int, Intent)`方法返回的，值为`setResult(int resultCode, Intent data)`的第一个参数`resultCode`。

看完上面枯燥的介绍，相信还是有一点模糊的，光说不练假把式，下面举个例子，说明一下上面这几个函数的实际应用。

在如下所示的Demo中，`FirstActivity`会通过`startActivityForResult`方法启动`SecondActivity`：

```java
public void launchSecondActivity(){
    Intent intent = new Intent();
    intent.setAction("test.action");
    startActivityForResult(intent, 1234);
}
```

`SecondActivity`收到intent后，会要求用户确认，若确认通过则通过`setResult`将结果回传`FirstActivity`：

```java
private void passCheck(){
    Toast.makeText(getApplicationContext(), "Checking...", Toast.LENGTH_SHORT).show();
    Intent intent = getIntent();
    setResult(RESULT_OK, intent);
    finish();
}
```

`FristActivity`可以通过`onActivityResult`来接收返回的结果，并执行相应的操作：

```java
@override
protected void onActivityResult(int requestCode, int resultCode, Intent data){
    super.onActivityResult(requestCode, resultCode, data);
    if(resultCode == RESULT_OK){
        Toast.makeText(getApplicationContext(), "Pass User Check", Toast.LENGTH_LONG).show();
    }    
}
```

以上就是这几个函数的一个简单的实践。

### Content Provider相关

> TODO: 补全

## 风险一：Intent重定向漏洞[^1][^2][^3][^4][^5][^6][^7][^8]

如果应用从不可信 Intent 的`extras`字段中提取 Intent或部分信息，攻击者截取到Intent或部分信息后，主要有以下两种危害：

- 启动非预期的专用组件，利用敏感的参数来执行敏感操作

- 利用授予的 URI 权限窃取敏感文件或系统数据

### 利用点1：绕过原有代码执行逻辑或敏感数据泄露

第一种情况为，三方应用利用`setResult`绕过原有的代码执行逻辑或者获取intent中携带的敏感数据。

在上文中，我们能够看见`SecondActivity`中通过提取`FirstActivity`中发送的intent，通过进一步处理，再将结果返回，我们查看`SecondActivity`在`AndroidManifest.xml`中的定义


[^1]: [Activity 参考](https://developer.android.com/reference/android/app/Activity)
[^2]: [Intent 参考](https://developer.android.com/reference/android/content/Intent)
[^3]: [GHSL-2021-1033: Intent URI permission manipulation in Nextcloud News for Android - CVE-2021-41256]( https://securitylab.github.com/advisories/GHSL-2021-1033_Nextcloud_News_for_Android/)
[^4]: [NextCloud News App](https://github.com/nextcloud/news-android)
[^5]: [startActivityForResult的简单使用总结](https://www.jianshu.com/p/acaa50c35811)
[^6]: [FileProvider 参考](https://developer.android.com/reference/androidx/core/content/FileProvider)
[^7]: [Android FileProvider配置使用](https://www.jianshu.com/p/e9043ab9dc69)
[^8]: [针对 Intent 重定向漏洞的修复方法](https://support.google.com/faqs/answer/9267555)
