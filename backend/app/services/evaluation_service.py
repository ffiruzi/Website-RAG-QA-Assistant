import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.core.config import settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating RAG system answers."""

    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.0,
            model_name="gpt-3.5-turbo",
            openai_api_key=settings.OPENAI_API_KEY
        )

    def evaluate_answer(
            self,
            question: str,
            answer: str,
            context: str = None,
            reference_answer: str = None
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of an answer.

        Args:
            question: The original question
            answer: The generated answer
            context: Optional context used to generate the answer
            reference_answer: Optional reference answer for comparison

        Returns:
            Dictionary with evaluation metrics
        """
        # Basic metrics
        metrics = {
            "length": len(answer),
            "has_answer": len(answer) > 20,
        }

        # If we have context, evaluate relevance and factuality
        if context:
            relevance_score = self._evaluate_relevance(question, answer, context)
            factuality_score = self._evaluate_factuality(answer, context)

            metrics["relevance_score"] = relevance_score
            metrics["factuality_score"] = factuality_score

        # If we have a reference answer, compare to it
        if reference_answer:
            similarity_score = self._evaluate_similarity(answer, reference_answer)
            metrics["similarity_score"] = similarity_score

        # Calculate overall score (0-100)
        overall_score = 0

        if "relevance_score" in metrics and "factuality_score" in metrics:
            # Weight factuality more heavily
            overall_score = (metrics["relevance_score"] * 0.4) + (metrics["factuality_score"] * 0.6)
        elif "similarity_score" in metrics:
            # If we only have similarity, use that
            overall_score = metrics["similarity_score"]
        else:
            # Basic score based on length and having an answer
            overall_score = 50 if metrics["has_answer"] else 0

            # Adjust based on length (penalize very short or very long answers)
            length_modifier = min(metrics["length"] / 200, 1.0)  # Cap at 1.0
            overall_score *= length_modifier

        metrics["overall_score"] = round(overall_score)

        return metrics

    def _evaluate_relevance(self, question: str, answer: str, context: str) -> float:
        """
        Evaluate how relevant the answer is to the question and context.
        Returns a score from 0-100.
        """
        try:
            prompt_template = """
            You are an evaluation assistant. Your task is to rate the RELEVANCE of an answer to a question, 
            based on the provided context.

            Question: {question}

            Context: {context}

            Answer: {answer}

            Instructions:
            1. Evaluate how well the answer addresses the question.
            2. Consider whether the answer uses information from the context appropriately.
            3. Determine if the answer stays on topic and relevant to what was asked.
            4. Ignore factual correctness for this evaluation, focus only on relevance.

            Rate the relevance on a scale from 0 to 100, where:
            - 0-20: Completely irrelevant, does not address the question at all
            - 21-40: Mostly irrelevant, barely addresses the question
            - 41-60: Somewhat relevant, addresses parts of the question but misses key aspects
            - 61-80: Mostly relevant, addresses the question well with minor omissions
            - 81-100: Highly relevant, directly and comprehensively addresses the question

            Provide your score as a single number between 0 and 100.

            Score:
            """

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["question", "context", "answer"]
            )

            # chain = LLMChain(llm=self.llm, prompt=prompt)
            chain = prompt | self.llm

            result = chain.invoke({
                "question": question,
                "context": context,
                "answer": answer
            })

            # Parse the score
            try:
                score = float(result.strip())
                return max(0, min(100, score))  # Ensure within 0-100 range
            except ValueError:
                # If parsing fails, default to 50
                logger.warning(f"Failed to parse relevance score: {result}")
                return 50.0

        except Exception as e:
            logger.error(f"Error evaluating relevance: {str(e)}")
            return 50.0  # Default score

    def _evaluate_factuality(self, answer: str, context: str) -> float:
        """
        Evaluate the factual accuracy of the answer based on the context.
        Returns a score from 0-100.
        """
        try:
            prompt_template = """
            You are an evaluation assistant. Your task is to rate the FACTUAL ACCURACY of an answer
            based on the provided context.

            Context: {context}

            Answer: {answer}

            Instructions:
            1. Evaluate how factually accurate the answer is compared to the context.
            2. Check if the answer contains any contradictions to the information in the context.
            3. Determine if the answer contains any hallucinations (information not present in the context).
            4. Ignore relevance for this evaluation, focus only on factual accuracy.

            Rate the factual accuracy on a scale from 0 to 100, where:
            - 0-20: Completely inaccurate, contains major contradictions or hallucinations
            - 21-40: Mostly inaccurate, contains several factual errors
            - 41-60: Partially accurate, contains some correct information but also some errors
            - 61-80: Mostly accurate, contains predominantly correct information with minor errors
            - 81-100: Highly accurate, all information is factually correct based on the context

            Provide your score as a single number between 0 and 100.

            Score:
            """

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "answer"]
            )

            chain = LLMChain(llm=self.llm, prompt=prompt)

            result = chain.run({
                "context": context,
                "answer": answer
            })

            # Parse the score
            try:
                score = float(result.strip())
                return max(0, min(100, score))  # Ensure within 0-100 range
            except ValueError:
                # If parsing fails, default to 50
                logger.warning(f"Failed to parse factuality score: {result}")
                return 50.0

        except Exception as e:
            logger.error(f"Error evaluating factuality: {str(e)}")
            return 50.0  # Default score

    def _evaluate_similarity(self, answer: str, reference_answer: str) -> float:
        """
        Evaluate the similarity between the generated answer and a reference answer.
        Returns a score from 0-100.
        """
        try:
            prompt_template = """
            You are an evaluation assistant. Your task is to rate the SIMILARITY between a generated answer
            and a reference answer.

            Generated Answer: {answer}

            Reference Answer: {reference_answer}

            Instructions:
            1. Evaluate how similar the generated answer is to the reference answer in terms of content.
            2. Consider whether the generated answer covers the same key points as the reference answer.
            3. Ignore minor differences in phrasing or style, focus on the information conveyed.

            Rate the similarity on a scale from 0 to 100, where:
            - 0-20: Completely different, shares almost no information with the reference
            - 21-40: Mostly different, shares very little information with the reference
            - 41-60: Somewhat similar, shares some key information with the reference
            - 61-80: Mostly similar, shares most key information with the reference
            - 81-100: Highly similar, covers all the key points in the reference

            Provide your score as a single number between 0 and 100.

            Score:
            """

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["answer", "reference_answer"]
            )

            chain = LLMChain(llm=self.llm, prompt=prompt)

            result = chain.run({
                "answer": answer,
                "reference_answer": reference_answer
            })

            # Parse the score
            try:
                score = float(result.strip())
                return max(0, min(100, score))  # Ensure within 0-100 range
            except ValueError:
                # If parsing fails, default to 50
                logger.warning(f"Failed to parse similarity score: {result}")
                return 50.0

        except Exception as e:
            logger.error(f"Error evaluating similarity: {str(e)}")
            return 50.0  # Default score