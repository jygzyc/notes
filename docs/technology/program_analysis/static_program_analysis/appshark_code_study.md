---
title: Appshark代码学习
slug: technology/program_analysis/static_program_analysis/discussion-36/
number: 36
url: https://github.com/jygzyc/notes/discussions/36
created: 2025-02-08
updated: 2025-02-10
authors: [jygzyc]
categories: [程序分析]
labels: ['静态程序分析']
draft: true
comments: true
---

<!-- name: appshark_code_study -->

## 初始化

从Java入口代码跳转到Kotlin

```kt
//net.bytedance.security.app.StaticAnalyzeMain
fun main(args: Array<String>) {
    //...
    val configPath = args[0]
    try {
        // ... 获取配置
        val argumentConfig: ArgumentConfig = Json.decodeFromString(configJson)
        cfg = argumentConfig
        ArgumentConfig.mergeWithDefaultConfig(argumentConfig)
        // ... 导入引擎配置-库包名
        getConfig().libraryPackage?.let {
            if (it.isNotEmpty()) {
                EngineConfig.libraryConfig.setPackage(it)
            }
        }
        // 协程调用主函数
        runBlocking { StaticAnalyzeMain.startAnalyze(argumentConfig) }
    // ...
}
```

```kotlin
//net.bytedance.security.app.StaticAnalyzeMain
suspend fun startAnalyze(argumentConfig: ArgumentConfig) {
    // 1. 初始化阶段
    val v3 = AnalyzeStepByStep()
    v3.initSoot(...)  // 初始化 Soot 静态分析框架
    
    // 2. APK 解析阶段
    parseApk(...)     // 使用 jadx 反编译工具解析 APK
    
    // 3. 规则加载与预处理
    val rules = v3.loadRules(...)  // 加载分析规则
    val ctx = v3.createContext(rules) // 创建分析上下文
    
    // 4. 扩展分析
    if(supportFragment) processFragmentEntries() // Fragment 专项分析
    loadDynamicRegisterReceiver(ctx) // 动态广播接收器分析
    
    // 5. 核心分析流程
    ctx.buildCustomClassCallGraph(rules) // 构建调用图
    val analyzers = v3.parseRules(ctx, rules) // 创建规则分析器
    v3.solve(ctx, analyzers) // 执行分析
}
```
