---
title: 主页
slug: index./
number: 21
url: https://github.com/jygzyc/notes/discussions/21
created: 2024-06-25
updated: 2025-01-21
authors: [jygzyc]
template: home.html
draft: false
comments: false
---

<!-- name: index -->

本站点基于[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)进行部署，一部分文章来源于之前的博客。

可以通过[note.lilac.fun](https://note.lilac.fun/)可以访问本站点，基于[Github Pages](https://pages.github.com/)，国内访问会有一定的延迟。

## 记录

在之前几年时间里，折腾过`Hexo`，`Hugo`，甚至还开发过相关的插件，搞过不同的留言系统，也搞过不同的相册，但是最后还是打算回归简洁。

在自建服务器到期了之后，因为也没有其他使用服务器的需求，又回归了Github，在一次无意中发现了`Mkdocs`，并喜欢上了它简洁的风格。下定决心，将之前无用的部分去除，重新建立站点。

未来，希望可以一直记录下去，把这里作为一个起点。

## 技术

本站参考[维燕的知识花园](https://weiyan.cc/)，使用了`Mkdocs` + `Github Discussions`的方式，在原作者的基础上做了少许修改，减少了一部分处理不同页面中重复的步骤，重点的代码都有注释，可以用来部署其他站点

- [x] 20230527：`nav.json`中放了全站的router，使用`nav2pages.py`进行转化，这里的标签使用两位一个分类，逐步估计应该是够用了（不够用再改），对应了discussion的各级分类和标签，具体可以参考一下`discussionFileConverter.py`的代码
- [x] 20240609：使用[Picx4R2](https://github.com/jygzyc/Picx4R2)作为图床应用，修改了部分代码缺陷，调整了上传图片后的粘贴链接，解决了图床管理时点击图片无法放大查看的问题
- [x] 20240623：解决评论加载时顺序不正确的问题，现在生成源Markdown时不会增加giscus评论代码，而是在模板中进行判断，以`page.meta.number`为生成依据；解决文件创建与更新时间错误问题——新增`page.meta.created`字段，新增`overrides/partials/source-file.html`文件解决创建时间错误
- [x] 20240624：`discussionFileConverter.py`中新增评论关闭列表，指定列表内`number`号文章将关闭评论
- [x] 20240630: 更新`discussionFileConverter.py`，`nav2pages.py`中部分代码和注释，方便维护
- [x] 20241121: 更新图床为[CloudFlare-ImgBed](https://github.com/MarSeventh/CloudFlare-ImgBed)，后续使用Telegram作为图床Base

## 联系

个人现在使用比较多的是邮箱，可以直接联系[jyg.zyc@outlook.com](mailto:jyg.zyc@outlook.com)

## 致谢

感谢[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)，让我认识了一个非常简洁和好看的博客主题，并能够很快在社区解决部署时出现的问题。

感谢[维燕的知识花园](https://weiyan.cc/)，让我学习了如何使用 Github discussions 建立博客站点。


