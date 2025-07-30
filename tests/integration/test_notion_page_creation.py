"""Integration test for Notion page creation."""

import os
import pytest
from scribe_to_notion.adapters.notion_page_adapter import NotionPageAdapter
from tests.integration.config import NOTION_API_TOKEN, PARENT_PAGE_ID


def test_create_page_with_real_api():
    """Test creating a page with the real Notion API."""
    # Set the API token
    os.environ["NOTION_API_TOKEN"] = NOTION_API_TOKEN

    client = NotionPageAdapter()

    # Test creating a simple page
    expected_content = "This is a test page created by our integration test."
    page_id = client.create_page(
        parent_id=PARENT_PAGE_ID,
        title="Test Page from Scribe to Notion",
        content=expected_content,
    )

    # Verify we got a page ID back
    assert page_id is not None
    assert isinstance(page_id, str)
    assert len(page_id) > 0

    # Verify the page exists
    assert client.page_exists(page_id), "Page should exist after creation"

    # Verify the page content is correct
    actual_content = client.get_page_content(page_id)
    assert (
        actual_content == expected_content
    ), f"Expected content '{expected_content}', got '{actual_content}'"

    # Clean up - delete the page we just created
    try:
        success = client.delete_page(page_id)
        assert success, "Page deletion should succeed"
        print(f"Successfully deleted test page: {page_id}")
    except Exception as e:
        print(f"Error deleting test page {page_id}: {e}")
        raise

    # Verify the page no longer exists
    assert not client.page_exists(page_id), "Page should not exist after deletion"


def test_create_and_delete_page_without_content():
    """Test creating a page without content and then deleting it."""
    os.environ["NOTION_API_TOKEN"] = NOTION_API_TOKEN

    client = NotionPageAdapter()

    page_id = client.create_page(
        parent_id=PARENT_PAGE_ID, title="Empty Test Page", content=""
    )

    assert page_id is not None
    assert isinstance(page_id, str)

    # Verify the page exists
    assert client.page_exists(page_id), "Page should exist after creation"

    # Verify the page content is empty
    actual_content = client.get_page_content(page_id)
    assert actual_content == "", f"Expected empty content, got '{actual_content}'"

    # Clean up - delete the page we just created
    try:
        success = client.delete_page(page_id)
        assert success, "Page deletion should succeed"
        print(f"Successfully deleted empty test page: {page_id}")
    except Exception as e:
        print(f"Error deleting empty test page {page_id}: {e}")
        raise

    # Verify the page no longer exists
    assert not client.page_exists(page_id), "Page should not exist after deletion"
