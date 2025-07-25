"""Core domain models for Scribe clippings."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Clipping:
    """Represents a single clipping from Amazon Scribe/Kindle."""

    book_title: str
    author: Optional[str]
    clipping_type: str  # "surlignement", "note", "signet"
    page: Optional[str]
    location: Optional[str]
    date: str  # Keep the original French date string
    content: str

    def __post_init__(self):
        """Clean up the data after initialization."""
        # Remove BOM characters and strip whitespace
        self.book_title = self.book_title.strip().replace("\ufeff", "")
        self.content = self.content.strip()

        # Clean up optional fields
        if self.author:
            self.author = self.author.strip()
        if self.page:
            self.page = self.page.strip()
        if self.location:
            self.location = self.location.strip()
