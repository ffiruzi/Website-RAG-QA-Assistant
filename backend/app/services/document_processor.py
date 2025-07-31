import logging
import json
import os
import asyncio
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import datetime

from app.services.langchain_setup import process_document_batch, chunk_document, load_vectorstore, get_embeddings
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing documents into embeddings."""

    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.content_dir = os.path.join(storage_dir, "crawler", "content")
        self.embeddings_dir = os.path.join(storage_dir, "embeddings")
        self.processed_file = os.path.join(storage_dir, "processed_urls.json")

        # Create directories if they don't exist
        os.makedirs(self.embeddings_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.processed_file), exist_ok=True)

        # Load processed URLs
        self.processed_urls = self._load_processed_urls()

    def _load_processed_urls(self) -> Dict[str, str]:
        """Load the set of URLs that have already been processed."""
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading processed URLs: {str(e)}")
        return {}

    def _save_processed_urls(self) -> None:
        """Save the set of processed URLs."""
        with open(self.processed_file, 'w') as f:
            json.dump(self.processed_urls, f, indent=2)

    def mark_url_processed(self, url: str) -> None:
        """Mark a URL as processed with timestamp."""
        self.processed_urls[url] = datetime.datetime.now().isoformat()
        self._save_processed_urls()

    def is_url_processed(self, url: str) -> bool:
        """Check if a URL has been processed."""
        return url in self.processed_urls

    def get_vectorstore_path(self, website_id: int) -> str:
        """Get the path to the vectorstore for a website."""
        return os.path.join(self.embeddings_dir, f"website_{website_id}")

    def get_website_documents(self, website_id: int) -> List[Dict[str, Any]]:
        """Load all documents for a website from the crawler data."""
        website_dir = os.path.join(self.content_dir, str(website_id))
        documents = []

        if not os.path.exists(website_dir):
            logger.warning(f"No content directory found for website {website_id}")
            return []

        for filename in os.listdir(website_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(website_dir, filename), 'r') as f:
                        document = json.load(f)
                        if document.get('url') and not self.is_url_processed(document['url']):
                            documents.append(document)
                except Exception as e:
                    logger.error(f"Error loading document {filename}: {str(e)}")

        return documents

    def process_website(self, website_id: int, batch_size: int = 100) -> Dict[str, Any]:
        """
        Process all documents for a website and generate embeddings.

        Args:
            website_id: ID of the website to process
            batch_size: Number of chunks to process in a batch

        Returns:
            Dictionary with processing statistics
        """
        start_time = datetime.datetime.now()

        # Get all unprocessed documents
        documents = self.get_website_documents(website_id)

        if not documents:
            return {
                "website_id": website_id,
                "status": "no_documents",
                "documents_found": 0,
                "documents_processed": 0,
                "chunks_created": 0,
                "duration_seconds": 0
            }

        # Get vectorstore path
        vectorstore_path = self.get_vectorstore_path(website_id)

        # Process documents in batches
        total_chunks = process_document_batch(documents, vectorstore_path, batch_size)

        # Mark documents as processed
        for doc in documents:
            self.mark_url_processed(doc['url'])

            # Update database if possible
            try:
                # Import needed only when called
                from sqlalchemy.orm import Session
                from app.core.database import SessionLocal
                from app.repositories.page import PageRepository

                # Create session
                db = SessionLocal()
                try:
                    page_repo = PageRepository(db)

                    # Get page by URL
                    page = page_repo.get_by_url(doc['url'])

                    if page:
                        # Mark page as indexed
                        page_repo.update(page.id, {
                            "is_indexed": True
                        })
                finally:
                    db.close()
            except Exception as db_error:
                # Log error but continue - this is just an enhancement
                logger.error(f"Error updating page index status in database: {str(db_error)}")

        # Calculate duration
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "website_id": website_id,
            "status": "success",
            "documents_found": len(documents),
            "documents_processed": len(documents),
            "chunks_created": total_chunks,
            "duration_seconds": duration
        }

    def refresh_website(self, website_id: int, force: bool = False) -> Dict[str, Any]:
        """
        Refresh embeddings for a website, optionally forcing reprocessing of all URLs.

        Args:
            website_id: ID of the website to refresh
            force: If True, reprocess all URLs regardless of previous processing

        Returns:
            Dictionary with refresh statistics
        """
        if force:
            # Clear processed URLs for this website
            website_dir = os.path.join(self.content_dir, str(website_id))
            if os.path.exists(website_dir):
                for filename in os.listdir(website_dir):
                    if filename.endswith(".json"):
                        try:
                            with open(os.path.join(website_dir, filename), 'r') as f:
                                document = json.load(f)
                                if document.get('url') and document['url'] in self.processed_urls:
                                    del self.processed_urls[document['url']]
                        except Exception as e:
                            logger.error(f"Error loading document {filename}: {str(e)}")

                self._save_processed_urls()

        # Process the website
        return self.process_website(website_id)

    def get_website_stats(self, website_id: int) -> Dict[str, Any]:
        """
        Get statistics about a website's vectorstore.

        Args:
            website_id: ID of the website

        Returns:
            Dictionary with vectorstore statistics
        """
        vectorstore_path = self.get_vectorstore_path(website_id)

        if not os.path.exists(vectorstore_path):
            return {
                "website_id": website_id,
                "status": "no_vectorstore",
                "document_count": 0,
                "embedding_count": 0
            }

        try:
            # Check if index file exists
            index_file = os.path.join(vectorstore_path, "index.faiss")
            if not os.path.exists(index_file):
                return {
                    "website_id": website_id,
                    "status": "incomplete_vectorstore",
                    "error": "FAISS index file missing",
                    "document_count": 0,
                    "embedding_count": 0
                }

            # Load vectorstore
            embeddings = get_embeddings()
            vectorstore = load_vectorstore(vectorstore_path, embeddings)

            # Get statistics
            # Use a safer approach to count unique sources
            sources = set()
            doc_count = 0

            # Safely handle the docstore contents
            for doc_id, doc in vectorstore.docstore._dict.items():
                doc_count += 1
                # Check if metadata exists and has source or url
                if hasattr(doc, 'metadata'):
                    source = None
                    if isinstance(doc.metadata, dict):
                        source = doc.metadata.get('source') or doc.metadata.get('url')
                    elif hasattr(doc.metadata, 'source'):
                        source = doc.metadata.source
                    elif hasattr(doc.metadata, 'url'):
                        source = doc.metadata.url

                    if source:
                        sources.add(source)

            return {
                "website_id": website_id,
                "status": "success",
                "document_count": len(sources) if sources else doc_count,
                "embedding_count": doc_count,
                "updated_at": datetime.datetime.fromtimestamp(
                    os.path.getmtime(vectorstore_path)
                ).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting website stats: {str(e)}", exc_info=True)
            return {
                "website_id": website_id,
                "status": "error",
                "error": str(e)
            }