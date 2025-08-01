"""Command-line interface for Scribe to Notion import."""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List

from ..adapters.file_clipping_adapter import FileClippingAdapter
from ..adapters.notion_page_adapter import NotionPageAdapter
from ..services.import_service import ImportService


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Import Amazon Scribe clippings to Notion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
  # Import clippings to Notion
  scribe-to-notion /path/to/My\ Clippings.txt --parent-page-id YOUR_PAGE_ID

  # Import with custom API token
  NOTION_API_TOKEN=your_token scribe-to-notion clippings.txt --parent-page-id YOUR_PAGE_ID
        """,
    )

    parser.add_argument(
        "clippings_file", type=str, help="Path to the My Clippings.txt file"
    )
    parser.add_argument(
        "--parent-page-id",
        required=True,
        help="Notion parent page ID where book pages will be created",
    )
    parser.add_argument(
        "--api-token",
        help="Notion API token (or set NOTION_API_TOKEN environment variable)",
    )

    return parser


def run_import(
    clippings_file: str, parent_page_id: str, api_token: Optional[str] = None
):
    """Run the import process with the given parameters."""
    # Validate clippings file
    clippings_path = Path(clippings_file)
    if not clippings_path.exists():
        print(f"❌ Error: Clippings file not found: {clippings_file}")
        sys.exit(1)

    # Set up API token
    api_token = api_token or os.getenv("NOTION_API_TOKEN")
    if not api_token:
        print("❌ Error: Notion API token is required.")
        print("   Set NOTION_API_TOKEN environment variable or use --api-token")
        sys.exit(1)

    try:
        # Create adapters
        clipping_adapter = FileClippingAdapter()
        page_publisher = NotionPageAdapter(api_token=api_token)

        # Create service
        service = ImportService(page_publisher, clipping_adapter)

        print(f"📖 Parsing clippings from: {clippings_file}")

        # Parse clippings first
        clippings = clipping_adapter.get_clippings(clippings_file)
        highlights = [c for c in clippings if c.clipping_type == "surlignement"]

        print(f"✅ Found {len(clippings)} total clippings")
        print(f"✅ Found {len(highlights)} highlights")

        # Group by book
        books: Dict[str, List] = {}
        for highlight in highlights:
            if highlight.book_title not in books:
                books[highlight.book_title] = []
            books[highlight.book_title].append(highlight)

        print(f"📚 Found {len(books)} books with highlights:")
        for book_title, book_highlights in books.items():
            print(f"   • {book_title}: {len(book_highlights)} highlights")

        print(f"\n🚀 Importing to Notion parent page: {parent_page_id}")

        # Import to Notion
        result = service.import_clippings(clippings_file, parent_page_id)

        print("\n✅ Import completed successfully!")
        print(f"📄 Created {len(result)} book pages:")

        for book_title, page_ids in result.items():
            page_id = page_ids[0]  # We only create one page per book
            notion_url = f"https://notion.so/{page_id.replace('-', '')}"
            print(f"   • {book_title}")
            print(f"     📄 Page ID: {page_id}")
            print(f"     🔗 URL: {notion_url}")

        print(f"\n🎉 All done! Your highlights are now in Notion.")

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    run_import(args.clippings_file, args.parent_page_id, args.api_token)


if __name__ == "__main__":
    main()
