# -*- coding:utf-8 -*-
"""
File: hook_meta.py
Author: 2024 Kamil Krzyśków (HRY)
Description:
Via: https://github.com/squidfunk/mkdocs-material/discussions/5161
MkDocs hook to replace destination urls with custom slugs. 
The main issue of this feature is the fact that the front matter header is loaded 
for each page sequentially in the on_page_markdown event. To avoid issues with 
internal link references it's required to read the front matter before the MkDocs 
event. This duplicates the read task, so it decreases overall performance relative
to the amount of files.
Current limitations:
- Primitive collision check for slugs and files, doesn't check if a file has a slug that voids the collision
- `use_directory_urls` was always True during testing, the hook will not handle False 

Created: 2024
Last Modified: Ecool
Description:
Added functionality to skip files with a 'draft' tag in the meta during generation.
"""

import os
from mkdocs.plugins import get_plugin_logger
from mkdocs.utils import meta

log = get_plugin_logger("hook_meta")


class SlugCollision:
    """Container class to handle the slug collision logic"""

    file_urls: dict[str, str]
    """Dict mapping of file urls to file paths of the original file urls"""

    slug_urls: dict[str, str]
    """Dict mapping of slug urls to file paths of the custom meta slugs"""

    def __init__(self):
        self.file_urls = {}
        self.slug_urls = {}

    def is_valid(self, slug: str) -> bool:
        """Check the slug string for errors and check for collisions"""

        if slug is None:
            return False

        if not isinstance(slug, str):
            log.error(f"'slug' has to be a string not {type(slug)}")
            return False
        
        if slug.startswith("/") or not slug.endswith("/"):
            log.warning(f"'slug': '{slug}' can't start with a '/' and has to end with a '/'")
            return False

        if "\\" in slug:
            log.error(f"'slug' can't be a Windows path with '\\'")
            return False

        if slug in self.file_urls:
            log.warning(f"'slug': '{slug}' collides with the file: {self.file_urls[slug]}")
            return False

        if slug in self.slug_urls:
            log.warning(f"'slug': '{slug}' was already used in the file: {self.slug_urls[slug]}")
            return False

        return True 

def _load_meta(file):
    """Local copy of mkdocs.structure.pages.Page.read_source"""

    try:
        with open(file.abs_src_path, encoding="utf-8-sig", errors="strict") as f:
            source = f.read()
        _, file_meta = meta.get_data(source)
        return file_meta
    except OSError:
        log.error(f"File not found: {file.src_path}")
        raise
    except ValueError:
        log.error(f"Encoding error reading file: {file.src_path}")
        raise


def on_files(files, config, **__):
    """
    via: https://www.mkdocs.org/dev-guide/plugins/#on_files
    """
    # meta slug collision check
    slug_collision = SlugCollision()

    # First load the urls
    for file in files.documentation_pages():
        slug_collision.file_urls[file.url] = file.abs_src_path

    for file in files.documentation_pages():
        is_draft = _load_meta(file).get("draft")
        if is_draft == True:
            files.remove(file)
            log.info(f"Remove '{file.name}' due to 'draft' tag in meta data")
            continue

    # Second process the meta
    for file in files.documentation_pages():
        slug = _load_meta(file).get("slug")

        if not slug_collision.is_valid(slug):
            continue

        # TODO Add handling for `use_directory_urls`
        file.url = slug
        file.dest_uri = slug + "index.html"
        file.abs_dest_path = os.path.normpath(os.path.join(config["site_dir"], file.dest_uri))

        slug_collision.slug_urls[slug] = file.abs_src_path
