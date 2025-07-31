#!/usr/bin/env python
import os
import sys
import argparse
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.document_processor import DocumentProcessor
from app.services.search_service import SearchService


def check_vectorstore(website_id: int) -> None:
    """Check vectorstore statistics for a website."""
    processor = DocumentProcessor()

    # Get statistics
    stats = processor.get_website_stats(website_id)

    print(f"Vectorstore statistics for website {website_id}:")
    print(json.dumps(stats, indent=2))

    if stats.get("status") == "success":
        # Perform a test search
        search_service = SearchService()
        search_query = "What is this website about?"

        print(f"\nPerforming test search: '{search_query}'")
        results = search_service.search(website_id, search_query, 3)

        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results):
                print(f"\nResult {i + 1} (score: {result['score']:.4f}):")
                print(f"Source: {result['metadata'].get('url', 'Unknown')}")
                print(f"Title: {result['metadata'].get('title', 'Unknown')}")
                print(f"Content excerpt: {result['text'][:200]}...")
        else:
            print("No search results found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check vectorstore statistics")
    parser.add_argument("website_id", type=int, help="ID of the website to check")

    args = parser.parse_args()
    check_vectorstore(args.website_id)


if __name__ == "__main__":
    main()