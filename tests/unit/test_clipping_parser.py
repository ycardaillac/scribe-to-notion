"""Tests for the clipping parser."""

import pytest
from pathlib import Path
from scribe_to_notion.core.models import Clipping
from scribe_to_notion.core.parser import ClippingParser


def test_clipping_model_creation():
    """Test that we can create a Clipping object."""
    clipping = Clipping(
        book_title="The Hard Thing About Hard Things",
        author=None,
        clipping_type="surlignement",
        page="12-12",
        location=None,
        date="dimanche 18 mai 2025 12:48:14",
        content="was also on the highest academic track in math",
    )

    assert clipping.book_title == "The Hard Thing About Hard Things"
    assert clipping.clipping_type == "surlignement"
    assert clipping.page == "12-12"
    assert clipping.content == "was also on the highest academic track in math"


def test_clipping_model_cleans_bom_characters():
    """Test that BOM characters are automatically cleaned."""
    clipping = Clipping(
        book_title="\ufeffThe Hard Thing About Hard Things",
        author=None,
        clipping_type="surlignement",
        page="12-12",
        location=None,
        date="dimanche 18 mai 2025 12:48:14",
        content="test content",
    )
    assert clipping.book_title == "The Hard Thing About Hard Things"
    assert "\ufeff" not in clipping.book_title


def test_clipping_model_with_author():
    """Test clipping with author information."""
    clipping = Clipping(
        book_title="Sauve-moi (French Edition) (Musso, Guillaume)",
        author="Musso, Guillaume",
        clipping_type="surlignement",
        page="7",
        location="emplacement 58-59",
        date="dimanche 18 mai 2025 12:34:30",
        content="Juliette frissonna en écoutant ces nouvelles.",
    )

    assert clipping.book_title == "Sauve-moi (French Edition) (Musso, Guillaume)"
    assert clipping.author == "Musso, Guillaume"
    assert clipping.location == "emplacement 58-59"


def test_parser_reads_clippings_file():
    """Test that the parser can read and parse a clippings file."""
    parser = ClippingParser()
    clippings = parser.parse_file("tests/unit/My Clippings.txt")

    assert len(clippings) > 0
    assert all(isinstance(clipping, Clipping) for clipping in clippings)


def test_parser_parses_highlight_correctly():
    """Test parsing of a highlight clipping."""
    parser = ClippingParser()
    clippings = parser.parse_file("tests/unit/My Clippings.txt")

    # Find the first highlight
    highlight = next(c for c in clippings if c.clipping_type == "surlignement")

    assert highlight.book_title == "Sauve-moi (French Edition) (Musso, Guillaume)"
    assert highlight.author == "Musso, Guillaume"
    assert highlight.page == "7"
    assert highlight.location == "emplacement 58-59"
    assert highlight.content == "Juliette frissonna en écoutant ces nouvelles."


def test_parser_parses_note_correctly():
    """Test parsing of a note clipping."""
    parser = ClippingParser()
    clippings = parser.parse_file("tests/unit/My Clippings.txt")

    # Find the note
    note = next(c for c in clippings if c.clipping_type == "note")

    assert note.book_title == "The Hard Thing About Hard Things"
    assert note.page == "12"
    assert note.content == "Very interesting indeed"


def test_parser_parses_bookmark_correctly():
    """Test parsing of a bookmark clipping."""
    parser = ClippingParser()
    clippings = parser.parse_file("tests/unit/My Clippings.txt")

    # Find the bookmark
    bookmark = next(c for c in clippings if c.clipping_type == "signet")

    assert bookmark.book_title == "The Hard Thing About Hard Things"
    assert bookmark.page == "23"
    assert bookmark.content == ""  # Bookmarks have no content
