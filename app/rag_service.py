from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import logging

logger = logging.getLogger(__name__)

# Connect to the existing offline vector store
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

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