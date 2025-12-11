"""
Service for checking semantic similarity between questions using embeddings
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import logging

logger = logging.getLogger(__name__)


class SimilarityService:
    """Service to find semantically similar questions using embeddings"""
    
    def __init__(self, questions_file: str = "question.json"):
        """
        Initialize the similarity service.
        
        Args:
            questions_file: Path to the JSON file containing existing questions
        """
        # Load questions
        self.questions_file = questions_file
        self.questions = self._load_questions()
        
        # Initialize embedding model
        logger.info("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Build FAISS index
        self.index = None
        self._build_index()
    
    def _load_questions(self) -> List[Dict[str, Any]]:
        """Load questions from JSON file"""
        try:
            # Get the project root (parent of backend directory)
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent  # Go up from services/ to backend/
            project_root = backend_dir.parent  # Go up from backend/ to project root
            
            # Try multiple possible paths
            possible_paths = [
                project_root / self.questions_file,
                project_root / "question.json",
                project_root / "questions.json",
                Path(self.questions_file),  # Absolute path
                Path("question.json"),  # Current directory
                Path("questions.json"),  # Current directory
            ]
            
            for path in possible_paths:
                if path.exists():
                    logger.info(f"Loading questions from {path.absolute()}")
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            logger.warning("Questions file not found, using empty list")
            return []
        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            return []
    
    def _build_index(self):
        """Build FAISS index for fast similarity search"""
        if not self.questions:
            logger.warning("No questions to index")
            self.index = None
            return
        
        try:
            # Extract question texts
            question_texts = [q["question"] for q in self.questions]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(question_texts)} questions...")
            embeddings = self.model.encode(question_texts, show_progress_bar=True)
            embeddings = np.array(embeddings).astype('float32')
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Create FAISS index (cosine similarity)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity on normalized vectors
            self.index.add(embeddings)
            
            logger.info(f"FAISS index built with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            self.index = None
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison by removing extra whitespace and converting to lowercase"""
        import re
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Convert to lowercase for comparison
        return text.lower()
    
    def _are_texts_similar(self, text1: str, text2: str, threshold: float = 0.99) -> bool:
        """
        Check if two texts are nearly identical using both exact and normalized comparison.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            threshold: Similarity threshold (0-1) for considering texts as identical
            
        Returns:
            True if texts are considered identical/nearly identical
        """
        # Exact match (case-insensitive, whitespace normalized)
        normalized1 = self._normalize_text(text1)
        normalized2 = self._normalize_text(text2)
        
        if normalized1 == normalized2:
            return True
        
        # Check semantic similarity for near-matches
        try:
            emb1 = self.model.encode([normalized1])
            emb2 = self.model.encode([normalized2])
            # Calculate cosine similarity
            similarity = np.dot(emb1[0], emb2[0]) / (np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0]))
            return similarity >= threshold
        except:
            # Fallback to normalized text comparison
            return normalized1 == normalized2
    
    async def find_similar(self, query_question: str, threshold: float = 0.8, top_k: int = 10, exclude_exact: bool = True) -> Dict[str, Any]:
        """
        Find similar questions using semantic similarity.
        
        Args:
            query_question: The question to find similarities for
            threshold: Minimum similarity score (0-1)
            top_k: Maximum number of results to return
            exclude_exact: If True, exclude questions that are identical or nearly identical to the query
            
        Returns:
            Dictionary with keys:
            - "results": List of dictionaries with question info and similarity scores
            - "exact_match_found": Boolean indicating if an exact match was found
            - "exact_match_id": ID of the exact match (if found), None otherwise
        """
        if not self.index or not self.questions:
            logger.warning("Index not available, returning empty results")
            return {
                "results": [],
                "exact_match_found": False,
                "exact_match_id": None
            }
        
        try:
            # Generate embedding for query
            query_embedding = self.model.encode([query_question])
            query_embedding = np.array(query_embedding).astype('float32')
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index (get more results to filter out exact matches)
            k = min(top_k * 2, len(self.questions))  # Get more candidates to filter
            similarities, indices = self.index.search(query_embedding, k)
            
            # Check for exact matches first
            exact_match_found = False
            exact_match_id = None
            
            # Filter by threshold and exclude exact matches
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity >= threshold and idx < len(self.questions):
                    question_text = self.questions[idx]["question"]
                    
                    # Check if this is an exact match
                    is_exact_match = self._are_texts_similar(query_question, question_text, threshold=0.99)
                    
                    if is_exact_match:
                        exact_match_found = True
                        exact_match_id = self.questions[idx]["id"]
                        logger.debug(f"Found exact match: question ID {exact_match_id}")
                        
                        # Skip exact match if exclude_exact is True
                        if exclude_exact:
                            continue
                    
                    question_data = self.questions[idx].copy()
                    question_data["similarity"] = float(similarity)
                    question_data["is_exact_match"] = is_exact_match
                    results.append(question_data)
                    
                    # Stop if we have enough results
                    if len(results) >= top_k:
                        break
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(f"Found {len(results)} similar questions above threshold {threshold} (exact match found: {exact_match_found}, excluded: {exclude_exact})")
            
            return {
                "results": results,
                "exact_match_found": exact_match_found,
                "exact_match_id": exact_match_id
            }
            
        except Exception as e:
            logger.error(f"Similarity search error: {str(e)}")
            return {
                "results": [],
                "exact_match_found": False,
                "exact_match_id": None
            }

