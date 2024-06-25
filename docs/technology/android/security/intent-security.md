---
title: Android Intent安全那些事儿
slug: technology/android/security/discussion-22/
number: 22
url: https://github.com/jygzyc/notes/discussions/22
created: 2024-06-25
updated: 2024-06-25
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

## 风险一：Intent重定向漏洞[^1][^2][^3][^4][^5][^6][^7]

如果应用从不可信 Intent 的`extras`字段中提取 Intent或部分信息，攻击者截取到Intent或部分信息后，有可能执行如下操作：

- 启动非预期的专用组件，利用可控的参数来执行敏感操作

- 利用授予的 URI 权限窃取敏感文件

### 背景知识

- `public void startActivityForResult (Intent intent,  int requestCode)`

这个方法本质上与public void startActivityForResult (Intent intent,  int requestCode， Bundle options)相同，用来在启动Activity结束后返回结果，其中第一个参数intent是你需要发送的intent，第二个参数requestCode，当其大于或等于0时，Activity启动后的结果将被归还到onActivityResult方法中；而当其小于0时，该方法本质上就等同于startActivity(Intent)，即启动的Activity将不再被作为子Activity，不会返回数据。

- `public final void setResult (int resultCode， Intent data)`

调用此方法可设置Activity返回调用方的result。第一个参数resultCode有三种常量，分别为RESULT_CANCELED（值为0），RESULT_FIRST_USER（值为1）和RESULT_OK（值为-1）。第二个参数Intent在Android 2.3以上版本可以被赋予Intent.FLAG_GRANT_READ_URI_PERMISSION和/或Intent.FLAG_GRANT_WRITE_URI_PERMISSION 标志。这将授予接收结果的Activity对Intent中特定 URI 的访问权限，且访问将一直保留到Activity结束。

- `protected void onActivityResult(int requestCode, int resultCode, Intent data)`

这个方法在启动的Activity退出时调用。其中第一个参数requestCode用来提供给onActivityResult，以便确认返回的数据是从哪个Activity返回的，其实就是在startActivityForResult中设置的requestCode。第二个参数resultCode是由子Activity通过其setResult(Int, Intent)方法返回的，值为setResult(int resultCode, Intent data)的第一个参数resultCode。




[^1]: [Activity 参考](https://developer.android.com/reference/android/app/Activity)
[^2]: [Intent 参考](https://developer.android.com/reference/android/content/Intent)
[^3]: [GHSL-2021-1033: Intent URI permission manipulation in Nextcloud News for Android - CVE-2021-41256]( https://securitylab.github.com/advisories/GHSL-2021-1033_Nextcloud_News_for_Android/)
[^4]: [NextCloud News App](https://github.com/nextcloud/news-android)
[^5]: [startActivityForResult的简单使用总结](https://www.jianshu.com/p/acaa50c35811)
[^6]: [FileProvider 参考](https://developer.android.com/reference/androidx/core/content/FileProvider)
[^7]: [Android FileProvider配置使用](https://www.jianshu.com/p/e9043ab9dc69)

