"""Notion API client adapter."""

import os
from typing import Optional
from notion_client import Client


class NotionClient:
    """Simple Notion API client for page creation."""

    def __init__(self, api_token: Optional[str] = None):
        """Initialize the Notion client."""
        self.api_token = api_token or os.getenv("NOTION_API_TOKEN")

        if not self.api_token:
            raise ValueError(
                "Notion API token is required. Set NOTION_API_TOKEN environment variable."
            )

        self.client = Client(auth=self.api_token)

    def create_page(self, parent_id: str, title: str, content: str = "") -> str:
        """Create a new page in Notion."""
        try:
            response = self.client.pages.create(
                parent={"page_id": parent_id},
                properties={"title": {"title": [{"text": {"content": title}}]}},
                children=(
                    [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": content}}
                                ]
                            },
                        }
                    ]
                    if content
                    else []
                ),
            )
            return response["id"]
        except Exception as e:
            raise Exception(f"Failed to create page: {e}")

    def delete_page(self, page_id: str) -> bool:
        """Delete a page in Notion."""
        try:
            self.client.pages.update(page_id, archived=True)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete page: {e}")
