"""
Service for refining mathematical questions using LangChain and Groq
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RefinementResult(BaseModel):
    """Structured output for refinement"""
    refined_question: str = Field(description="The improved version of the mathematical question")
    changes_made: str = Field(description="A clear description of what changes were made (grammar, clarity, formatting)")
    reasoning: str = Field(description="Brief explanation of why these changes improve the question")


class RefinementService:
    """Service to refine mathematical questions for grammar, clarity, and formatting"""
    
    def __init__(self):
        # Initialize Groq LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            groq_api_key=api_key,
            temperature=0.3  # Slightly higher for creative refinement
        )
        
        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=RefinementResult)
        
        # Create refinement prompt
        self.refinement_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert mathematical editor and educator. Your task is to refine mathematical questions to improve their grammar, clarity, and formatting while preserving their mathematical meaning.

Guidelines for refinement:
1. Fix any grammatical errors
2. Improve clarity and readability
3. Ensure proper mathematical notation and formatting
4. Make the question more precise and unambiguous
5. Preserve the original mathematical intent completely
6. Use standard mathematical terminology

Do NOT:
- Change the mathematical content or difficulty
- Add information not present in the original
- Remove important details
- Change the type of question (proof, computation, explanation, etc.)

{format_instructions}"""),
            ("human", "Original question: {original_question}\n\nRefine this mathematical question for grammar, clarity, and formatting.")
        ])
    
    async def refine(self, original_question: str) -> Dict[str, Any]:
        """
        Refine a mathematical question for grammar, clarity, and formatting.
        
        Args:
            original_question: The original question to refine
            
        Returns:
            Dictionary with 'refined_question', 'changes_made', and 'reasoning' keys
        """
        try:
            # Format the prompt with output parser instructions
            prompt = self.refinement_prompt.partial(
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            # Create chain
            chain = prompt | self.llm | self.output_parser
            
            # Run refinement
            result = await chain.ainvoke({"original_question": original_question})
            
            return {
                "refined_question": result.refined_question,
                "changes_made": result.changes_made,
                "reasoning": result.reasoning
            }
            
        except Exception as e:
            logger.error(f"Refinement error: {str(e)}")
            # Fallback: return original question with a note
            return {
                "refined_question": original_question,
                "changes_made": "Refinement service encountered an error. Original question returned.",
                "reasoning": f"Error: {str(e)}"
            }

