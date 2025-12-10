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
            # Try multiple possible paths
            possible_paths = [
                Path(self.questions_file),
                Path("question.json"),
                Path("questions.json"),
                Path("backend") / "question.json",
                Path("backend") / "questions.json",
            ]
            
            for path in possible_paths:
                if path.exists():
                    logger.info(f"Loading questions from {path}")
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
    
    async def find_similar(self, query_question: str, threshold: float = 0.8, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar questions using semantic similarity.
        
        Args:
            query_question: The question to find similarities for
            threshold: Minimum similarity score (0-1)
            top_k: Maximum number of results to return
            
        Returns:
            List of dictionaries with question info and similarity scores
        """
        if not self.index or not self.questions:
            logger.warning("Index not available, returning empty results")
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.model.encode([query_question])
            query_embedding = np.array(query_embedding).astype('float32')
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            k = min(top_k, len(self.questions))
            similarities, indices = self.index.search(query_embedding, k)
            
            # Filter by threshold and format results
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity >= threshold and idx < len(self.questions):
                    question_data = self.questions[idx].copy()
                    question_data["similarity"] = float(similarity)
                    results.append(question_data)
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(f"Found {len(results)} similar questions above threshold {threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search error: {str(e)}")
            return []

