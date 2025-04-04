---
title: 提示工程个人笔记
slug: technology/ai/prompt/discussion-37/
number: 37
url: https://github.com/jygzyc/notes/discussions/37
created: 2025-03-12
updated: 2025-03-23
authors: [jygzyc]
categories: [人工智能]
labels: ['Prompt相关']
draft: true
comments: true
---

<!-- name: llm_prompt -->

> AI prompt 个人笔记[^1][^2][^3]

## Prompt简介与构建思维模式

Prompt是指你向AI输入的内容，它直接指示AI该做什么任务或生成什么样的输出，简而言之， Prompt就是你与AI之间的“对话内容”，可以是问题、指令、描述或者任务要求，目的是引导AI进行特定的推理，生成或操作，从而得到预期的结果

### 大模型设置

**Temperature**：temperature 的参数值越小，模型返回结果确定性越高，反之，创造性越高。在实际应用方面，对于质量保障（QA）等任务，更低的 temperature 值可以促使模型基于事实返回更真实和简洁的结果。 对于诗歌生成或其他创造性任务，适度地调高 temperature 参数值可能会更好。

**Top_p**：同样，使用 top_p（与 temperature 一起称为核采样（nucleus sampling）的技术），可以用来控制模型返回结果的确定性。如果你需要准确和事实的答案，就把参数值调低。如果你在寻找更多样化的响应，可以将其值调高点。

一般建议是改变 Temperature 和 Top_P 其中一个参数就行，不用两个都调整。

**Max Length**：您可以通过调整 max length 来控制大模型生成的 token 数。指定 Max Length 有助于防止大模型生成冗长或不相关的响应并控制成本。

### Prompt构建思维模式

- 输入决定输出思维模型：核心原则是“理解思维，清晰表达，极致压缩”。
- 本质逻辑：理解为炼丹过程，需将需求提炼至本质（如毛选十六字方针，敌进我退，敌驻我扰，敌疲我打，敌退我追）。
- 方法论：
    1. 明确目标与需求
    2. 提供必要的背景信息（领域知识+上下文）
    3. 明确输出参数（格式/字数/数据与引用/风格）

案例1：

```md
模糊输入 -> 如果你输入“写一篇文章”，AI并不知道你具体需要什么样的文章  
模糊输入 -> 如果你输入"写一篇关于AI在医疗行业应用的1000字文"，却没有其他和未来发展趋势、AI的具体应用领域等信息，AI将难以满足你的要求
清晰表达 -> "分析2024年中国电子消费品市场的发展趋势"，指明主题、时间、地点、明确方向，让 AI 容易理解你的真实意图
```

案例2：

```md
假设你请求AI分析智能家居市场，相关的背景信息包括  
- 市场规模：2024年智能家居市场预计达到500亿美元  
- 主要竞争者：Amazon、Google、Apple等  
- 技术动态：人工智能助手、物联网设备的集成、语音控制的普及等  
```

这些背景信息将帮助AI更精准地定位分析内容，确保报告全面且具体

AI 使用过程中常见如下坑点：

- 输出不符合预期：AI没有理解你的意图，输出与需求存在偏差
- 任务抽象复杂：任务内容过于抽象复杂，AI难以处理
- 语句敏感，遇到限制：含有敏感词汇或主题，触发AI的安全限制

但其实上述的问题都可以通过更加优化的Prompt设计来解决

## Prompt设计与优化

Prompt设计的本质：**将你的想法进行极致简洁的输出**

极致简洁示例1:

```md
> 世界，这个浩瀚而奇妙的舞台，被数十亿的灵魂所共享。但每个人都在各自独特的角度，创造着不同的生活画面。从富足的城市到贫瘠的角落，从繁华的都市到宁静的乡村，这些生活的碎片汇聚在一起，形成了我们复杂多元的世界。在我看来，理解和尊重这种多样性，是我们作为人类共同体的责任，也是通往和平与和谐的关键...（全文略）

极致简洁：描述世界多样性
```

极致简洁示例2:

```md
> 人工智能的发展历程，是一部充满探索与创新的历史。但在这种迅速的发展中，人类也需要时刻保持谨慎。在这个时代中，人类文明的进步和AI的发展紧密相连，这一现象使得人类的进化轨迹发生了前所未有的改变。从而引发了人类的担忧和对技术伦理的思考...（全文略）

极致简洁：可持续发展
```

### Prompt设计技巧

- 具体化问题，明确主题

通过将问题具体化，可以更精确地获得所需的信息。明确主题，有助于更准确地判断信息来源。

- ~~请帮我提供有关于经济学的书籍~~
- **请帮我寻找有关于商业竞争的书籍，特别是关于2022-2024年间，基于案例的优秀著作**

- 少样本分析

// TODO

## Prompt越狱

// TODO

## 附录1：常见的提示技术

// TODO

[^1]: [Prompt越狱手册](https://github.com/Acmesec/PromptJailbreakManual)
[^2]: [提示工程指南](https://www.promptingguide.ai/)
[^3]: [Ai迷思录（应用与安全指南）](https://github.com/Acmesec/theAIMythbook)
