"""
Service for refining mathematical questions using LangChain and Groq
"""
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any
import logging

# Try to import OutputFixingParser - it may be in different locations depending on langchain version
try:
    from langchain.output_parsers import OutputFixingParser
except ImportError:
    try:
        from langchain_core.output_parsers import OutputFixingParser
    except ImportError:
        OutputFixingParser = None  # Will handle gracefully if not available

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.3  # Slightly higher for creative refinement
        )
        
        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=RefinementResult)
        
        # Create refinement prompt with explicit JSON format requirements
        self.refinement_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert mathematical editor and educator. Your task is to refine mathematical questions to improve their grammar, clarity, and formatting while preserving their mathematical meaning.

CRITICAL REFINEMENT REQUIREMENTS:
1. Convert Unicode mathematical symbols to LaTeX notation (e.g., → becomes \\to, ∞ becomes \\infty, ∈ becomes \\in)
2. Fix any grammatical errors and improve sentence structure
3. Improve clarity and readability
4. Ensure proper mathematical notation and formatting
5. Make the question more precise and unambiguous
6. Use standard mathematical terminology
7. Ensure the question is well-structured and professional
8. ALWAYS make meaningful improvements - do not return the exact same question

IMPORTANT: You MUST make actual improvements. If the question has Unicode symbols (like →, ∞, ∈, etc.), convert them to LaTeX. If there are formatting issues, fix them. If the grammar can be improved, improve it.

Do NOT:
- Return the question unchanged
- Change the mathematical content or difficulty
- Add information not present in the original
- Remove important details
- Change the type of question (proof, computation, explanation, etc.)
- Alter the mathematical meaning in any way

OUTPUT FORMAT: You must respond ONLY with valid JSON in this exact format (no markdown, no code blocks, no explanatory text):
{format_instructions}"""),
            ("human", "Original question: {original_question}\n\nRefine this mathematical question. Convert Unicode symbols to LaTeX notation, improve grammar and formatting, and make it more professional. Respond with ONLY the JSON object, no other text.")
        ])
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text that may contain markdown code blocks or explanatory text"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Try to find JSON object
        # Look for { ... } pattern
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If no match, try to parse the whole text
        return text.strip()
    
    def _parse_with_fallback(self, raw_output: str) -> RefinementResult:
        """Parse LLM output with multiple fallback strategies"""
        # Strategy 1: Try direct parsing
        try:
            return self.output_parser.parse(raw_output)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.debug(f"Direct parsing failed: {e}")
        
        # Strategy 2: Extract JSON from markdown/text
        try:
            json_text = self._extract_json_from_text(raw_output)
            return self.output_parser.parse(json_text)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.debug(f"Extracted JSON parsing failed: {e}")
        
        # Strategy 3: Try to fix common JSON issues
        try:
            # Remove trailing commas, fix quotes, etc.
            json_text = self._extract_json_from_text(raw_output)
            json_text = re.sub(r',\s*}', '}', json_text)
            json_text = re.sub(r',\s*]', ']', json_text)
            return self.output_parser.parse(json_text)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.debug(f"Fixed JSON parsing failed: {e}")
        
        # Strategy 4: Use OutputFixingParser as last resort (if available)
        if OutputFixingParser is not None:
            try:
                fixing_parser = OutputFixingParser.from_llm(
                    parser=self.output_parser,
                    llm=self.llm
                )
                return fixing_parser.parse(raw_output)
            except Exception as e:
                logger.debug(f"OutputFixingParser failed: {e}")
        
        # If all strategies failed, raise error
        logger.error(f"All parsing strategies failed. Raw output: {raw_output[:200]}...")
        raise ValueError(f"Could not parse LLM output. Please check the format.")
    
    def _normalize_unicode_symbols(self, text: str) -> str:
        """Normalize Unicode mathematical symbols to LaTeX notation"""
        # Common Unicode to LaTeX mappings
        unicode_to_latex = {
            '→': r'\to',
            '←': r'\leftarrow',
            '↔': r'\leftrightarrow',
            '∞': r'\infty',
            '∈': r'\in',
            '∉': r'\notin',
            '∋': r'\ni',
            '⊂': r'\subset',
            '⊃': r'\supset',
            '⊆': r'\subseteq',
            '⊇': r'\supseteq',
            '∪': r'\cup',
            '∩': r'\cap',
            '∅': r'\emptyset',
            '∀': r'\forall',
            '∃': r'\exists',
            '∄': r'\nexists',
            '∧': r'\land',
            '∨': r'\lor',
            '¬': r'\neg',
            '⇒': r'\Rightarrow',
            '⇐': r'\Leftarrow',
            '⇔': r'\Leftrightarrow',
            '≠': r'\neq',
            '≤': r'\leq',
            '≥': r'\geq',
            '±': r'\pm',
            '×': r'\times',
            '÷': r'\div',
            '∑': r'\sum',
            '∏': r'\prod',
            '∫': r'\int',
            '√': r'\sqrt',
            '∂': r'\partial',
            '∇': r'\nabla',
            'α': r'\alpha',
            'β': r'\beta',
            'γ': r'\gamma',
            'δ': r'\delta',
            'ε': r'\epsilon',
            'θ': r'\theta',
            'λ': r'\lambda',
            'μ': r'\mu',
            'π': r'\pi',
            'ρ': r'\rho',
            'σ': r'\sigma',
            'τ': r'\tau',
            'φ': r'\phi',
            'ω': r'\omega',
            'Γ': r'\Gamma',
            'Δ': r'\Delta',
            'Θ': r'\Theta',
            'Λ': r'\Lambda',
            'Π': r'\Pi',
            'Σ': r'\Sigma',
            'Φ': r'\Phi',
            'Ω': r'\Omega',
        }
        
        result = text
        for unicode_char, latex in unicode_to_latex.items():
            result = result.replace(unicode_char, latex)
        
        return result
    
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
            format_instructions = self.output_parser.get_format_instructions()
            # Make format instructions more explicit
            format_instructions += "\n\nIMPORTANT: Respond with ONLY the JSON object. Do not include markdown code blocks, explanatory text, or any other content. Just the raw JSON."
            
            prompt = self.refinement_prompt.partial(
                format_instructions=format_instructions
            )
            
            # Create chain - get raw output first
            chain = prompt | self.llm
            raw_output = await chain.ainvoke({"original_question": original_question})
            
            # Extract text from LLM message
            if hasattr(raw_output, 'content'):
                raw_text = raw_output.content
            else:
                raw_text = str(raw_output)
            
            logger.debug(f"Raw LLM output: {raw_text[:200]}...")
            
            # Parse with fallback strategies
            result = self._parse_with_fallback(raw_text)
            
            # Ensure we actually made improvements
            refined = result.refined_question.strip()
            original = original_question.strip()
            
            # If no changes were made, try to at least normalize Unicode symbols
            if refined == original or refined == self._normalize_unicode_symbols(original):
                logger.warning("LLM returned unchanged question, applying Unicode normalization")
                refined = self._normalize_unicode_symbols(original)
                changes = "Converted Unicode mathematical symbols to LaTeX notation"
                reasoning = "The question was already well-formatted, but Unicode symbols were converted to standard LaTeX notation for better compatibility."
            else:
                changes = result.changes_made
                reasoning = result.reasoning
            
            return {
                "refined_question": refined,
                "changes_made": changes,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Refinement error: {str(e)}", exc_info=True)
            # Fallback: try to at least normalize Unicode symbols
            try:
                normalized = self._normalize_unicode_symbols(original_question)
                if normalized != original_question:
                    return {
                        "refined_question": normalized,
                        "changes_made": "Converted Unicode mathematical symbols to LaTeX notation (automatic fallback due to LLM error)",
                        "reasoning": f"LLM refinement failed ({str(e)}), but Unicode symbols were automatically converted to LaTeX."
                    }
            except:
                pass
            
            # Final fallback: return original with error note
            return {
                "refined_question": original_question,
                "changes_made": "Refinement service encountered an error. Original question returned.",
                "reasoning": f"Error: {str(e)}"
            }

