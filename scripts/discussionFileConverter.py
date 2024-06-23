# -*- coding:utf-8 -*-

from enum import Enum, unique
from pathlib import Path
from slugify import slugify
import unittest
import sys
import argparse
import json
import re
import os

###################
# Comment Config
###################
dismiss_comment = [5]

def _is_comment_close(discussion:dict) -> str:
    number = discussion["number"]
    return "true" if number in dismiss_comment else "false"


class FileException(Exception):
    def __init__(self, message):
        super.__init__(message)
        print("File error: ", message)
        sys.exit(1)


class ArgumentException(Exception):
    def __init__(self, message):
        super.__init__(message)
        print("Arguments error: ", message)
        sys.exit(1)


@unique
class MdType(Enum):
    """
    MdType defines the different types of markdown filename labels as enum members.
    
    Attributes:
    - PRESET: Represents a preset filename for the markdown file.
    - SPECIFIC: Represents a specific filename for the markdown file.
    """
    PRESET = 1
    SPECIFIC = 2


class TestConverterMethods(unittest.TestCase):

    def setUp(self):
        with open("discussions", "r", encoding="utf-8") as f:
            self.discussions_data = eval(f.read())
        if not self.discussions_data:
            raise FileException("Test: discussion_data error")
        with open("nav.json", "r", encoding="utf-8") as f:
            self.nav_data = json.load(f)
        if not self.nav_data:
            raise FileException("Test: nav_data error")

    def test__md_filename_generator(self):
        if 'nodes' in self.discussions_data.keys():
            discussions_list = self.discussions_data['nodes']
            for discussion in discussions_list:
                if not discussion:
                    continue
                discussion_title = discussion['title']
                if discussion_title == "留言板": # site test
                    self.assertEqual(_md_filename_generator(discussion, MdType.SPECIFIC), "site-message.md")
                if discussion_title == "JavaScript基础": # common test
                    self.assertEqual(_md_filename_generator(discussion, MdType.PRESET), "javascript-base.md")

    def test__md_directory_generator(self):
        if 'nodes' in self.discussions_data.keys():
            discussions_list = self.discussions_data['nodes']
            for discussion in discussions_list:
                if not discussion:
                    continue
                discussion_title = discussion['title']
                if discussion_title == "留言板": # site test
                    self.assertEqual(_md_directory_generator(discussion, self.nav_data), ".")
                if discussion_title == "JavaScript基础": # common test
                    self.assertEqual(_md_directory_generator(discussion, self.nav_data), "technology/program/js/") 

    def test__md_meta_generator(self):
        if 'nodes' in self.discussions_data.keys():
            discussions_list = self.discussions_data['nodes']
            for discussion in discussions_list:
                if not discussion:
                    continue
                discussion_title = discussion['title']
                if discussion_title == "留言板": # site test
                    print(_md_meta_generator(discussion, 
                                             _md_filename_generator(discussion, flag=MdType.SPECIFIC),
                                             _md_directory_generator(discussion, self.nav_data)))
                if discussion_title == "JavaScript基础": # common test
                    print(_md_meta_generator(discussion, 
                                             _md_filename_generator(discussion, flag=MdType.PRESET),
                                             _md_directory_generator(discussion, self.nav_data))) 

def _md_filename_generator(discussion, flag):
    """
    Generate a markdown filename based on the content and flag provided.
    
    Parameters:
    - discussion: discussion node.
    - flag: Determines the logic for generating the filename. Can be 'MdType.PRESET', 'MdType.SPEC', or other.
    
    Returns:
    - str: A string representing the generated markdown filename.
    
    Description:
    This function is designed to create a filename for a markdown file based on the discussion content and a given flag.
    It uses regular expressions to extract specific parts of the discussion text and slugifies them to create a valid filename.
    """
    match flag:
        case MdType.PRESET:
            discussion_body = discussion["body"]
            match = re.search(r'<!--(.*?)-->', discussion_body)
            filename = match.group(1) if match else None
            return f'{slugify(filename, allow_unicode=False, lowercase=False)}.md' \
                if filename != None \
                    else f'{slugify(discussion["title"])}.md'
        case MdType.SPECIFIC:
            discussion_labels = [label['name'] for label in discussion['labels']['nodes']] if discussion['labels']['nodes'] else None
            return f'{slugify(discussion_labels[0], allow_unicode=False, lowercase=False)}.md' \
                if discussion_labels != None \
                else f'{slugify(discussion["title"], allow_unicode=True, lowercase=False)}.md'
        case _:
            return f'{slugify(discussion["title"])}.md'

def _md_directory_generator(discussion, nav):
    """
    Generate a markdown directory path based on the discussion object.
    
    Parameters:
    - discussion: A dictionary containing information about the discussion,
                         including 'category' and 'labels'.
    - nav: A json mapping numerical prefixes to their corresponding
                       directory paths.
    
    Returns:
    - str or None: The generated markdown directory path if found, otherwise None.
    
    Description:
    This function determines the appropriate directory for a markdown file based on
    the discussion's category name and labels. It uses regular expressions to extract
    numerical prefixes and then looks up the corresponding directory path in the
    provided navigation dictionary.
    """
    category_num, _ = discussion['category']['name'].split("-")
    category = discussion['category']['name']
    if int(category_num) < 100:
        if int(category_num[:2]) == 0:
            return "."
        else:
            return nav[category]
    else:
        discussion_label = (
            [label['name'] for label in discussion['labels']['nodes']] 
            if discussion['labels']['nodes'] else []
        )
        return nav[category_num[:2]][discussion_label[0]] if discussion_label != [] else nav[category_num[:2]][category]

def _md_meta_generator(discussion: dict, md_name, md_path):
    """
    Generate markdown metadata for a given discussion object.
    
    Parameters:
    - discussion (dict): A dictionary representing a discussion object which includes
                         details like 'title', 'url', etc.
    - md_name
    - md_path
    
    Returns:
    - str: A string of markdown formatted metadata.
    
    Description:
    This function creates markdown metadata (YAML front matter) for a discussion object.
    It constructs the metadata based on the category number of the discussion. The category
    number determines the structure and content of the metadata.
    """
    category_num_prefix = discussion['category']['name'][:2]
    md_name, _ = os.path.splitext(os.path.basename(md_name)) #if md_name[-3:] == ".md" else md_name
    
    # site and blog pages
    if int(category_num_prefix) == 0:
        metadata = (f'---\n'
                    f'title: {discussion["title"]}\n'
                    f'url: {discussion["url"]}\n'
                    f'number: {str(discussion["number"])}\n'
                    f'slug: {"{}/".format(md_name)}\n'
                    f'created: {discussion["createdAt"][0:10]}\n'
                    f'updated: {discussion["updatedAt"][0:10]}\n'
                    f'authors: [{discussion["author"]["login"]}]\n'
                    f'categories: \n'
                    f'  - {discussion["category"]["name"]}\n'
                    f'comments: {_is_comment_close(discussion)}\n'
                    f'---\n\n')
    elif int(category_num_prefix) == 9:
        slug = "blog/discussion-{0}".format(discussion["number"])
        metadata = (f'---\n'
                    f'title: {discussion["title"]}\n'
                    f'slug: {slug}/\n'
                    f'number: {str(discussion["number"])}\n'
                    f'url: {discussion["url"]}\n'
                    f'date:\n'
                    f'  created: {discussion["createdAt"][0:10]}\n'
                    f'  updated: {discussion["updatedAt"][0:10]}\n'
                    f'authors: [Ecool]\n'
                    f'categories: \n'
                    f'  - {discussion["category"]["name"]}\n'
                    f'labels: {[label["name"] for label in discussion["labels"]["nodes"]] if discussion["labels"]["nodes"] else []}\n'
                    f'comments: {_is_comment_close(discussion)}\n'
                    f'---\n\n')
    else:
        # common pages
        slug = Path(md_path).joinpath("discussion-{0}".format(discussion["number"]))
        metadata = (f'---\n'
                    f'title: {discussion["title"]}\n'
                    f'slug: {slug}/\n'
                    f'number: {str(discussion["number"])}\n'
                    f'url: {discussion["url"]}\n'
                    f'created: {discussion["createdAt"][0:10]}\n'
                    f'updated: {discussion["updatedAt"][0:10]}\n'
                    f'authors: [{discussion["author"]["login"]}]\n'
                    f'categories: \n'
                    f'  - {discussion["category"]["name"]}\n'
                    f'labels: {[label["name"] for label in discussion["labels"]["nodes"]] if discussion["labels"]["nodes"] else []}\n'
                    f'comments: {_is_comment_close(discussion)}\n'
                    f'---\n\n')
    return metadata


def converter(discussions_data, nav_data, out_dir):
    # 处理所有的 discussions
    if 'nodes' in discussions_data.keys():
        discussions_list = discussions_data['nodes']
        for discussion in discussions_list:
            if not discussion:
                print("Null discussion!")
                continue
            
            md_path = _md_directory_generator(discussion=discussion, nav=nav_data)

            category_num = discussion['category']['name'][:2]
            if int(category_num) == 0: # site pages
                md_filename = _md_filename_generator(discussion, MdType.SPECIFIC)
            else:
                md_filename = _md_filename_generator(discussion, MdType.PRESET)
            
            md_metadata = _md_meta_generator(discussion=discussion, md_name=md_filename, md_path=md_path)
            discussion_body = discussion["body"]
            saved_dir = Path(out_dir).joinpath(md_path)
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


def _main():
    parser = argparse.ArgumentParser()
    parser.description = "Convert the discussions file to markdown"
    parser.add_argument("-i", "--input", help="Discussions input file", dest="input", default="discussions")
    parser.add_argument("-o", "--output", help="Markdown files directory", dest="output", required=True)
    parser.add_argument("-n", "--navigation", help="Navigation file", dest="navigation", required=True)
    args = parser.parse_args()

    input_file = args.input
    nav_file_path = args.navigation
    out_dir = args.output
    
    with open(nav_file_path, "r", encoding="utf-8") as f:
        nav_data = json.load(f)
    with open(input_file, "r", encoding="utf-8") as f:
        discussions_data = eval(f.read())
    
    # handle Exception
    if nav_data is None or discussions_data is None:
        raise FileException("Navigation file or disscussions file null")
    
    converter(discussions_data=discussions_data, nav_data=nav_data, out_dir=out_dir)


if __name__ == "__main__":
    # unittest.main()
    _main()
    
