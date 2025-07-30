"""Tests for the import service."""

import pytest
from unittest.mock import Mock

from scribe_to_notion.core.models import Clipping
from scribe_to_notion.services.import_service import ImportService


class TestImportService:
    """Test the ImportService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_page_publisher = Mock()
        self.mock_clipping_repo = Mock()
        self.service = ImportService(self.mock_page_publisher, self.mock_clipping_repo)

    def test_import_clippings_creates_pages_for_each_book(self):
        """Test that import creates pages for each book."""
        # Arrange
        mock_clippings = [
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="surlignement",
                page="10",
                location=None,
                date="test date",
                content="Highlight 1",
            ),
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="surlignement",
                page="15",
                location=None,
                date="test date",
                content="Highlight 2",
            ),
            Clipping(
                book_title="Book 2",
                author="Author 2",
                clipping_type="surlignement",
                page="5",
                location=None,
                date="test date",
                content="Highlight 3",
            ),
            # This should be filtered out (not a highlight)
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="note",
                page="20",
                location=None,
                date="test date",
                content="Note 1",
            ),
        ]

        self.mock_clipping_repo.get_clippings.return_value = mock_clippings
        self.mock_page_publisher.create_page.side_effect = ["page_id_1", "page_id_2"]

        # Act
        result = self.service.import_clippings("test_file.txt", "parent_id")

        # Assert
        assert len(result) == 2
        assert "Book 1" in result
        assert "Book 2" in result
        assert result["Book 1"] == ["page_id_1"]
        assert result["Book 2"] == ["page_id_2"]

        # Verify the service called the repositories correctly
        self.mock_clipping_repo.get_clippings.assert_called_once_with("test_file.txt")
        assert self.mock_page_publisher.create_page.call_count == 2

        # Verify page creation calls
        calls = self.mock_page_publisher.create_page.call_args_list
        assert calls[0][1]["title"] == "Book 1"
        assert calls[0][1]["parent_id"] == "parent_id"
        assert calls[1][1]["title"] == "Book 2"
        assert calls[1][1]["parent_id"] == "parent_id"

    def test_highlights_are_sorted_by_page_number(self):
        """Test that highlights are sorted by page number."""
        # Arrange
        mock_clippings = [
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="surlignement",
                page="15",
                location=None,
                date="test date",
                content="Highlight 2",
            ),
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="surlignement",
                page="5",
                location=None,
                date="test date",
                content="Highlight 1",
            ),
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="surlignement",
                page="10",
                location=None,
                date="test date",
                content="Highlight 3",
            ),
        ]

        self.mock_clipping_repo.get_clippings.return_value = mock_clippings
        self.mock_page_publisher.create_page.return_value = "page_id"

        # Act
        self.service.import_clippings("test_file.txt", "parent_id")

        # Assert - verify content is sorted by page number
        call_args = self.mock_page_publisher.create_page.call_args
        content = call_args[1]["content"]

        # Content should have highlights in page order: 5, 10, 15
        assert '"Highlight 1" (p.5)' in content
        assert '"Highlight 3" (p.10)' in content
        assert '"Highlight 2" (p.15)' in content

        # Check order
        lines = content.split("\n\n")
        assert "Highlight 1" in lines[0]
        assert "Highlight 3" in lines[1]
        assert "Highlight 2" in lines[2]

    def test_only_highlights_are_imported(self):
        """Test that only highlights (surlignement) are imported."""
        # Arrange
        mock_clippings = [
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="surlignement",
                page="10",
                location=None,
                date="test date",
                content="Highlight",
            ),
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="note",
                page="10",
                location=None,
                date="test date",
                content="Note",
            ),
            Clipping(
                book_title="Book 1",
                author="Author 1",
                clipping_type="signet",
                page="10",
                location=None,
                date="test date",
                content="Bookmark",
            ),
        ]

        self.mock_clipping_repo.get_clippings.return_value = mock_clippings
        self.mock_page_publisher.create_page.return_value = "page_id"

        # Act
        result = self.service.import_clippings("test_file.txt", "parent_id")

        # Assert
        assert len(result) == 1
        assert "Book 1" in result

        # Verify only highlight content is in the page
        call_args = self.mock_page_publisher.create_page.call_args
        content = call_args[1]["content"]
        assert "Highlight" in content
        assert "Note" not in content
        assert "Bookmark" not in content
