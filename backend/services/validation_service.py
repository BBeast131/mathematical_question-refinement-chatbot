"""
Service for validating mathematical questions using LangChain and Groq
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Structured output for validation"""
    is_valid: bool = Field(description="Whether the input is a valid mathematical question")
    reasoning: str = Field(description="Brief explanation of why it is or isn't valid")
    suggestions: str = Field(description="Suggestions for improvement if invalid, or empty if valid")


class ValidationService:
    """Service to validate if user input is a valid mathematical question"""
    
    def __init__(self):
        # Initialize Groq LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.1  # Low temperature for consistent validation
        )
        
        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=ValidationResult)
        
        # Create validation prompt
        self.validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert mathematician and educator. Your task is to determine if a user's input is a valid mathematical question.

A valid mathematical question should:
1. Be clearly stated and grammatically correct
2. Contain mathematical content (concepts, problems, proofs, computations, etc.)
3. Be answerable or discussable in a mathematical context
4. Not be just a casual conversation or non-mathematical query

Examples of VALID mathematical questions:
- "What is the derivative of x^2?"
- "Prove that the square root of 2 is irrational"
- "How do I solve the equation 2x + 3 = 7?"
- "Explain the concept of limits in calculus"

Examples of INVALID inputs:
- "Hello, how are you?"
- "What's the weather today?"
- "Tell me a joke"
- Just numbers or symbols without context: "2+2"

{format_instructions}"""),
            ("human", "User input: {user_input}\n\nAnalyze this input and determine if it is a valid mathematical question.")
        ])
    
    async def validate(self, user_input: str) -> Dict[str, Any]:
        """
        Validate if the user input is a valid mathematical question.
        
        Args:
            user_input: The user's input to validate
            
        Returns:
            Dictionary with 'is_valid', 'message', and 'reasoning' keys
        """
        try:
            # Format the prompt with output parser instructions
            prompt = self.validation_prompt.partial(
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            # Create chain
            chain = prompt | self.llm | self.output_parser
            
            # Run validation
            result = await chain.ainvoke({"user_input": user_input})
            
            # Format response message
            if result.is_valid:
                message = "✓ Your question is valid! Let's proceed to refinement."
            else:
                message = f"✗ Your input doesn't appear to be a valid mathematical question. {result.suggestions}"
            
            return {
                "is_valid": result.is_valid,
                "message": message,
                "reasoning": result.reasoning,
                "suggestions": result.suggestions if not result.is_valid else ""
            }
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            # Fallback validation - basic check
            if len(user_input.strip()) < 10:
                return {
                    "is_valid": False,
                    "message": "Input is too short. Please provide a complete mathematical question.",
                    "reasoning": "Input length check failed"
                }
            # If LLM fails, assume valid but log warning
            logger.warning(f"LLM validation failed, defaulting to valid: {str(e)}")
            return {
                "is_valid": True,
                "message": "Question received (validation check had issues, but proceeding).",
                "reasoning": "Fallback validation"
            }

