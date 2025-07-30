"""Integration test for the import service."""

import os
import pytest
from scribe_to_notion.adapters.notion_page_adapter import NotionPageAdapter
from scribe_to_notion.adapters.file_clipping_adapter import FileClippingAdapter
from scribe_to_notion.services.import_service import ImportService
from tests.integration.config import NOTION_API_TOKEN, PARENT_PAGE_ID


def test_import_clippings_integration():
    """Test the full import workflow with real repositories."""
    # Set up the API token
    os.environ["NOTION_API_TOKEN"] = NOTION_API_TOKEN

    # Create real adapters
    page_publisher = NotionPageAdapter()
    clipping_adapter = FileClippingAdapter()

    # Create the service with real dependencies
    service = ImportService(page_publisher, clipping_adapter)

    # Import clippings from the test file
    clippings_file = "tests/unit/My Clippings.txt"
    result = service.import_clippings(clippings_file, PARENT_PAGE_ID)

    # Verify we got results
    assert len(result) > 0, "Should have imported at least one book"

    # Store created page IDs for cleanup
    created_page_ids = []
    for book_title, page_ids in result.items():
        created_page_ids.extend(page_ids)
        print(f"✅ Created page for '{book_title}' with ID: {page_ids[0]}")

    # Verify pages exist and have content
    for page_id in created_page_ids:
        assert page_publisher.page_exists(page_id), f"Page {page_id} should exist"

        content = page_publisher.get_page_content(page_id)
        assert content is not None, f"Page {page_id} should have content"
        assert len(content) > 0, f"Page {page_id} should not be empty"

        print(f"📄 Page {page_id} content length: {len(content)} characters")

    # Verify content matches clippings
    verify_imported_content(clipping_adapter, page_publisher, result)

    # Clean up - delete all created pages
    for page_id in created_page_ids:
        try:
            success = page_publisher.delete_page(page_id)
            if success:
                print(f"🗑️ Successfully deleted page: {page_id}")
            else:
                print(f"❌ Failed to delete page: {page_id}")
        except Exception as e:
            print(f"❌ Error deleting page {page_id}: {e}")

    # Verify pages no longer exist
    for page_id in created_page_ids:
        assert not page_publisher.page_exists(
            page_id
        ), f"Page {page_id} should not exist after deletion"

    print(f"🧹 Cleaned up {len(created_page_ids)} test pages")


def verify_imported_content(clipping_adapter, page_publisher, result):
    """Verify that the imported content matches the original clippings."""
    clippings_file = "tests/unit/My Clippings.txt"
    all_clippings = clipping_adapter.get_clippings(clippings_file)

    # Group clippings by book
    clippings_by_book = {}
    for clipping in all_clippings:
        if clipping.clipping_type == "surlignement":  # Only highlights
            if clipping.book_title not in clippings_by_book:
                clippings_by_book[clipping.book_title] = []
            clippings_by_book[clipping.book_title].append(clipping)

    # Debug: Print all highlights found
    for book_title, highlights in clippings_by_book.items():
        print(f"\n🔍 Debug - Book: '{book_title}'")
        print(f"   Found {len(highlights)} highlights:")
        for i, highlight in enumerate(highlights, 1):
            print(f"   {i}. Page {highlight.page}: '{highlight.content[:50]}...'")

    # Verify each book
    for book_title, page_ids in result.items():
        page_id = page_ids[0]  # We only create one page per book

        # Get the highlights for this book
        book_highlights = clippings_by_book.get(book_title, [])
        expected_highlight_count = len(book_highlights)

        # Get the content from Notion
        notion_content = page_publisher.get_page_content(page_id)
        assert notion_content is not None, f"Page {page_id} should have content"

        # Count the highlights in Notion content (each highlight is on a separate line)
        notion_highlight_lines = [
            line.strip() for line in notion_content.split("\n\n") if line.strip()
        ]
        actual_highlight_count = len(notion_highlight_lines)

        print(f"\n📊 Book: '{book_title}'")
        print(f"   Expected highlights: {expected_highlight_count}")
        print(f"   Actual highlights: {actual_highlight_count}")
        print(f"   Content preview: {notion_content[:100]}...")

        # Debug: Print actual Notion content lines
        print(f"   Notion content lines:")
        for i, line in enumerate(notion_highlight_lines, 1):
            print(f"   {i}. {line[:50]}...")

        # Verify the counts match
        assert (
            actual_highlight_count == expected_highlight_count
        ), f"Book '{book_title}': Expected {expected_highlight_count} highlights, got {actual_highlight_count}"

        # Verify each highlight content is present
        for highlight in book_highlights:
            expected_text = f'"{highlight.content}"'
            if highlight.page:
                expected_text += f" (p.{highlight.page})"

            assert (
                expected_text in notion_content
            ), f"Highlight '{expected_text}' not found in Notion content for book '{book_title}'"

        print(
            f"   ✅ All {expected_highlight_count} highlights verified for '{book_title}'"
        )

    print(f"🎯 Content verification complete for {len(result)} books")
