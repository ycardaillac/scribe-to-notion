"""Integration test for Notion page creation."""

import os
import pytest
from scribe_to_notion.adapters.notion_client import NotionClient
from tests.integration.config import NOTION_API_TOKEN, PARENT_PAGE_ID


def test_create_page_with_real_api():
    """Test creating a page with the real Notion API."""
    # Set the API token
    os.environ["NOTION_API_TOKEN"] = NOTION_API_TOKEN

    client = NotionClient()

    # Test creating a simple page
    page_id = client.create_page(
        parent_id=PARENT_PAGE_ID,
        title="Test Page from Scribe to Notion",
        content="This is a test page created by our integration test.",
    )

    # Verify we got a page ID back
    assert page_id is not None
    assert isinstance(page_id, str)
    assert len(page_id) > 0

    print(f"✅ Successfully created page with ID: {page_id}")
    print(f"🔗 You can view it at: https://notion.so/{page_id.replace('-', '')}")

    # Clean up - delete the page we just created
    try:
        success = client.delete_page(page_id)
        if success:
            print(f"🗑️ Successfully deleted test page: {page_id}")
        else:
            print(f"❌ Failed to delete test page: {page_id}")
    except Exception as e:
        print(f"❌ Error deleting test page {page_id}: {e}")


def test_create_and_delete_page_without_content():
    """Test creating a page without content and then deleting it."""
    os.environ["NOTION_API_TOKEN"] = NOTION_API_TOKEN

    client = NotionClient()

    page_id = client.create_page(
        parent_id=PARENT_PAGE_ID, title="Empty Test Page", content=""
    )

    assert page_id is not None
    assert isinstance(page_id, str)

    print(f"✅ Successfully created empty page with ID: {page_id}")

    # Clean up - delete the page we just created
    try:
        success = client.delete_page(page_id)
        if success:
            print(f"🗑️ Successfully deleted empty test page: {page_id}")
        else:
            print(f"❌ Failed to delete empty test page: {page_id}")
    except Exception as e:
        print(f"❌ Error deleting empty test page {page_id}: {e}")
