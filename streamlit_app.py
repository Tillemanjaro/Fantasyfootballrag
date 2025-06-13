import streamlit as st
from retriever.search_index import search_index
from retriever.ask_rag import ask_rag
import os
from sleeper.league_manager import SleeperLeagueManager

# Set page configuration
st.set_page_config(
    page_title="Fantasy Football RAG Advisor",
    page_icon="🏈",
    layout="wide"
)

# Add title and description
st.title("🏈 Fantasy Football RAG Advisor")
st.markdown("""
This app helps you make fantasy football decisions using AI-powered analysis of current player data.
""")

# Create tabs
tab1, tab2 = st.tabs(["General Questions", "Personal League"])

with tab1:
    st.header("Ask Your Fantasy Football Questions")
    
    # Example questions as buttons
    st.subheader("Quick Questions")
    if st.button("Who are the top 5 QBs this week?"):
        question = "Who are the top 5 QBs this week?"
        with st.spinner('Analyzing...'):
            context_chunks = search_index(question)
            if context_chunks:
                response = ask_rag(question, context_chunks)
                st.write(response)
            else:
                st.warning("No relevant information found.")

    # Custom question input
    st.subheader("Ask Your Own Question")
    question = st.text_input("Enter your fantasy football question:")
    if question:
        with st.spinner('Analyzing...'):
            context_chunks = search_index(question)
            if context_chunks:
                response = ask_rag(question, context_chunks)
                st.write(response)
            else:
                st.warning("No relevant information found.")

with tab2:
    st.header("Personal League Analysis")
    username = st.text_input("Enter your Sleeper username:")
    
    if username:
        try:
            league_manager = SleeperLeagueManager()
            leagues_info = league_manager.get_user_leagues_info(username)
            
            if leagues_info and leagues_info.get("leagues"):
                st.success(f"Found {len(leagues_info['leagues'])} leagues")
                
                # League selector
                league_names = [league.get("name", "Unnamed League") for league in leagues_info["leagues"]]
                selected_league = st.selectbox("Select your league:", league_names)
                
                if selected_league:
                    st.subheader(f"Analysis for {selected_league}")
            else:
                st.warning("No leagues found for this username.")
        except Exception as e:
            st.error(f"Error fetching league data: {str(e)}")
