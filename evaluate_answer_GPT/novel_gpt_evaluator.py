from typing import List, Dict, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class RAGMetrics:
    context_relevance: float
    answer_completeness: float
    hallucination_score: float
    semantic_similarity: float
    counterfactual_robustness: float

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Calculate cosine similarity between vectors.
    Args:
        a: Array of shape (n_samples_a, n_features)
        b: Array of shape (n_samples_b, n_features)
    Returns:
        similarities: Array of shape (n_samples_a, n_samples_b)
    """
    a_norm = np.linalg.norm(a, axis=1)
    b_norm = np.linalg.norm(b, axis=1)
    
    # Reshape norms to allow broadcasting
    a_norm = a_norm.reshape(-1, 1)
    b_norm = b_norm.reshape(-1, 1)
    
    # Calculate similarities
    similarities = np.dot(a, b.T) / (np.dot(a_norm, b_norm.T) + 1e-8)
    return similarities

class NovelRAGEvaluator:
    def __init__(self, llm_evaluator, embedding_model):
        self.llm = llm_evaluator
        self.embedding_model = embedding_model
        
    def generate_counterfactuals(self, context: str, n_variations: int = 3) -> List[str]:
        """Generate semantically similar but factually different contexts"""
        prompt = f"""Generate {n_variations} alternative versions of this context that:
        1. Maintain similar semantic structure
        2. Change key facts or details
        3. Remain plausible within the domain
        
        Context: {context}"""
        
        return self.llm.generate(prompt).split('\n')
    
    def evaluate_semantic_preservation(self, original_response: str, 
                                    counterfactual_responses: List[str]) -> float:
        """Measure how much core meaning is preserved across counterfactual responses"""
        embeddings = self.embedding_model.encode([original_response] + counterfactual_responses)
        similarities = cosine_similarity(embeddings[0:1], embeddings[1:])
        return float(np.mean(similarities))
    
    def detect_hallucinations(self, response: str, context: str) -> Tuple[float, List[str]]:
        """Identify potential hallucinations using contrastive learning"""
        prompt = f"""Analyze this response for statements that cannot be directly supported by the given context.
        For each statement, provide a confidence score (0-1) that it's a hallucination.
        
        Context: {context}
        Response: {response}"""
        
        analysis = self.llm.analyze(prompt)
        # Parse hallucination scores and statements
        # Implementation details omitted for brevity
        return hallucination_score, hallucinated_statements
    
    def evaluate_rag(self, 
                    query: str,
                    retrieved_context: str,
                    response: str,
                    ground_truth: str = None) -> RAGMetrics:
        """Comprehensive RAG evaluation using novel counterfactual approach"""
        
        # 1. Generate counterfactual contexts
        counterfactual_contexts = self.generate_counterfactuals(retrieved_context)
        
        # 2. Get responses for counterfactual contexts
        counterfactual_responses = [
            self.llm.generate(query, context=c) for c in counterfactual_contexts
        ]
        
        # 3. Evaluate semantic preservation
        semantic_similarity = self.evaluate_semantic_preservation(
            response, counterfactual_responses
        )
        
        # 4. Detect hallucinations
        hallucination_score, _ = self.detect_hallucinations(response, retrieved_context)
        
        # 5. Analyze context relevance through contrastive learning
        context_relevance = self._evaluate_context_relevance(
            query, retrieved_context, counterfactual_contexts
        )
        
        # 6. Measure answer completeness
        answer_completeness = self._measure_completeness(
            response, ground_truth if ground_truth else retrieved_context
        )
        
        # 7. Calculate counterfactual robustness
        counterfactual_robustness = self._calculate_robustness(
            response, counterfactual_responses
        )
        
        return RAGMetrics(
            context_relevance=context_relevance,
            answer_completeness=answer_completeness,
            hallucination_score=hallucination_score,
            semantic_similarity=semantic_similarity,
            counterfactual_robustness=counterfactual_robustness
        )
    
    def _evaluate_context_relevance(self, query: str, 
                                  original_context: str,
                                  counterfactual_contexts: List[str]) -> float:
        """Evaluate context relevance through contrastive analysis"""
        query_embedding = self.embedding_model.encode([query])[0]
        original_embedding = self.embedding_model.encode([original_context])[0]
        counterfactual_embeddings = self.embedding_model.encode(counterfactual_contexts)
        
        # Calculate relevance score using contrastive learning principles
        query_embedding = query_embedding.reshape(1, -1)
        original_embedding = original_embedding.reshape(1, -1)
        
        positive_similarity = cosine_similarity(query_embedding, original_embedding)[0][0]
        negative_similarities = cosine_similarity(query_embedding, counterfactual_embeddings)[0]
        
        # Use InfoNCE-like scoring
        relevance_score = positive_similarity / (positive_similarity + np.mean(negative_similarities))
        return float(relevance_score)
    
    def _measure_completeness(self, response: str, reference: str) -> float:
        """Measure answer completeness using semantic coverage"""
        prompt = f"""Evaluate how completely this response covers the key information in the reference.
        Score from 0-1, where 1 means all key information is covered.
        
        Reference: {reference}
        Response: {response}"""
        
        return float(self.llm.score(prompt))
    
    def _calculate_robustness(self, original_response: str, 
                            counterfactual_responses: List[str]) -> float:
        """Calculate how robust the response is to counterfactual changes"""
        embeddings = self.embedding_model.encode([original_response] + counterfactual_responses)
        original_embedding = embeddings[0:1]
        counterfactual_embeddings = embeddings[1:]
        
        similarities = cosine_similarity(original_embedding, counterfactual_embeddings)[0]
        
        # A lower similarity to counterfactuals indicates higher robustness
        return 1.0 - float(np.mean(similarities))