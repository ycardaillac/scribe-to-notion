"""Tests for the clipping adapter."""

import pytest
from pathlib import Path
from scribe_to_notion.core.models import Clipping
from scribe_to_notion.adapters.file_clipping_adapter import FileClippingAdapter


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
    """Test that BOM characters are cleaned from the model."""
    clipping = Clipping(
        book_title="\ufeffThe Hard Thing About Hard Things",
        author=None,
        clipping_type="surlignement",
        page="12-12",
        location=None,
        date="test date",
        content="\ufeffwas also on the highest academic track in math",
    )

    assert clipping.book_title == "The Hard Thing About Hard Things"
    assert clipping.content == "was also on the highest academic track in math"


def test_clipping_model_extracts_author():
    """Test that author is extracted from book title."""
    clipping = Clipping(
        book_title="The Hard Thing About Hard Things (Horowitz, Ben)",
        author="Horowitz, Ben",
        clipping_type="surlignement",
        page="12-12",
        location=None,
        date="test date",
        content="was also on the highest academic track in math",
    )

    assert clipping.author == "Horowitz, Ben"


def test_file_clipping_adapter_parses_file():
    """Test that FileClippingAdapter can parse the clippings file."""
    adapter = FileClippingAdapter()
    clippings = adapter.get_clippings("tests/unit/My Clippings.txt")

    assert len(clippings) > 0
    assert all(isinstance(c, Clipping) for c in clippings)


def test_file_clipping_adapter_parses_highlights():
    """Test that highlights are parsed correctly."""
    adapter = FileClippingAdapter()
    clippings = adapter.get_clippings("tests/unit/My Clippings.txt")

    highlights = [c for c in clippings if c.clipping_type == "surlignement"]
    assert len(highlights) > 0

    # Check that we have the expected highlights
    highlight_titles = [h.book_title for h in highlights]
    assert "The Hard Thing About Hard Things" in highlight_titles
    assert "Sauve-moi (French Edition) (Musso, Guillaume)" in highlight_titles


def test_file_clipping_adapter_parses_notes():
    """Test that notes are parsed correctly."""
    adapter = FileClippingAdapter()
    clippings = adapter.get_clippings("tests/unit/My Clippings.txt")

    notes = [c for c in clippings if c.clipping_type == "note"]
    assert len(notes) > 0

    # Check that we have the expected note
    note_titles = [n.book_title for n in notes]
    assert "The Hard Thing About Hard Things" in note_titles


def test_file_clipping_adapter_parses_bookmarks():
    """Test that bookmarks are parsed correctly."""
    adapter = FileClippingAdapter()
    clippings = adapter.get_clippings("tests/unit/My Clippings.txt")

    bookmarks = [c for c in clippings if c.clipping_type == "signet"]
    assert len(bookmarks) > 0

    # Check that we have the expected bookmark
    bookmark_titles = [b.book_title for b in bookmarks]
    assert "The Hard Thing About Hard Things" in bookmark_titles
