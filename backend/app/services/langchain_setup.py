from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS  # Update this import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, ConversationalRetrievalChain, RetrievalQA
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any, Optional, Union
import os



import json
import pickle
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_embeddings():
    """Get the OpenAI embeddings model."""
    return OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY
    )


def get_text_splitter(chunk_size=1000, chunk_overlap=200):
    """Get a text splitter for chunking documents."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )


def get_vectorstore(texts, metadatas=None, embeddings=None):
    """Create a FAISS vectorstore from texts."""
    if embeddings is None:
        embeddings = get_embeddings()

    return FAISS.from_texts(texts, embeddings, metadatas=metadatas)


def save_vectorstore(vectorstore, path):
    """Save a vectorstore to disk."""
    vectorstore.save_local(path)


def load_vectorstore(path, embeddings=None):
    """Load a vectorstore from disk."""
    if embeddings is None:
        embeddings = get_embeddings()

    if os.path.exists(path):
        return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

    return None


def get_llm(temperature=0.0, model_name="gpt-3.5-turbo"):
    """Get the OpenAI LLM."""
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model_name=model_name,
        temperature=temperature
    )


def get_qa_prompt():
    """Get the prompt template for Q&A."""
    template = """
    You are a helpful assistant that answers questions based on the provided context.
    Your goal is to provide accurate, relevant, and helpful responses.

    Context: {context}

    Question: {question}

    Answer the question based only on the provided context. Be detailed and thorough in your response.
    If the context doesn't contain sufficient information to answer the question fully, acknowledge this
    and provide what information you can based on the context.

    DO NOT make up or infer information that is not present in the context.

    If you need to reference a source, you can mention it naturally in your response.

    Answer:
    """

    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


def get_conversational_qa_prompt():
    """Get the prompt template for conversational Q&A."""
    template = """
    You are a helpful, knowledgeable assistant that provides accurate information based on the provided context. 
    You represent the website you're integrated with, so answer as if you're part of the website's official support.

    Context: {context}

    Chat History: {chat_history}

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

    return PromptTemplate(
        template=template,
        input_variables=["context", "chat_history", "question"]
    )


def get_condense_question_prompt():
    """Get the prompt template for condensing follow-up questions."""
    template = """
    Given the following conversation and a follow up question, rephrase the follow up question 
    to be a standalone question that captures all relevant context from the conversation.

    Chat History:
    {chat_history}

    Follow Up Question: {question}

    Standalone Question:
    """

    return PromptTemplate(
        template=template,
        input_variables=["chat_history", "question"]
    )


def create_qa_chain(vectorstore=None):
    """Create a Q&A chain using LangChain."""
    if vectorstore is None:
        raise ValueError("Vectorstore is required for QA chain")

    llm = get_llm()
    prompt = get_qa_prompt()

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 'stuff' means stuff all documents into the prompt
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )


def create_conversational_qa_chain(vectorstore=None, memory=None):
    """Create a conversational Q&A chain using LangChain."""
    if vectorstore is None:
        raise ValueError("Vectorstore is required for conversational QA chain")

    llm = get_llm(temperature=0.2)

    if memory is None:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        ),
        memory=memory,
        condense_question_prompt=get_condense_question_prompt(),
        combine_docs_chain_kwargs={
            "prompt": get_conversational_qa_prompt()
        },
        return_source_documents=True
    )


def chunk_document(document: Dict[str, Any], text_splitter=None) -> List[Dict[str, Any]]:
    """
    Split a document into chunks suitable for embedding.

    Args:
        document: Document to split with at least 'content' and 'url' keys
        text_splitter: Optional text splitter to use

    Returns:
        List of chunk dictionaries with text and metadata
    """
    if text_splitter is None:
        text_splitter = get_text_splitter()

    # Extract text
    content = document.get('text', document.get('content', ''))
    if not content:
        return []

    # Build metadata
    metadata = {
        'url': document['url'],
        'source': document['url'],
        'title': document.get('title', ''),
    }

    # Add relevant metadata if available
    if 'metadata' in document:
        if document['metadata'].get('published_date'):
            metadata['published_date'] = document['metadata']['published_date']
        if document['metadata'].get('author'):
            metadata['author'] = document['metadata']['author']

    metadata['domain'] = document.get('domain', document['url'].split('/')[2] if '://' in document['url'] else '')
    metadata['content_type'] = document.get('content_type', 'webpage')

    # Split the text
    texts = text_splitter.split_text(content)

    # Create chunks with metadata
    chunks = []
    for i, text in enumerate(texts):
        chunk_metadata = metadata.copy()
        chunk_metadata['chunk_index'] = i
        chunks.append({
            'text': text,
            'metadata': chunk_metadata
        })

    return chunks


def process_document_batch(documents: List[Dict[str, Any]], vectorstore_path: str, batch_size=100) -> int:
    """
    Process a batch of documents and store their embeddings.

    Args:
        documents: List of documents to process
        vectorstore_path: Path to save/update the vectorstore
        batch_size: Number of chunks to embed at once

    Returns:
        Number of chunks processed
    """
    text_splitter = get_text_splitter()
    embeddings = get_embeddings()

    # Load existing vectorstore if it exists
    vectorstore = None
    if os.path.exists(vectorstore_path):
        try:
            vectorstore = load_vectorstore(vectorstore_path, embeddings)
        except Exception as e:
            logger.error(f"Failed to load existing vectorstore: {e}")
            # Create a new one if loading fails
            vectorstore = None

    # Process documents into chunks
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc, text_splitter)
        all_chunks.extend(chunks)

    if not all_chunks:
        logger.warning("No chunks created from documents")
        return 0

    # Split chunks into batches to avoid memory issues
    total_processed = 0
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        texts = [chunk['text'] for chunk in batch]
        metadatas = [chunk['metadata'] for chunk in batch]

        # Create or update vectorstore
        if vectorstore is None:
            vectorstore = get_vectorstore(texts, metadatas, embeddings)
        else:
            vectorstore.add_texts(texts, metadatas)

        total_processed += len(batch)
        logger.info(f"Processed {total_processed}/{len(all_chunks)} chunks")

        # Save after each batch for resilience
        save_vectorstore(vectorstore, vectorstore_path)

    return total_processed