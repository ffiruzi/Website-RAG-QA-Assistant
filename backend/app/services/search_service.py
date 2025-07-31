import logging
from typing import List, Dict, Any, Optional
import os

from app.services.langchain_setup import load_vectorstore, get_embeddings, get_llm
from app.services.document_processor import DocumentProcessor
from app.core.cache import cache_decorator
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching embeddings and generating answers."""

    def __init__(self, storage_dir: str = "data"):
        self.processor = DocumentProcessor(storage_dir)
        self.embeddings = get_embeddings()

    @cache_decorator(ttl=60 * 5, prefix="search", enabled=settings.CACHE_ENABLED)
    def search(
            self,
            website_id: int,
            query: str,
            top_k: int = 5,
            offset: int = 0,
            min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for documents relevant to a query.
        """
        vectorstore_path = self.processor.get_vectorstore_path(website_id)

        if not os.path.exists(vectorstore_path):
            logger.warning(f"No vectorstore found for website {website_id}")
            return []

        try:
            # Load vectorstore with allow_dangerous_deserialization=True
            vectorstore = load_vectorstore(vectorstore_path, self.embeddings)

            # Search for relevant documents
            docs_with_scores = vectorstore.similarity_search_with_score(
                query,
                k=top_k + offset
            )

            # Apply offset
            if offset > 0:
                docs_with_scores = docs_with_scores[offset:]

            # Format results
            results = []
            for doc, score in docs_with_scores:
                # Skip results below min_score
                if score < min_score:
                    continue

                results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })

            return results

        except Exception as e:
            logger.error(f"Error searching vectorstore: {str(e)}")
            return []

    @cache_decorator(ttl=60 * 5, prefix="answer_query", enabled=settings.CACHE_ENABLED)
    def answer_query(
            self,
            website_id: int,
            query: str,
            top_k: int = 8,
            session_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Answer a query using RAG.

        Args:
            website_id: ID of the website to search
            query: User query
            top_k: Number of documents to retrieve (increased from 5 to 8)
            session_id: Session identifier

        Returns:
            Dictionary with answer and sources
        """
        # Search for relevant documents
        search_results = self.search(website_id, query, top_k)

        if not search_results:
            return {
                "answer": "I don't have enough information to answer that question.",
                "sources": []
            }

        # Prepare context from search results
        context = "\n\n".join([result["text"] for result in search_results])

        # Get answer from LLM
        llm = get_llm()
        answer = llm.predict(
            f"""You are a helpful assistant that answers questions based on the provided context.

            Context:
            {context}

            Question: {query}

            Answer the question based on the provided context. Be specific and detailed. If you find information
            in the context that is relevant to the question, provide a clear and concise answer. If the context doesn't 
            contain the necessary information to answer the question fully, use what information is available to provide
            a partial answer, and acknowledge what information is missing.

            Answer:
            """
        )

        # Format sources
        sources = []
        for result in search_results:
            if 'url' in result['metadata'] and 'source' in result['metadata']:
                source_url = result['metadata']['url'] or result['metadata']['source']
                source_title = result['metadata'].get('title', 'Unknown Title')

                # Avoid duplicate sources
                if not any(s['url'] == source_url for s in sources):
                    sources.append({
                        "url": source_url,
                        "title": source_title,
                        "score": result["score"]
                    })

        return {
            "answer": answer,
            "sources": sources
        }