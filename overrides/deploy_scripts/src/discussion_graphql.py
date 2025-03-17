# -*- coding:utf-8 -*-
from datetime import datetime
from zoneinfo import ZoneInfo

class DiscussionGraphql:

    @staticmethod
    def get_categories(
        gh_owner: str, 
        gh_repo_name: str
    ) -> str:
        query = f"""
        query{{
            repository(owner: {gh_owner}, name: {gh_repo_name}){{
                discussionCategories(first: 25){{
                    nodes {{
                        id
                        name
                        description
                    }}
                }}
            }}
        }}
        """
        return query

    @staticmethod
    def update_discussion(
        discussionId: str,
        body: str,
        title: str,
        categoryId: str
    ) -> str:
        query = f"""
        mutation {{
            updateDiscussion(
                input: {{
                    discussionId: {discussionId}, 
                    body: {body}, 
                    title: {title},
                    categoryId: {categoryId}
                }}) 
            {{
                discussion {{
                    id
                }}
            }}
        }}
        """
        return query

    @staticmethod
    def make_query_discussions(
        gh_owner: str,
        gh_repo_name: str,
        end_cursor: str
    ) -> str:
        after_endCursor = ""
        if end_cursor:
            after_endCursor = 'after: "{}"'.format(end_cursor)
        query=f"""
        query {{
            repository(owner:"{gh_owner}", name:"{gh_repo_name}"){{
                discussions(
                    orderBy: {{field: CREATED_AT, direction: DESC}}
                    first: 5
                    {after_endCursor}) 
                {{
                    nodes {{
                        id
                        title
                        number
                        url
                        createdAt
                        lastEditedAt
                        updatedAt
                        body
                        bodyText
                        author{{
                            login
                        }}
                        category {{
                            id
                            name
                            description
                        }}
                        labels (first: 100) {{
                            nodes {{
                                name
                                description
                                color
                            }}
                        }}
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
        """
        return query


