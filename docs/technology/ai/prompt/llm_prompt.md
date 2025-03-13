---
title: Prompt个人笔记
slug: technology/ai/prompt/discussion-37/
number: 37
url: https://github.com/jygzyc/notes/discussions/37
created: 2025-03-12
updated: 2025-03-12
authors: [jygzyc]
categories: [人工智能]
labels: ['Prompt相关']
draft: false
comments: true
---

<!-- name: llm_prompt -->

> AI prompt 个人笔记[^1][^2]

## Prompt简介

Prompt是指你向AI输入的内容，它直接指示AI该做什么任务或生成什么样的输出，简而言之， Prompt就是你与AI之间的“对话内容”，可以是问题、指令、描述或者任务要求，目的是引导AI进行特定的推理，生成或操作，从而得到预期的结果

### 大模型设置

**Temperature**：简单来说，temperature 的参数值越小，模型就会返回越确定的一个结果。如果调高该参数值，大语言模型可能会返回更随机的结果，也就是说这可能会带来更多样化或更具创造性的产出。（调小temperature）实质上，你是在增加其他可能的 token 的权重。在实际应用方面，对于质量保障（QA）等任务，我们可以设置更低的 temperature 值，以促使模型基于事实返回更真实和简洁的结果。 对于诗歌生成或其他创造性任务，适度地调高 temperature 参数值可能会更好。

## Prompt构建与优化

// TODO

## Prompt越狱

// TODO


[^1]: [Prompt越狱手册](https://github.com/Acmesec/PromptJailbreakManual)
[^2]: [提示工程指南](https://www.promptingguide.ai/)