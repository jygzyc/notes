import unittest
import json
from pathlib import Path
from src.discussion_request import DiscussionRequest
from src.discussion_graphql import DiscussionGraphql

class TestDiscussionRequest(unittest.TestCase):
    def setUp(self):

        with open(Path(__file__).parent.joinpath("test_config.json"), "r") as f:
            test_config = json.load(f)
        self.discussion_request = DiscussionRequest(
            github_repo=test_config.get("test_github_repo"),
            github_token=test_config.get("test_github_token")
        )
    
    def test_query_discussions(self):
        result = self.discussion_request.query_discussions()
        self.assertIsNotNone(result)
