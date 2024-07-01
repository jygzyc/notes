# -*- coding:utf-8 -*-

from enum import Enum, unique
from pathlib import Path
import unittest
import argparse
import json
import re
import os

from slugify import slugify

########################
# Comment Configuration
########################
closed_comments_list = [5]

def _is_comment_open(discussion: dict):
    """
    Check if comments are open for a given discussion.
    
    Parameters:
    - discussion (dict): A dictionary representing the discussion object,
                        which must include a 'number' key.
    
    Returns:
    - str: "false" if the discussion number is in the closed_comments_list,
           or "true" otherwise.
    
    Description:
    This function determines whether comments should be open or closed for a
    specific discussion based on its number. It checks if the discussion number
    is present in the closed_comments_list. If it is, the function returns "false",
    indicating that comments are closed. If not, it returns "true", indicating
    that comments are open.
    """
    number = discussion["number"]
    return "false" if number in closed_comments_list else "true"


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
            assert "discussion test data error"
        with open("nav.json", "r", encoding="utf-8") as f:
            self.nav_data = json.load(f)
        if not self.nav_data:
            assert "nav_data test error"

    def test__md_filename_generator(self):
        if 'nodes' in self.discussions_data.keys():
            discussions_list = self.discussions_data['nodes']
            for discussion in discussions_list:
                if not discussion:
                    continue
                discussion_title = discussion['title']
                if discussion_title == "留言板":
                    self.assertEqual(_md_filename_generator(discussion, MdType.SPECIFIC), "site-message.md")
                if discussion_title == "JavaScript基础":
                    self.assertEqual(_md_filename_generator(discussion, MdType.PRESET), "javascript-base.md")

    def test__md_directory_generator(self):
        if 'nodes' in self.discussions_data.keys():
            discussions_list = self.discussions_data['nodes']
            for discussion in discussions_list:
                if not discussion:
                    continue
                discussion_title = discussion['title']
                if discussion_title == "留言板":
                    self.assertEqual(_md_directory_generator(discussion, self.nav_data), ".")
                if discussion_title == "JavaScript基础":
                    self.assertEqual(_md_directory_generator(discussion, self.nav_data), "technology/program/js/") 

    def test__md_meta_generator(self):
        if 'nodes' in self.discussions_data.keys():
            discussions_list = self.discussions_data['nodes']
            for discussion in discussions_list:
                if not discussion:
                    continue
                discussion_title = discussion['title']
                if discussion_title == "留言板":
                    print(_md_meta_generator(discussion, 
                                             _md_filename_generator(discussion, flag=MdType.SPECIFIC),
                                             _md_directory_generator(discussion, self.nav_data)))
                if discussion_title == "JavaScript基础":
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
    Generate a markdown directory path based on navigation and discussion object.
    
    Parameters:
    - discussion: A dictionary containing information about the github discussion.
    - nav: A json mapping numerical prefixes to their corresponding
                       directory paths.
    
    Returns:
    - str or None or False: The generated markdown directory path if found, or return 
                        None. When the exception occurs, return False.
    
    Description:
    This function determines the appropriate directory for a markdown file based on
    the discussion's category name and labels. It uses regular expressions to extract
    numerical prefixes and then looks up the corresponding directory path in the
    provided navigation dictionary.
    """
    try:
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
    except Exception:
        return False

def _md_meta_generator(discussion: dict, md_name, md_path):
    """
    Generate markdown metadata for a given discussion object.
    
    Parameters:
    - discussion: A dictionary containing information about the github discussion.
    - md_name: Markdown file name generated by `_md_filename_generator()` function.
    - md_path: Markdown file path generated by `_md_directory_generator()` function
    
    Returns:
    - str: A string of markdown formatted metadata.
    
    Description:
    This function creates markdown metadata (YAML front matter) for a discussion object.
    It constructs the metadata based on the category number of the discussion. The category
    number determines the structure and content of the metadata.
    """
    category_num_prefix = discussion['category']['name'][:2]
    md_name, _ = os.path.splitext(os.path.basename(md_name)) #if md_name[-3:] == ".md" else md_name
    
    if int(category_num_prefix) == 0:
        # generate site pages metadata
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
                    f'comments: {_is_comment_open(discussion)}\n'
                    f'---\n\n')
    elif int(category_num_prefix) == 9:
        # generate blog pages metadata
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
                    f'authors: [Ecool]\n'
                    f'categories: \n'
                    f'  - {discussion["category"]["name"]}\n'
                    f'labels: {[label["name"] for label in discussion["labels"]["nodes"]] if discussion["labels"]["nodes"] else []}\n'
                    f'comments: {_is_comment_open(discussion)}\n'
                    f'---\n\n')
    else:
        # generate common pages metadata
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
                    f'comments: {_is_comment_open(discussion)}\n'
                    f'---\n\n')
    return metadata


def converter(discussions_data, nav_data, out_dir):
    # handle all discussions
    if 'nodes' in discussions_data.keys():
        discussions_list = discussions_data['nodes']
        for discussion in discussions_list:
            if not discussion:
                print("Null discussion!")
                continue

            # When the generation of the markdown file path fails, proceed to the next one.
            md_path = _md_directory_generator(discussion=discussion, nav=nav_data)
            if not md_path:
                print("[*] Path: {} skip processing".format(discussion['category']['name']))
                continue
            category_num = discussion['category']['name'][:2]

            # Only site pages use the label to generate the file name; the rest generate 
            # the file name based on the first comment in the discussion content.
            if int(category_num) == 0:
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
        assert "Navigation file or disscussions file null"
    
    converter(discussions_data=discussions_data, nav_data=nav_data, out_dir=out_dir)


if __name__ == "__main__":
    # unittest.main()
    _main()
    
