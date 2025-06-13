import os
import streamlit as st
import openai
import logging
from pathlib import Path
from dotenv import load_dotenv
import numpy as np

__all__ = ['search_index', 'get_openai_client']

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_openai_client():
    """Set up OpenAI API key globally using openai module."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and hasattr(st, 'secrets'):
        api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found")
        st.error("OpenAI API key not found. Please check your .env file or Streamlit secrets.")
        st.stop()
    logger.info("Setting OpenAI API key globally")
    openai.api_key = api_key
    return openai

# Initialize the OpenAI client (actually just sets the key)
try:
    get_openai_client()
    logger.info("Successfully set OpenAI API key")
except Exception as e:
    logger.error(f"Failed to set OpenAI API key at module level: {str(e)}")

def search_index(query, top_k=5):
    """Search the vector index for relevant context"""
    try:
        get_openai_client()  # Ensure key is set
        # Create embeddings for the query
        response = openai.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        query_embedding = response.data[0].embedding
        
        # Load FAISS index and metadata
        import faiss
        import pickle
        from pathlib import Path
        
        data_dir = Path(__file__).parent.parent / "data"
        faiss_path = data_dir / "fantasy_index.faiss"
        metadata_path = data_dir / "fantasy_metadata.pkl"
        
        if not faiss_path.exists():
            logger.error(f"FAISS index not found at {faiss_path}")
            st.error("Fantasy football data needs to be indexed first. Please run build_faiss_index.py")
            return []
            
        # Load index and metadata
        index = faiss.read_index(str(faiss_path))
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
            
        # Normalize query vector
        query_vector = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Search
        scores, indices = index.search(query_vector, top_k)
        
        # Get results with metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # Valid index
                result = metadata[idx]
                result['score'] = float(score)
                results.append(result)
                
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        st.error(f"⚠️ Error during search: {str(e)}")
        return []