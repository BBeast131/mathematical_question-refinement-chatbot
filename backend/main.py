"""
Main FastAPI application for Mathematical Question Refinement Chatbot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root (parent of backend directory)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from services.validation_service import ValidationService
from services.refinement_service import RefinementService
from services.similarity_service import SimilarityService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mathematical Question Refinement Chatbot")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization on first use)
validation_service = None
refinement_service = None
similarity_service = None


def get_validation_service():
    """Get or initialize validation service"""
    global validation_service
    if validation_service is None:
        validation_service = ValidationService()
    return validation_service


def get_refinement_service():
    """Get or initialize refinement service"""
    global refinement_service
    if refinement_service is None:
        refinement_service = RefinementService()
    return refinement_service


def get_similarity_service():
    """Get or initialize similarity service"""
    global similarity_service
    if similarity_service is None:
        similarity_service = SimilarityService()
    return similarity_service


class UserMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ValidationResponse(BaseModel):
    is_valid: bool
    message: str
    reasoning: Optional[str] = None
    suggestions: Optional[str] = None


class RefinementResponse(BaseModel):
    refined_question: str
    changes_made: str
    reasoning: Optional[str] = None


class SimilarityResult(BaseModel):
    question_id: int
    question: str
    similarity_score: float
    domain: str
    subdomain: str


class SimilarityResponse(BaseModel):
    similar_questions: List[SimilarityResult]
    threshold: float = 0.8
    exact_match_found: bool = False
    exact_match_id: Optional[int] = None


@app.get("/")
async def root():
    return {"message": "Mathematical Question Refinement Chatbot API"}


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_question(user_message: UserMessage):
    """
    Validate if the user input is a valid mathematical question.
    Returns validation result with reasoning.
    """
    try:
        logger.info(f"Validating question: {user_message.message[:100]}...")
        service = get_validation_service()
        result = await service.validate(user_message.message)
        return ValidationResponse(
            is_valid=result["is_valid"],
            message=result["message"],
            reasoning=result.get("reasoning"),
            suggestions=result.get("suggestions", "")
        )
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post("/api/refine", response_model=RefinementResponse)
async def refine_question(user_message: UserMessage):
    """
    Refine the mathematical question for grammar, clarity, and formatting.
    """
    try:
        logger.info(f"Refining question: {user_message.message[:100]}...")
        service = get_refinement_service()
        result = await service.refine(user_message.message)
        return RefinementResponse(
            refined_question=result["refined_question"],
            changes_made=result["changes_made"],
            reasoning=result.get("reasoning")
        )
    except Exception as e:
        logger.error(f"Refinement error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


@app.post("/api/similarity", response_model=SimilarityResponse)
async def check_similarity(user_message: UserMessage):
    """
    Check semantic similarity between the finalized question and existing questions.
    Returns questions with similarity > 80% (0.8).
    """
    try:
        logger.info(f"Checking similarity for: {user_message.message[:100]}...")
        service = get_similarity_service()
        similarity_data = await service.find_similar(user_message.message, threshold=0.8, exclude_exact=True)
        
        results = similarity_data["results"]
        exact_match_found = similarity_data.get("exact_match_found", False)
        exact_match_id = similarity_data.get("exact_match_id")
        
        similar_questions = [
            SimilarityResult(
                question_id=r["id"],
                question=r["question"],
                similarity_score=r["similarity"],
                domain=r.get("domain", "Unknown"),
                subdomain=r.get("subdomain", "Unknown")
            )
            for r in results
        ]
        
        return SimilarityResponse(
            similar_questions=similar_questions,
            threshold=0.8,
            exact_match_found=exact_match_found,
            exact_match_id=exact_match_id
        )
    except Exception as e:
        logger.error(f"Similarity check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Similarity check failed: {str(e)}")


@app.post("/api/chat")
async def chat(user_message: UserMessage):
    """
    Unified chat endpoint that handles the conversation flow.
    This endpoint manages the state machine for validation -> refinement -> similarity.
    """
    try:
        message = user_message.message.strip().lower()
        
        # Check if user is accepting/declining refinement
        if message in ["accept", "yes", "ok", "confirm"]:
            return {
                "type": "acceptance",
                "message": "Question accepted! Checking for similar questions...",
                "next_action": "similarity_check"
            }
        elif message in ["reject", "no", "revise", "change"]:
            return {
                "type": "revision_request",
                "message": "Please provide your revised question or describe what changes you'd like.",
                "next_action": "refinement"
            }
        
        # For now, return a simple response structure
        # The frontend will handle the flow logic
        return {
            "type": "message",
            "message": "Please use /api/validate, /api/refine, or /api/similarity endpoints for specific operations."
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

