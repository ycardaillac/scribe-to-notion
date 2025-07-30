"""Notion page adapter implementation."""

import os
from typing import Optional, Dict, Any, List
from notion_client import Client

from ..core.interfaces import PagePublisherRepository


class NotionPageAdapter(PagePublisherRepository):
    """Notion implementation of PagePublisherRepository."""

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
            # Split content into chunks if it's too long
            content_blocks = self._split_content_into_blocks(content)

            response = self.client.pages.create(
                parent={"page_id": parent_id},
                properties={"title": {"title": [{"text": {"content": title}}]}},
                children=content_blocks,
            )
            return response["id"]
        except Exception as e:
            raise Exception(f"Failed to create page: {e}")

    def _split_content_into_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Split content into blocks that fit Notion's character limits."""
        if not content:
            return []

        # Notion has a 2000 character limit per text block
        MAX_CHARACTERS = 2000

        blocks = []
        lines = content.split("\n\n")

        current_block: List[str] = []
        current_length = 0

        for line in lines:
            line_with_separator = line + "\n\n"
            line_length = len(line_with_separator)

            # If adding this line would exceed the limit, create a new block
            if current_length + line_length > MAX_CHARACTERS and current_block:
                blocks.append(self._create_paragraph_block("\n\n".join(current_block)))
                current_block = [line]
                current_length = line_length
            else:
                current_block.append(line)
                current_length += line_length

        # Add the last block
        if current_block:
            blocks.append(self._create_paragraph_block("\n\n".join(current_block)))

        return blocks

    def _create_paragraph_block(self, text: str) -> Dict[str, Any]:
        """Create a paragraph block with the given text."""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }

    def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Get a page by ID. Returns None if page doesn't exist."""
        try:
            return self.client.pages.retrieve(page_id)
        except Exception:
            return None

    def get_page_content(self, page_id: str) -> Optional[str]:
        """Get the content of a page as a string."""
        try:
            # Get the page blocks
            blocks = self.client.blocks.children.list(page_id)

            content_parts = []
            for block in blocks.get("results", []):
                if block.get("type") == "paragraph":
                    rich_text = block.get("paragraph", {}).get("rich_text", [])
                    block_content = ""
                    for text in rich_text:
                        block_content += text.get("text", {}).get("content", "")
                    if block_content:
                        content_parts.append(block_content)

            # Join with double newlines to preserve the original structure
            return "\n\n".join(content_parts)
        except Exception:
            return None

    def delete_page(self, page_id: str) -> bool:
        """Delete a page in Notion."""
        try:
            self.client.pages.update(page_id, archived=True)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete page: {e}")

    def page_exists(self, page_id: str) -> bool:
        """Check if a page exists (not archived)."""
        page = self.get_page(page_id)
        return page is not None and not page.get("archived", False)
