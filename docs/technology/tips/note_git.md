---
title: git问题记录
slug: technology/tips/discussion-32/
number: 32
url: https://github.com/jygzyc/notes/discussions/32
created: 2024-10-28
updated: 2025-03-17
authors: [jygzyc]
categories: [Tips]
labels: []
draft: false
comments: true
---

<!-- name: note_git -->

## Filename too long

先查看 git 配置，`git config --get core.longpaths`，若返回结果为`false`，则使用`git config core.longpaths true`设置为true