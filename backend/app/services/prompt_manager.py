import os
import json
import logging
from typing import Dict, Any, Optional, List
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class PromptManager:
    """Service for managing and customizing prompts."""

    def __init__(self, storage_dir: str = "data/prompts"):
        self.storage_dir = storage_dir
        self.prompts = {}

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)

        # Load prompts
        self._load_prompts()

    def _load_prompts(self):
        """Load prompt templates from disk."""
        if not os.path.exists(self.storage_dir):
            self._save_default_prompts()
            return

        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json"):
                    prompt_id = filename.replace(".json", "")
                    filepath = os.path.join(self.storage_dir, filename)

                    with open(filepath, "r") as f:
                        prompt_data = json.load(f)
                        self.prompts[prompt_id] = prompt_data

            if not self.prompts:
                self._save_default_prompts()

        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            self._save_default_prompts()

    def _save_default_prompts(self):
        """Save default prompt templates to disk."""
        default_prompts = {
            "qa": {
                "template": """
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
                """,
                "input_variables": ["context", "question"],
                "description": "Standard Q&A prompt for answering questions based on context"
            },
            "conversational_qa": {
                "template": """
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
                """,
                "input_variables": ["context", "chat_history", "question"],
                "description": "Conversational Q&A prompt that maintains conversation history"
            },
            "condense_question": {
                "template": """
                Given the following conversation and a follow up question, rephrase the follow up question 
                to be a standalone question that captures all relevant context from the conversation.

                Chat History:
                {chat_history}

                Follow Up Question: {question}

                Standalone Question:
                """,
                "input_variables": ["chat_history", "question"],
                "description": "Condenses follow-up questions into standalone questions with context"
            }
        }

        # Save prompts to disk
        for prompt_id, prompt_data in default_prompts.items():
            self.prompts[prompt_id] = prompt_data
            self._save_prompt(prompt_id, prompt_data)

    def _save_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]):
        """Save a prompt template to disk."""
        try:
            filepath = os.path.join(self.storage_dir, f"{prompt_id}.json")
            with open(filepath, "w") as f:
                json.dump(prompt_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving prompt {prompt_id}: {str(e)}")

    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Get a prompt template by ID."""
        prompt_data = self.prompts.get(prompt_id)
        if not prompt_data:
            return None

        try:
            return PromptTemplate(
                template=prompt_data["template"],
                input_variables=prompt_data["input_variables"]
            )
        except Exception as e:
            logger.error(f"Error creating prompt template for {prompt_id}: {str(e)}")
            return None

    def update_prompt(self, prompt_id: str, template: str, input_variables: List[str], description: str = "") -> bool:
        """Update or create a prompt template."""
        try:
            # Validate the template by creating a PromptTemplate
            PromptTemplate(
                template=template,
                input_variables=input_variables
            )

            # Update the prompt
            prompt_data = {
                "template": template,
                "input_variables": input_variables,
                "description": description
            }

            self.prompts[prompt_id] = prompt_data
            self._save_prompt(prompt_id, prompt_data)

            return True
        except Exception as e:
            logger.error(f"Error updating prompt {prompt_id}: {str(e)}")
            return False

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt template."""
        if prompt_id not in self.prompts:
            return False

        try:
            filepath = os.path.join(self.storage_dir, f"{prompt_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)

            del self.prompts[prompt_id]
            return True
        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {str(e)}")
            return False

    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts."""
        return [
            {
                "id": prompt_id,
                "description": prompt_data.get("description", ""),
                "input_variables": prompt_data.get("input_variables", [])
            }
            for prompt_id, prompt_data in self.prompts.items()
        ]