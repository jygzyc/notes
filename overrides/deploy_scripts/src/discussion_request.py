import requests
import json
from mkdocs.utils import meta 
from mkdocs.structure.files import Files
from mkdocs.structure.files import File
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from .discussion_graphql import DiscussionGraphql

class DiscussionRequest:

    discussions_data: dict

    def __init__(self, github_repo: str, github_token: str):
        self.gh_repo = github_repo
        self.gh_token = github_token
        self.gh_owner = self.gh_repo.split("/")[0]
        self.gh_repo_name = self.gh_repo.split("/")[-1]
        self.discussions_data = self.query_discussions()

    def _request(self, query: str):
        headers = {
            "Authorization": f"Bearer {self.gh_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        url = "https://api.github.com/graphql"
        response = requests.post(url=url, headers=headers, json={"query": query})
        return response.json()

    def query_discussions(self) -> dict:
        try:
            has_next_page = True
            all_discussions = []
            end_cursor = ""
            while has_next_page:
                query = DiscussionGraphql.make_query_discussions(
                    gh_owner=self.gh_owner, 
                    gh_repo_name=self.gh_repo_name,
                    end_cursor=end_cursor
                )
                results = self._request(query).get("data", "").get("repository", "").get("discussions", "")
                temp_discussion = results['nodes']
                has_next_page = results['pageInfo']['hasNextPage']
                end_cursor = results['pageInfo']['endCursor']
                all_discussions.extend(temp_discussion)

            beijing_tz = ZoneInfo('Asia/Shanghai')
            beijing_time = datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")
            discussions_with_timestamp = {'date': str(beijing_time), 'nodes': all_discussions}
            print(f"[*] Query {self.gh_repo} discussions successfully!")
            return discussions_with_timestamp
        except Exception as e:
            print(f"[x] Query discussions Error: {str(e)}")
    
    def update_discussion(self, markdown_path: Path) -> any:
        try:
            results = None
            with open(markdown_path, encoding="utf-8-sig", errors="strict") as f:
                source = f.read()
            file_content, file_meta = meta.get_data(source)
            escased_body = json.dumps(file_content, ensure_ascii=False, indent=None)
            discussion_number = file_meta.get("number")
            discussion_id = ""
            category_id = ""
            discussion_nodes = self.discussions_data.get("nodes", [])
            for item in discussion_nodes:
                if item["number"] == int(discussion_number):
                    discussion_id = item["id"]
                    category_id = item["category"]["id"]
                    original_body = item["body"]
                    break
            if json.dumps(original_body, ensure_ascii=False, indent=None) != escased_body:
                query = DiscussionGraphql.update_discussion(discussionId=discussion_id,
                                                            body=escased_body,
                                                            title=file_meta.get("title"),
                                                            categoryId=category_id)
                results = self._request(query)
                print(f"[*] Update discussion {str(markdown_path)} successfully!")
            return results
        except Exception as e:
            raise e

