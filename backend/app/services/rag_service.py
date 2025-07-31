import logging
import os
from typing import List, Dict, Any, Optional

# Update these imports
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.base import Chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.services.langchain_setup import get_embeddings, load_vectorstore

logger = logging.getLogger(__name__)



class RAGService:
    """Service for RAG-based question answering."""

    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.embeddings_dir = os.path.join(storage_dir, "embeddings")
        self.models = {}  # Cache for loaded RAG chains
        self.memories = {}  # Conversation memories

    def get_vectorstore_path(self, website_id: int) -> str:
        """Get the path to the vectorstore for a website."""
        return os.path.join(self.embeddings_dir, f"website_{website_id}")

    def _create_qa_prompt(self) -> PromptTemplate:
        """Create the prompt template for question answering."""
        template = """
        You are a helpful, knowledgeable assistant that provides accurate information based on the context provided. 
        You represent the website you're integrated with, so answer as if you're part of the website's official support.

        Context:
        {context}

        Chat History:
        {chat_history}

        Question: {question}

        Instructions:
        1. Answer the question based ONLY on the provided context.
        2. If the context doesn't contain sufficient information to answer the question fully, say so clearly.
        3. DO NOT make up information or provide answers not supported by the context.
        4. Be concise but thorough in your response.
        5. If appropriate, reference specific parts of the context in your answer.
        6. If the user is asking about a specific page or section, direct them to it if mentioned in the context.
        7. Format your response clearly with proper paragraphs and bullet points when appropriate.
        8. If you're unsure, indicate the level of certainty in your answer.

        Answer:
        """
        return PromptTemplate.from_template(template)

    def _create_condense_question_prompt(self) -> PromptTemplate:
        """Create the prompt template for condensing follow-up questions."""
        template = """
        Given the following conversation and a follow up question, rephrase the follow up question 
        to be a standalone question that captures all relevant context from the conversation.

        Chat History:
        {chat_history}

        Follow Up Question: {question}

        Standalone Question:
        """
        return PromptTemplate.from_template(template)

    def get_rag_chain(self, website_id: int, session_id: str) -> Optional[Chain]:
        """
        Get or create a RAG chain for a website and session.
        """
        # Create a unique key for this website+session
        chain_key = f"{website_id}_{session_id}"

        # Check if we already have a chain for this session
        if chain_key in self.models:
            return self.models[chain_key]

        # Check if vectorstore exists
        vectorstore_path = self.get_vectorstore_path(website_id)
        if not os.path.exists(vectorstore_path):
            logger.warning(f"No vectorstore found for website {website_id}")
            return None

        try:
            # Load vectorstore
            embeddings = get_embeddings()
            vectorstore = load_vectorstore(vectorstore_path, embeddings)

            # Create memory with the output key specified
            if session_id not in self.memories:
                self.memories[session_id] = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True,
                    output_key="answer"
                )

            # Set up the LLM
            llm = ChatOpenAI(
                temperature=0.2,
                model_name="gpt-3.5-turbo",
                openai_api_key=settings.OPENAI_API_KEY
            )

            # Create the chain
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                ),
                memory=self.memories[session_id],
                condense_question_prompt=self._create_condense_question_prompt(),
                combine_docs_chain_kwargs={
                    "prompt": self._create_qa_prompt()
                },
                return_source_documents=True
            )

            # Cache it
            self.models[chain_key] = chain
            return chain

        except Exception as e:
            logger.error(f"Error creating RAG chain: {str(e)}")
            return None

    def answer_query(
            self,
            website_id: int,
            query: str,
            session_id: str = "default",
            use_chat_history: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a query using RAG.
        """
        # Get the RAG chain
        chain = self.get_rag_chain(website_id, session_id)

        if not chain:
            return {
                "answer": "I'm sorry, but I don't have information about this website yet. Please try again later.",
                "sources": [],
                "success": False
            }

        try:
            # If we don't want to use chat history, temporarily clear it
            if not use_chat_history and session_id in self.memories:
                original_memory = self.memories[session_id].chat_memory.messages.copy()
                self.memories[session_id].chat_memory.clear()

            # Use the new invoke method instead of calling directly
            result = chain.invoke({"question": query})
            answer = result["answer"]
            source_documents = result.get("source_documents", [])

            # Restore chat history if we cleared it
            if not use_chat_history and session_id in self.memories:
                self.memories[session_id].chat_memory.messages = original_memory

            # Process sources to remove duplicates and format nicely
            sources = []
            seen_urls = set()

            for doc in source_documents:
                metadata = doc.metadata
                url = metadata.get("url", metadata.get("source", ""))

                if url and url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "url": url,
                        "title": metadata.get("title", ""),
                        "chunk_index": metadata.get("chunk_index", 0)
                    })

            return {
                "answer": answer,
                "sources": sources,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error answering query: {str(e)}")
            return {
                "answer": "I'm sorry, I experienced an error while processing your question. Please try again.",
                "sources": [],
                "success": False,
                "error": str(e)
            }

    def reset_conversation(self, session_id: str) -> bool:
        """
        Reset the conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            if session_id in self.memories:
                self.memories[session_id].clear()
            return True
        except Exception as e:
            logger.error(f"Error resetting conversation: {str(e)}")
            return False

    def evaluate_answer(self, answer: str, sources: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Evaluate the quality of an answer.

        Args:
            answer: Generated answer
            sources: Source documents used
            query: Original query

        Returns:
            Dictionary with evaluation metrics
        """
        # This is a simplified evaluation - in a production system,
        # you would implement more sophisticated metrics

        metrics = {
            "has_answer": len(answer) > 20,  # Simple check for non-empty answer
            "has_sources": len(sources) > 0,  # Check if sources were provided
            "source_count": len(sources),  # Number of sources used
        }

        # Calculate a simple quality score (0-100)
        quality_score = 0

        if metrics["has_answer"]:
            quality_score += 50  # Base score for having an answer

            # Bonus for answer length (up to 20 points)
            answer_length = min(len(answer) / 100, 20)
            quality_score += answer_length

        if metrics["has_sources"]:
            # Up to 30 points for sources
            source_score = min(len(sources) * 10, 30)
            quality_score += source_score

        metrics["quality_score"] = round(quality_score)

        return metrics