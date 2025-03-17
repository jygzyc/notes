import unittest
from pathlib import Path

from src.file_converter import DiscussionConverter

class TestConverterMethods(unittest.TestCase):

    def setUp(self):
        test_out_dir = Path(__file__).parent.joinpath("test_out") 
        test_discussions_file = Path(__file__).parent.joinpath("test_discussions")
        with open(test_discussions_file, "r", encoding="utf-8") as f:
            discussions_data = eval(f.read())
        if discussions_data is None:
            assert "Navigation file or disscussions file null"
        self.discussion_converter = DiscussionConverter(discussions_data=discussions_data, out_dir=test_out_dir)

    def test__path_preprocess(self):
        self.assertEqual(self.discussion_converter._path_preprocess(" blog.posts "), "blog/posts/")       # 首尾空格去除
        self.assertEqual(self.discussion_converter._path_preprocess("a.b.c.d/"), "a/b/c/d/")             # 多层目录转换
        self.assertEqual(self.discussion_converter._path_preprocess("  "), "/")
        self.assertEqual(self.discussion_converter._path_preprocess(" . "), ".")                     # 空输入处理