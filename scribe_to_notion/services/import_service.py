"""Service for importing clippings to any page publishing system."""

from typing import List, Dict

from ..core.interfaces import PagePublisherRepository, ClippingRepository
from ..core.models import Clipping


class ImportService:
    """Service for importing clippings to any page publishing system."""

    def __init__(
        self, page_publisher: PagePublisherRepository, clipping_repo: ClippingRepository
    ):
        """Initialize the import service with dependencies."""
        self.page_publisher = page_publisher
        self.clipping_repo = clipping_repo

    def import_clippings(
        self, clippings_source: str, parent_page_id: str
    ) -> Dict[str, List[str]]:
        """
        Import clippings from a source to any page publishing system.

        Returns a dictionary with book titles as keys and lists of created page IDs as values.
        """
        # Get clippings from source
        clippings = self.clipping_repo.get_clippings(clippings_source)

        # Filter only highlights
        highlights = [c for c in clippings if c.clipping_type == "surlignement"]

        # Group by book
        books = self._group_by_book(highlights)

        # Create pages for each book
        results = {}
        for book_title, book_highlights in books.items():
            page_id = self._create_book_page(
                book_title, book_highlights, parent_page_id
            )
            results[book_title] = [page_id]

        return results

    def _group_by_book(self, clippings: List[Clipping]) -> Dict[str, List[Clipping]]:
        """Group clippings by book title."""
        books: Dict[str, List[Clipping]] = {}
        for clipping in clippings:
            if clipping.book_title not in books:
                books[clipping.book_title] = []
            books[clipping.book_title].append(clipping)
        return books

    def _create_book_page(
        self, book_title: str, highlights: List[Clipping], parent_page_id: str
    ) -> str:
        """Create a page for a book with its highlights."""
        # Sort highlights by page number
        sorted_highlights = sorted(
            highlights, key=lambda h: self._extract_page_number(h.page or "")
        )

        # Format content
        content_lines = []
        for highlight in sorted_highlights:
            page_info = f" (p.{highlight.page})" if highlight.page else ""
            content_lines.append(f'"{highlight.content}"{page_info}')

        content = "\n\n".join(content_lines)

        # Create the page
        return self.page_publisher.create_page(
            parent_id=parent_page_id, title=book_title, content=content
        )

    def _extract_page_number(self, page_str: str) -> int:
        """Extract page number for sorting."""
        if not page_str:
            return 0

        # Handle ranges like "12-12" by taking the first number
        try:
            return int(page_str.split("-")[0])
        except (ValueError, IndexError):
            return 0
