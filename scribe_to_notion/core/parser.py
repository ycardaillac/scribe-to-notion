"""Parser for Amazon Scribe/Kindle clippings."""

import re
from pathlib import Path
from typing import List, Optional

from .models import Clipping


class ClippingParser:
    """Parser for Amazon Scribe/Kindle clippings file."""

    def parse_file(self, file_path: str) -> List[Clipping]:
        """Parse a clippings file and return a list of Clipping objects."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> List[Clipping]:
        """Parse clippings from a string content."""
        # Split by the separator
        clipping_blocks = content.split("==========")

        clippings = []
        for block in clipping_blocks:
            block = block.strip()
            if not block:
                continue

            try:
                clipping = self._parse_clipping_block(block)
                if clipping:
                    clippings.append(clipping)
            except Exception as e:
                # Log error but continue parsing other clippings
                print(f"Error parsing clipping block: {e}")
                continue

        return clippings

    def _parse_clipping_block(self, block: str) -> Optional[Clipping]:
        """Parse a single clipping block."""
        lines = block.split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        if len(lines) < 2:
            return None

        # First line is book title
        book_title = lines[0]
        author = self._extract_author(book_title)

        # Second line is metadata
        metadata_line = lines[1]
        metadata = self._parse_metadata(metadata_line)

        # Remaining lines are content
        content = "\n".join(lines[2:]) if len(lines) > 2 else ""

        return Clipping(
            book_title=book_title,
            author=author,
            clipping_type=metadata["type"],
            page=metadata["page"],
            location=metadata["location"],
            date=metadata["date"],
            content=content,
        )

    def _extract_author(self, book_title: str) -> Optional[str]:
        """Extract author from book title if present."""
        # Look for author in parentheses at the end
        match = re.search(r"\(([^)]+)\)\s*$", book_title)
        if match:
            return match.group(1)
        return None

    def _parse_metadata(self, metadata_line: str) -> dict:
        """Parse the metadata line to extract type, page, location, and date."""
        # Remove the leading dash and space
        metadata_line = metadata_line.lstrip("- ").strip()

        # Parse French metadata patterns
        patterns = [
            # "Votre surlignement sur la page 7 | emplacement 58-59 | Ajouté le dimanche 18 mai 2025 12:34:30"
            r"Votre surlignement sur la page (\S+) \| (emplacement [^|]+) \| Ajouté le (.+)",
            # "Votre surlignement sur la page 12-12 | Ajouté le dimanche 18 mai 2025 12:48:14"
            r"Votre surlignement sur la page (\S+) \| Ajouté le (.+)",
            # "Votre note sur la page 12 | Ajouté le dimanche 18 mai 2025 12:48:36"
            r"Votre note sur la page (\S+) \| Ajouté le (.+)",
            # "Votre signet sur la page 23 | Ajouté le mercredi 21 mai 2025 22:14:57"
            r"Votre signet sur la page (\S+) \| Ajouté le (.+)",
        ]

        for pattern in patterns:
            match = re.match(pattern, metadata_line)
            if match:
                groups = match.groups()

                if len(groups) == 3:  # Has location
                    page, location, date_str = groups
                    clipping_type = "surlignement"
                elif len(groups) == 2:  # No location
                    page, date_str = groups
                    location = None
                    # Determine type from the pattern
                    if "surlignement" in metadata_line:
                        clipping_type = "surlignement"
                    elif "note" in metadata_line:
                        clipping_type = "note"
                    elif "signet" in metadata_line:
                        clipping_type = "signet"
                    else:
                        clipping_type = "unknown"

                return {
                    "type": clipping_type,
                    "page": page,
                    "location": location,
                    "date": date_str,
                }

        # If no pattern matches, return default values
        return {
            "type": "unknown",
            "page": None,
            "location": None,
            "date": "Unknown date",
        }
