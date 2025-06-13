import os
import sys
import streamlit as st
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Verify environment variables are loaded
if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ OpenAI API key not found in environment variables")
    st.info("Please check your .env file configuration")
    st.stop()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from retriever import search_index
    from retriever.ask_rag import ask_rag
    from sleeper.league_manager import SleeperLeagueManager
except Exception as e:
    logger.error(f"Import error: {str(e)}")
    st.error("❌ Failed to load required modules")
    st.info("Please ensure all dependencies are installed")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Fantasy Football RAG Advisor",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# App title and description
st.title("🏈 Fantasy Football RAG Advisor")
st.markdown("""
    <div class='info-box'>
    Get AI-powered fantasy football insights and analysis using the latest player data.
    Ask questions about players, matchups, draft strategy, and more!
    </div>
""", unsafe_allow_html=True)

# Create main tabs
tab1, tab2 = st.tabs(["General Questions", "Personal League"])

with tab1:
    st.header("Ask Your Fantasy Football Questions")
    
    # Quick questions section
    st.subheader("Quick Questions")
    example_questions = {
        "Top Players": "Who are the top 5 QBs this week?",
        "Start/Sit": "Should I start Josh Allen or Patrick Mahomes?",
        "Rookies": "What rookie WRs should I target in the draft?",
        "Waiver Wire": "Who are the best waiver wire pickups this week?"
    }
    
    col1, col2 = st.columns(2)
    with col1:
        for label, question in list(example_questions.items())[:2]:
            if st.button(f"📋 {label}", key=f"btn_{label}"):
                with st.spinner('Analyzing...'):
                    try:
                        context_chunks = search_index(question)
                        if context_chunks:
                            response = ask_rag(question, context_chunks)
                            st.success("Analysis Complete")
                            st.write(response)
                            
                            # Show source data in expander
                            with st.expander("View Source Data"):
                                st.json(context_chunks)
                        else:
                            st.warning("No relevant information found.")
                    except Exception as e:
                        logger.error(f"Error processing question: {str(e)}")
                        st.error(f"❌ Error: {str(e)}")

    with col2:
        for label, question in list(example_questions.items())[2:]:
            if st.button(f"📋 {label}", key=f"btn_{label}"):
                with st.spinner('Analyzing...'):
                    try:
                        context_chunks = search_index(question)
                        if context_chunks:
                            response = ask_rag(question, context_chunks)
                            st.success("Analysis Complete")
                            st.write(response)
                            
                            with st.expander("View Source Data"):
                                st.json(context_chunks)
                        else:
                            st.warning("No relevant information found.")
                    except Exception as e:
                        logger.error(f"Error processing question: {str(e)}")
                        st.error(f"❌ Error: {str(e)}")

    # Custom question section
    st.subheader("Ask Your Own Question")
    with st.form(key='question_form'):
        question = st.text_input("Enter your fantasy football question:")
        submit_button = st.form_submit_button(label='Get Analysis')
        
        if submit_button and question:
            with st.spinner('Analyzing...'):
                try:
                    context_chunks = search_index(question)
                    if context_chunks:
                        response = ask_rag(question, context_chunks)
                        st.success("Analysis Complete")
                        st.write(response)
                        
                        with st.expander("View Source Data"):
                            st.json(context_chunks)
                    else:
                        st.warning("No relevant information found.")
                except Exception as e:
                    logger.error(f"Error processing question: {str(e)}")
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("Personal League Analysis")
    
    with st.form(key='sleeper_form'):
        username = st.text_input("Enter your Sleeper username:")
        submit_button = st.form_submit_button(label='Load Leagues')
        
        if submit_button and username:
            try:
                league_manager = SleeperLeagueManager()
                leagues_info = league_manager.get_user_leagues_info(username)
                
                if leagues_info and leagues_info.get("leagues"):
                    st.success(f"✅ Found {len(leagues_info['leagues'])} leagues")
                    
                    # League selector
                    league_names = [league.get("name", "Unnamed League") 
                                  for league in leagues_info["leagues"]]
                    selected_league = st.selectbox("Select your league:", league_names)
                    
                    if selected_league:
                        st.subheader(f"Analysis for {selected_league}")
                        
                        # League analysis tabs
                        league_tab1, league_tab2 = st.tabs(["Team Analysis", "Trade Analysis"])
                        
                        with league_tab1:
                            st.write("Team analysis coming soon!")
                            
                        with league_tab2:
                            st.write("Trade analysis coming soon!")
                else:
                    st.warning("No leagues found for this username.")
            except Exception as e:
                logger.error(f"Error fetching league data: {str(e)}")
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
    Made with ❤️ by Fantasy Football RAG Advisor
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    logger.info("Starting Fantasy Football RAG Advisor")