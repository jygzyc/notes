# Welcome to Ecool Note

!!! note "Mkdocs"
    本站点使用Mkdocs进行部署，详细的文档请参考[mkdocs.org](https://www.mkdocs.org)

:material-key-outline:{ .keyword} 命令

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

:material-key-outline:{ .keyword} 项目结构

`doc`目录中为文章所在目录，其中`Custom`可以存放自定义配置
`mkdoc.yml`为主配置项，此处使用了[mkdocs-material](https://squidfunk.github.io/mkdocs-material/)主题

```bash title="Project Layout"
.
├── Dockerfile
├── docker-compose.yml # Docker deploying file
├── docs
│   ├── custom # Custom configuration files
│   ├── index.md # The documentation homepage
│   └── ... # Other markdown pages, images and other files
├── mkdocs.yml # The configuration file
├── overrides # The theme custom configuration files
└── .gitignore
```





