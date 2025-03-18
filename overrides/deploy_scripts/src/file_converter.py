# -*- coding:utf-8 -*-

import shutil
import argparse
import re
from pathlib import Path
from slugify import slugify

from .utils import BiMap

author = "yves"

class NavPagesConverter(BiMap):
    def create_pages_files(self, out_dir: Path=None):
        for key, directory in self.iterate():
            if out_dir:
                directory = out_dir / directory.lstrip('/')
            else:
                directory = Path(directory)
            file_path = directory / ".pages"
            directory.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(f"title: {key}\n")

class DiscussionConverter:

    local_lock: bool = False
    def __init__(self, discussions_data: dict, out_dir: Path):
        self.discussions_data = discussions_data
        self.out_dir = out_dir
        self.nav_map = NavPagesConverter()
        self.local_lock: bool = self._if_local_commit_lock()

    def _if_local_commit_lock(self) -> bool:
        """Check for existence of a local commit lock file.
    
        Verifies whether the system has created a 'local.lock' file in the
        configured output directory, indicating active commit restrictions.
        
        Returns: 
            Lock status: True if Lock file present, False for any other  case variation
        """
        return self.out_dir.joinpath("local.lock").exists()

    def sync_remote(self):
        try:
            discussions_list = self.discussions_data['nodes'] if 'nodes' in self.discussions_data.keys() else []
            for discussion in discussions_list:
                if not discussion:
                    print("[!] Null discussion!")
                    continue
                self.nav_converter(discussion=discussion)
                self.file_converter(discussion=discussion)
            self.nav_map.create_pages_files(out_dir=self.out_dir)
        except Exception as e:
            print("[x] Sync remote error: {}".format(e))

    def nav_converter(self, discussion):
        try:
            discussion_category_name = discussion['category']['name']
            discussion_category_description = discussion['category']['description']
            if self._is_category_blog_or_site(discussion_category_description):
                return
            
            # use preprecess-discussion_category_description as BiMap value
            bi_map_value = self._path_preprocess(discussion_category_description)
            self.nav_map.put(discussion_category_name, bi_map_value)

            for node in discussion['labels']['nodes']:
                label_name = node['name']
                label_description = node['description']
                if self._is_label_draft(label_description) or \
                    self._is_label_locked(label_description) or \
                    self._is_blog_posts(label_description):
                    continue
                if label_description.find(discussion_category_description) != -1:
                    # use preprecess-label_description as BiMap value
                    bi_map_value = self._path_preprocess(label_description)
                    self.nav_map.put(label_name, bi_map_value)
                    break
        except Exception as e:
            print("[x] Nav converter error: {}".format(e))
            raise e

    def file_converter(self, discussion):
        try:
            # When the generation of the markdown file path fails, proceed to the next one.
            md_path = self.md_directory_path_generator(discussion=discussion)
            if not md_path:
                print("[!] Path: {} skip processing".format(discussion['category']['name']))
                return 

            md_filename = self.md_filename_generator(discussion=discussion)
            md_metadata = self.md_meta_generator(discussion=discussion, md_name=md_filename, md_path=md_path)
            discussion_body = discussion["body"]
            saved_dir = self.out_dir.joinpath(md_path)
            if saved_dir.exists():
                for i in saved_dir.glob(md_filename):
                    i.unlink()
            else:
                Path(saved_dir).mkdir(parents=True, exist_ok=True)

            saved_filepath = Path(saved_dir).joinpath(md_filename)
            print("[*] Path: {}".format(saved_filepath))
            with open(saved_filepath, "w") as md_file:
                md_file.write(md_metadata)
                md_file.write(discussion_body)
        except Exception as e:
            raise e

    def md_filename_generator(self, discussion: dict):
        """
        根据讨论内容生成 Markdown 文件名。

        该函数通过从讨论正文中提取特定模式或回退到对讨论标题进行 slugify 处理来生成 Markdown 文件名。

        参数:
        -----------
        discussion : dict
            表示讨论节点的字典。必须包含以下键：
            - "body": 包含讨论正文文本的字符串。
            - "title": 表示讨论标题的字符串。

        返回值:
        --------
        str
            表示生成的 Markdown 文件名的字符串。文件名可能是：
            - 从讨论正文的前 10 行中提取的 `<!-- name: filename -->` 模式中的文件名。
            - 如果未找到模式，则通过对讨论标题进行 slugify 处理生成的文件名。

        描述:
        ------------
        该函数首先尝试从讨论正文的前 10 行中搜索 `<!-- name: filename -->` 模式。如果找到模式，
        则使用提取的文件名。如果未找到模式，则通过对讨论标题进行 slugify 处理（例如，将其转换为 URL 友好的格式）
        并附加 `.md` 扩展名来生成文件名。

        示例:
        --------
        如果讨论正文包含：
        ```
        <!-- name: my_note -->
        Some discussion content...
        ```
        生成的文件名将是：`my_note.md`。

        如果讨论正文不包含模式且标题为 "My Discussion Title"，
        生成的文件名将是：`my_discussion_title.md`。
        """

        discussion_body = discussion["body"]
        pattern = r'<!--\s*name:\s*([^\s]+)\s*-->'

        for line in discussion_body.splitlines()[:10]:
            match = re.search(pattern, line)
            if match:
                filename = match.group(1)
                break
        else:
            filename = f'{slugify(discussion["title"], allow_unicode=False, lowercase=True)}'
        return f'{filename}.md'

    def md_directory_path_generator(self, discussion: dict):
        """
        根据讨论的分类和标签生成目录路径。

        该函数通过检查讨论的分类和关联的标签来构建目录路径。
        如果某个标签的描述与讨论分类的描述匹配，则使用标签描述生成路径。
        否则，使用讨论分类的描述作为备用路径。

        参数:
        -----------
        discussion : dict
            表示讨论节点的字典。必须包含以下键：
            - 'category': 包含 'name' 和 'description' 键的字典。
            - 'labels': 包含 'nodes' 键的字典，每个节点是一个包含 'name' 和 'description' 的字典。

        返回值:
        --------
        str
            表示生成的目录路径的字符串。路径的构建规则如下：
            1. 将点号（.）替换为空格，并用斜杠（/）连接。
            2. 确保路径以斜杠（/）结尾。

        描述:
        ------------
        该函数执行以下步骤：
        1. 提取讨论的分类描述。
        2. 定义一个预处理 lambda 函数，用于格式化字符串：将点号替换为斜杠，并确保结果以斜杠结尾。
        3. 遍历讨论的标签，查找描述与分类描述匹配的标签。如果找到，则使用标签描述生成路径。
        4. 如果未找到匹配的标签，则使用分类描述作为备用路径。
        5. 确保最终路径以斜杠结尾。

        示例:
        --------
        给定一个讨论：
        - 分类描述: "example.category.with.dots"
        - 标签描述: "example.label.with.dots"

        生成的路径可能是: "example/category/with/dots/" 或 "example/label/with/dots/"，具体取决于匹配结果。
        """
        discussion_category_description = discussion['category']['description']
        # use discussion_category_description as path
        result = self._path_preprocess(discussion_category_description)
        for node in discussion['labels']['nodes']:
            label_description = node['description']
            if self._is_label_draft(label_description) or \
                self._is_label_locked(label_description):
                continue
            if label_description.find(discussion_category_description) != -1:
                # use label_description as path
                result = self._path_preprocess(label_description)
        return result

    def md_meta_generator(self, discussion: dict, md_name, md_path):
        """
        根据讨论内容和路径生成 Markdown 文件的元数据。

        该函数根据 Markdown 文件的类型（站点页面、博客文章或普通页面）生成 YAML 格式的元数据。
        它会检查讨论是否为草稿或评论是否被锁定，并包含相关的标签和分类信息。

        参数:
        -----------
        discussion : dict
            表示讨论节点的字典。必须包含以下键：
            - 'labels': 包含 'nodes' 键的字典，每个节点是一个包含 'name' 的字典。
            - 'title': 讨论的标题。
            - 'number': 讨论的编号。
            - 'url': 讨论的 URL。
            - 'createdAt': 讨论的创建时间戳。
            - 'updatedAt': 讨论的最后更新时间戳。
            - 'author': 包含 'login' 键的字典，表示作者的 GitHub 用户名。
            - 'category': 包含 'name' 键的字典，表示讨论的分类。

        md_name : str
            Markdown 文件的名称。

        md_path : str
            Markdown 文件的保存路径。该路径决定了生成的元数据类型：
            - ".": 站点页面的元数据。
            - "blog/posts/": 博客文章的元数据。
            - 其他路径: 普通页面的元数据。

        返回值:
        --------
        str
            包含生成的元数据的 YAML 格式字符串。

        描述:
        ------------
        该函数执行以下步骤：
        1. 检查讨论是否为草稿或评论是否被锁定，通过检查其标签实现。
        2. 根据提供的 `md_path` 生成元数据：
        - 对于站点页面（md_path == "."），包含标题、slug、日期等基本元数据。
        - 对于博客文章（md_path == "blog/posts/"），包含额外的字段如分类。
        - 对于普通页面，包含标签和分类。
        3. 返回 YAML 格式的元数据字符串。
        """
        is_comment_open = "true"
        is_draft = "false"
        label_list = []

        for node in discussion['labels']['nodes']:
            label_name = node['name']
            label_description = node['description'].strip()
            if self._is_label_draft(label_description):
                is_draft = "true"
                continue
            elif self._is_label_locked(label_description):
                is_comment_open = "false"
                continue
            else:
                label_list.append(label_name)

        match md_path:
            case ".":
                metadata = (f'---\n'
                            f'title: {discussion["title"]}\n'
                            f'number: {str(discussion["number"])}\n'
                            f'url: {discussion["url"]}\n'
                            f'authors: [{discussion["author"]["login"]}]\n'
                            f'template: home.html\n'
                            f'draft: {is_draft}\n'
                            f'comments: {is_comment_open}\n'
                            f'---\n\n')
            case "blog/posts/":
                slug = "blog/discussion-{0}".format(discussion["number"])
                metadata = (f'---\n'
                            f'title: {discussion["title"]}\n'
                            f'slug: {slug}/\n'
                            f'number: {str(discussion["number"])}\n'
                            f'url: {discussion["url"]}\n'
                            f'date:\n'
                            f'  created: {discussion["createdAt"][0:10]}\n'
                            f'  updated: {discussion["updatedAt"][0:10]}\n'
                            f'created: {discussion["createdAt"][0:10]}\n'
                            f'updated: {discussion["updatedAt"][0:10]}\n'
                            f'authors: [{author}]\n'
                            f'categories: {label_list}\n' 
                            f'draft: {is_draft}\n'
                            f'comments: {is_comment_open}\n'
                            f'---\n\n')
            case _:
                slug = Path(md_path).joinpath("discussion-{0}".format(discussion["number"]))
                metadata = (f'---\n'
                            f'title: {discussion["title"]}\n'
                            f'slug: {slug}/\n'
                            f'number: {str(discussion["number"])}\n'
                            f'url: {discussion["url"]}\n'
                            f'created: {discussion["createdAt"][0:10]}\n'
                            f'updated: {discussion["updatedAt"][0:10]}\n'
                            f'authors: [{discussion["author"]["login"]}]\n'
                            f'categories: [{discussion["category"]["name"]}]\n'
                            f'labels: {label_list}\n'
                            f'draft: {is_draft}\n'
                            f'comments: {is_comment_open}\n'
                            f'---\n\n')
        return metadata

    def _path_preprocess(self, path: str) -> str:
        """Preprocess and normalize content path strings with strict formatting.
        
        Handles path conversion with the following rules:
        1. Always remove leading/trailing whitespace
        2. Convert dot-separated patterns to directory structure
        3. Maintain trailing slash based on original input
        
        Args:
            path: Raw input path string
            
        Returns:
            Normalized path with:
            - No leading/trailing whitespace
            - Dots converted to directory separators
            - Trailing slash preserved from original
            
        Examples:
            >>> _path_preprocess(" . ")
            '.'
            >>> _path_preprocess(" data.archive/  ")
            'data/archive/'
            >>> _path_preprocess("blog.posts")
            'blog/posts/'
        """
        stripped = path.strip()
    
        if stripped == ".":
            return stripped

        processed = "/".join(stripped.replace(".", " ").split())
        has_trailing_slash = path.rstrip().endswith("/") if stripped else path.endswith("/")
        return f"{processed}/" if not has_trailing_slash else processed
    
        # if path.strip() == ".":
        #     return path
        # return "/".join(path.replace(".", " ").split()).strip() + '/' \
        #     if not path.endswith('/') else "/".join(path.replace(".", " ").split()).strip()

    def _is_category_blog_or_site(self, category: str) -> bool:
        """Check if the given category represents blog posts or root site content.
    
        Verifies whether the specified category matches either:
        - The root site identifier ('.')
        - The blog posts category ('blog.posts')
        
        The comparison is case-sensitive and requires exact string matches.
        
        Args:
            category: The category string to validate
        
        Returns:
            bool: True if category is exactly '.' or 'blog.posts', False otherwise
        """
        return category == "." or category == "blog.posts"

    def _is_label_draft(self, label: str) -> bool:
        """
        Check if the given label represents a draft state.

        Args:
            label: The text label to be verified

        Returns:
            bool: True if the label is exactly 'draft', False for any other value or case variation
        """
        return label == "draft"

    def _is_label_locked(self, label: str) -> bool:
        """
        Check if the given label represents a locked state.

        Args:
            label: The text label to be verified

        Returns:
            bool: True if the label is exactly 'locked', False for any other value or case variation
        """
        return label == "locked"

    def _is_blog_posts(self, label: str) -> bool:
        """
        Check if the label is 'blog.label'.

        Args:
            label: The text label to be verified

        Returns:
            bool: True if the label is 'blog.label', otherwise False.
        """
        return label == "blog.label"

