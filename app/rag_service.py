import os
import logging
import torch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Optimize PyTorch CPU threading for low-spec edge devices
torch.set_num_threads(4) 
torch.set_num_interop_threads(1)

logger = logging.getLogger(__name__)

# INSTANT STARTUP: Use Google Gemini embeddings instead of downloading BAAI/bge-m3 locally
# Updated model name for Google Gemini embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
vector_store = Chroma(
    collection_name="swahili_grammar_kb",
    embedding_function=embeddings,
    persist_directory="./chromadb_grammar_kb"
)

# Implement the Guardrail Lookup
def fetch_validated_rule(rule_id: str) -> dict:
    """
    Queries ChromaDB for an exact match on rule_id metadata.
    Returns the metadata dictionary if found, or None if the rule is invalid.
    """
    try:
        # We use a strict metadata filter (where=...) instead of a semantic search
        result = vector_store.get(where={"rule_id": rule_id})
        
        # Check if the database returned any matching metadatas
        if not result or not result.get("metadatas") or len(result["metadatas"]) == 0:
            logger.warning(f"Guardrail Alert: AI Core cited unknown rule_id '{rule_id}'")
            return None
            
        return result["metadatas"][0]
        
    except Exception as e:
        logger.error(f"ChromaDB lookup failed: {str(e)}")
        return None

def query_knowledge_base(student_query: str, k: int = 2) -> list:
    """
    Searches the knowledge base for the most relevant pedagogical rules
    based on the student's free-form question.
    """
    try:
        # Get results AND their distance scores
        results_with_scores = vector_store.similarity_search_with_score(student_query, k=k)
        
        formatted_results = []
        for doc, score in results_with_scores:
            # Distance threshold: Only keep matches with a score less than 1.1
            # (Lower is closer/better in ChromaDB L2 distance)
            if score < 1.1:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "distance_score": round(score, 3) # Useful for debugging
                })
            else:
                logger.info(f"Dropped a result because distance {score} was too high.")
            
        return formatted_results
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        return []