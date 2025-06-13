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
    """Search for relevant context using transformers"""
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
        import pickle
        from pathlib import Path
        import numpy as np
        
        # Load pre-trained model and tokenizer
        model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Tokenize and get embeddings for query
        inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            query_embedding = outputs.last_hidden_state.mean(dim=1).numpy()[0]
        
        # Load metadata and embeddings
        data_dir = Path(__file__).parent.parent / "data"
        metadata_path = data_dir / "fantasy_metadata.pkl"
        embeddings_path = data_dir / "fantasy_embeddings.npy"
        
        if not metadata_path.exists() or not embeddings_path.exists():
            logger.error("Fantasy football data not found")
            st.error("Fantasy football data needs to be indexed first")
            return []
            
        # Load data
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        embeddings = np.load(embeddings_path)
        
        # Calculate similarities using dot product
        similarities = np.dot(embeddings, query_embedding)
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Format results
        results = []
        for idx in top_indices:
            result = metadata[idx]
            result['score'] = float(similarities[idx])
            results.append(result)
            
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        st.error(f"⚠️ Error during search: {str(e)}")
        return []