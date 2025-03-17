# -*- coding:utf-8 -*-
import argparse
from pathlib import Path
from src.file_converter import DiscussionConverter
from src.discussion_request import DiscussionRequest

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.description = 'Github discussion Mkdocs converter'
    parser.add_argument("-r", "--repo", help="GitHub repository name with namespace", dest="repo", required=True)
    parser.add_argument("-t", "--token", help="GitHub access token", dest="token", required=True)
    parser.add_argument("-o", "--output", help="Markdown files directory", dest="output", required=True)
    return parser.parse_args()

def main():
    args = arg_parse()
    gh_repo: str = args.repo
    gh_token: str = args.token
    out_dir = Path(args.output)
    try:
        # Step 1: Get all discussions
        discussion_request = DiscussionRequest(gh_repo, gh_token)
        discussions_data = discussion_request.discussions_data
        with open("discussions" , "w", encoding='utf-8') as f:
            f.write(str(discussions_data))

        # Step 2: Confirm whether it is a local update
        discussion_converter = DiscussionConverter(discussions_data=discussions_data, out_dir=out_dir)
        if discussion_converter.local_lock:
            for md_file in out_dir.rglob("*.md"):
                discussion_request.update_discussion(md_file)
            Path(out_dir.joinpath("discussions")).unlink()
        else:
            discussion_converter.sync_remote()
    except Exception as e:
        print(f"[x] Main Error: {str(e)}")

if __name__ == "__main__":
    main()