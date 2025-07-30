"""Core interfaces for external dependencies."""

from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Clipping


class ClippingRepository(ABC):
    """Interface for clipping operations."""

    @abstractmethod
    def get_clippings(self, source: str) -> List[Clipping]:
        """Get clippings from a source (file path, URL, etc.)."""
        pass


class PagePublisherRepository(ABC):
    """Interface for publishing pages to any system (Notion, Obsidian, etc.)."""

    @abstractmethod
    def create_page(self, parent_id: str, title: str, content: str = "") -> str:
        """Create a new page and return its ID."""
        pass

    @abstractmethod
    def get_page_content(self, page_id: str) -> Optional[str]:
        """Get the content of a page as a string."""
        pass

    @abstractmethod
    def page_exists(self, page_id: str) -> bool:
        """Check if a page exists."""
        pass

    @abstractmethod
    def delete_page(self, page_id: str) -> bool:
        """Delete a page."""
        pass
