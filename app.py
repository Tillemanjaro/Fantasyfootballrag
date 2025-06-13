import streamlit as st
import os
import json
from datetime import datetime
from ask_rag import ask_rag
from retriever.search_index import search_index
from sleeper.league_manager import SleeperLeagueManager

# Page config
st.set_page_config(
    page_title="Fantasy Football Advisor",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Sleeper manager
@st.cache_resource
def get_sleeper_manager():
    return SleeperLeagueManager()

sleeper_manager = get_sleeper_manager()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .suggestion-btn {
        margin: 0.2rem;
    }
    .player-card {
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .keeper-card {
        padding: 1rem;
        border-radius: 5px;
        border: 2px solid #3498db;
        margin-bottom: 1rem;
        background-color: #f1f9ff;
    }
    .draft-info {
        color: #666;
        font-size: 0.9em;
    }
    .value-score {
        font-weight: bold;
        color: #2ecc71;
    }
    .grade-A {color: #2ecc71;}
    .grade-B {color: #3498db;}
    .grade-C {color: #f1c40f;}
    .grade-D {color: #e67e22;}
    .grade-F {color: #e74c3c;}
    .history-card {
        padding: 0.5rem;
        border-left: 3px solid #3498db;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Sleeper Integration
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Sleeper username input
    st.subheader("🛏️ Sleeper Integration")
    sleeper_username = st.text_input("Enter your Sleeper username:")
    
    if sleeper_username:
        leagues_info = sleeper_manager.get_user_leagues_info(sleeper_username)
        
        if "error" in leagues_info:
            st.error(leagues_info["error"])
        else:
            st.success(f"Found {len(leagues_info['leagues'])} leagues")
            
            # Debug league information
            if not leagues_info["leagues"]:
                st.warning("No leagues found for this user")
            else:
                # Ensure each league has a season
                missing_season = False
                for league in leagues_info["leagues"]:
                    if "season" not in league:
                        missing_season = True
                        st.error("League data is missing season information")
                        break
                
                if not missing_season:
                    # Season selector
                    try:
                        seasons = sorted(set(league["season"] for league in leagues_info["leagues"]), reverse=True)
                        if seasons:
                            selected_season = st.selectbox("Select season:", seasons)
                            
                            # Filter leagues by season
                            season_leagues = [l for l in leagues_info["leagues"] if l["season"] == selected_season]
                            
                            # League selector
                            if season_leagues:
                                selected_league = st.selectbox(
                                    "Select a league:",
                                    options=season_leagues,
                                    format_func=lambda x: x["league_name"]
                                )
                                
                                if selected_league:
                                    st.session_state.selected_league = selected_league
                                    st.session_state.user_id = leagues_info["user_id"]
                    except Exception as e:
                        st.error(f"Error processing league seasons: {str(e)}")

# Sidebar for navigation
st.sidebar.title("Fantasy Football Advisor 🏈")

# Add tabs for different sections
tab_general, tab_personal = st.tabs(["General Questions", "Personal League"])

with tab_general:
    st.header("Ask Fantasy Football Questions")
    
    # Example questions
    st.subheader("Quick Questions")
    example_questions = [
        "Who are the top 5 running backs for PPR leagues?",
        "Which rookie wide receivers should I target in the draft?",
        "Who are the best sleeper picks this season?",
        "Compare Justin Jefferson vs Ja'Marr Chase for this season",
        "What's the best draft strategy for the 1st round?",
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        for q in example_questions[:3]:
            if st.button(q, key=f"q_{q}", help="Click to ask this question"):
                st.session_state.question = q
    with col2:
        for q in example_questions[3:]:
            if st.button(q, key=f"q_{q}", help="Click to ask this question"):
                st.session_state.question = q
    
    # Custom question input
    st.subheader("Ask Your Own Question")
    question = st.text_input("Enter your fantasy football question:", 
                           value=st.session_state.get('question', ''),
                           key="custom_question",
                           help="Ask about players, draft strategy, trades, or general fantasy advice")
    
    if question:
        with st.spinner("Searching fantasy football data..."):
            # Get relevant context from vector search
            search_results = search_index(question, top_k=5)
            
            if search_results:
                # Get RAG response using the search results as context
                with st.spinner("Analyzing context and generating answer..."):
                    response = ask_rag(question, search_results)
                    
                    # Display the response in a clean format
                    st.markdown("### Answer")
                    st.write(response)
                    
                    # Optionally show the sources used
                    with st.expander("View Source Data"):
                        for idx, result in enumerate(search_results, 1):
                            st.markdown(f"**Source {idx}:**")
                            st.markdown(result, unsafe_allow_html=True)
                    
                    # Add a divider
                    st.markdown("---")
            else:
                st.error("No relevant information found in our database. Try asking about specific players, teams, or fantasy strategies.")

with tab_personal:
    st.header("Personal League Analysis")
    # Sleeper username input
    sleeper_username = st.text_input(
        "Enter your Sleeper username to get personalized advice:",
        help="This will help us provide advice specific to your league and roster"
    )

# Main content
st.title("🏈 Fantasy Football Advisor")

# League and Keeper Analysis (if connected)
if "selected_league" in st.session_state:
    league = st.session_state.selected_league
    
    # Tabs for different views
    tab_main, tab_keeper, tab_history, tab_trends = st.tabs([
        "📊 League Overview", 
        "👑 Keeper Analysis", 
        "📜 Historical Data",
        "📈 Trends"
    ])
    
    with tab_main:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("League Info")
            st.write(f"**League Name:** {league['league_name']}")
            st.write(f"**Season:** {league['season']}")
            st.write(f"**Total Teams:** {league['total_rosters']}")
            st.write(f"**Roster Positions:** {', '.join(league['roster_positions'])}")
        
        with col2:
            st.subheader("Current Roster")
            roster_players = sleeper_manager.get_roster_players(league["user_roster"])
            for player in roster_players:
                with st.container():
                    st.markdown(
                        f"""<div class="player-card">
                            <strong>{player['full_name']}</strong> ({player['position']} - {player['team']})
                            {f'🤕 {player["injury_status"]}' if player["injury_status"] else ''}
                        </div>""",
                        unsafe_allow_html=True
                    )
    
    with tab_keeper:
        st.subheader("Keeper Analysis")
        
        # Get keeper recommendations
        keeper_options = sleeper_manager.get_keeper_recommendations(
            league["league_id"], 
            st.session_state.user_id
        )
        
        if keeper_options:
            # Display top keepers
            st.write("### 🌟 Top Keeper Options")
            for option in keeper_options:
                player = option["player"]
                with st.container():
                    st.markdown(
                        f"""<div class="keeper-card">
                            <h4>{player['full_name']} ({player['position']} - {player['team']})</h4>
                            <p class="draft-info">
                                Originally Drafted: Round {option['original_round']}<br>
                                Keeper Round: Round {option['keeper_round']}<br>
                                <span class="value-score">Value Score: {option['value_score']:.2f}</span>
                            </p>
                        </div>""",
                        unsafe_allow_html=True
                    )
        else:
            st.info("No keeper data available for this league")
    
    with tab_history:
        st.subheader("Historical Data")
        
        # Show draft history
        if league.get("draft_info"):
            st.write("### 📝 Draft History")
            draft_picks = sleeper_manager.get_roster_players(
                league["user_roster"],
                include_draft_info=True
            )
            
            for player in draft_picks:
                if player.get("draft_info"):
                    with st.container():
                        st.markdown(
                            f"""<div class="history-card">
                                Round {player['draft_info']['round']}, Pick {player['draft_info']['pick']}: 
                                <strong>{player['full_name']}</strong> ({player['position']} - {player['team']})
                            </div>""",
                            unsafe_allow_html=True
                        )
        
        # Show traded picks
        traded_picks = sleeper_manager.get_trade_picks(league["league_id"])
        if traded_picks:
            st.write("### 🔄 Traded Draft Picks")
            for pick in traded_picks:
                st.write(f"Round {pick['round']} pick traded")
    
    with tab_trends:
        st.subheader("Trending Players")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 📈 Trending Adds")
            trending = sleeper_manager.get_trending_players(hours=24, limit=5)
            for player in trending["adds"]:
                st.write(f"- {player.get('full_name', 'Unknown')} (+{player.get('adds', 0)})")
        
        with col2:
            st.write("### 📉 Trending Drops")
            for player in trending["drops"]:
                st.write(f"- {player.get('full_name', 'Unknown')} (-{player.get('drops', 0)})")

# Quick suggestion buttons
st.subheader("Quick Questions")
col1, col2, col3 = st.columns(3)

suggestions = {
    "Analyze Keepers": "Who are my best keeper options based on draft position and current rankings?",
    "Compare Players": "Compare my current roster players for keeper value",
    "Draft Strategy": "What should my draft strategy be based on my keepers?",
}

if "selected_league" in st.session_state:
    roster_players = sleeper_manager.get_roster_players(
        st.session_state.selected_league["user_roster"]
    )
    if roster_players:
        player_names = [p["full_name"] for p in roster_players[:2]]
        suggestions["Compare My Players"] = f"Compare {' and '.join(player_names)} for keeper value"

for col, (label, question) in zip([col1, col2, col3], suggestions.items()):
    with col:
        if st.button(label, key=label):
            st.session_state.query = question

# Main query input
query = st.text_input(
    "Your fantasy football question:",
    value=st.session_state.get("query", ""),
    help="Ask about matchups, rankings, keepers, or draft strategy"
)

if query:
    with st.spinner("🔄 Analyzing..."):
        try:
            # Get context
            context_chunks = search_index(query)
            
            # Add roster and draft context if available
            if "selected_league" in st.session_state:
                league = st.session_state.selected_league
                roster_players = sleeper_manager.get_roster_players(
                    league["user_roster"],
                    include_draft_info=True
                )
                
                roster_context = "\nYour roster and draft positions:\n" + "\n".join(
                    f"- {p['full_name']} ({p['position']} - {p['team']})" +
                    (f" [Drafted: Round {p['draft_info']['round']}, Pick {p['draft_info']['pick']}]"
                     if p.get('draft_info') else "")
                    for p in roster_players
                )
                context_chunks.append(roster_context)
            
            # Get answer
            answer = ask_rag(query, context_chunks)
            
            # Display answer
            st.markdown("### 🤖 Analysis")
            st.markdown(answer)
            
            # Display context if enabled
            with st.expander("📚 Context Used", expanded=False):
                for i, chunk in enumerate(context_chunks, 1):
                    st.markdown(f"**Source {i}:** {chunk}")
            
            # Save to history
            if "history" not in st.session_state:
                st.session_state.history = []
            
            st.session_state.history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": query,
                "answer": answer,
                "context": context_chunks
            })

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            st.markdown("Please try rephrasing your question or check the following:")
            st.markdown("- Ensure your question is about fantasy football")
            st.markdown("- Check if your Sleeper connection is active")
            st.markdown("- Verify that the data source is accessible")

# History section
if st.session_state.get("history"):
    with st.expander("📜 Question History", expanded=False):
        for item in reversed(st.session_state.history):
            st.markdown(f"**Q:** {item['query']}")
            st.markdown(f"**A:** {item['answer']}")
            st.markdown(f"*Asked at: {item['timestamp']}*")
            st.markdown("---")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Fantasy Football Advisor • Connected with Sleeper API for personalized advice</p>
        <p>Use the sidebar to connect your Sleeper account and explore keeper values</p>
    </div>
    """,
    unsafe_allow_html=True
)
