import unittest
import json
import os
from pathlib import Path
from ..src.discussion_request import DiscussionRequest

class TestDiscussionRequest(unittest.TestCase):
    def setUp(self):

        with open(Path(__file__).parent.joinpath("test_config.json"), "r") as f:
            self.test_config = json.load(f)
        self.discussion_request = DiscussionRequest(
            github_repo=self.test_config.get("test_github_repo"),
            github_token=self.test_config.get("test_github_token")
        )

    def test_query_discussions(self):
        result = self.discussion_request.query_discussions()
        self.assertIsNotNone(result)

    def test_update_discussion_change(self):
        current_dir = os.getcwd()
        print(f"[D] target md path: {Path(current_dir) / self.test_config.get("test_md_path")}")
        result = self.discussion_request.update_discussion(
            markdown_path=Path(current_dir) / self.test_config.get("test_md_path")
        )
        self.assertIsNotNone(result)
    def test_update_discussion_unchange(self):
        current_dir = os.getcwd()
        print(f"[D] target md path: {Path(current_dir) / self.test_config.get("test_unchanged_md_path")}")
        result = self.discussion_request.update_discussion(
            markdown_path=Path(current_dir) / self.test_config.get("test_unchanged_md_path")
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()