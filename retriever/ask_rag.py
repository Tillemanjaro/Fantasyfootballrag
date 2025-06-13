import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("🔑 Using Key:", os.getenv("OPENAI_API_KEY")[:10])

# Ensure the API key is in the environment
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI()

def format_chunk(chunk):
    """Convert context chunk (dict or str) into a readable string."""
    if isinstance(chunk, dict):
        return "\n".join(f"{k}: {v}" for k, v in chunk.items())
    return str(chunk)

def ask_rag(query, context_chunks):
    # Convert each chunk to string
    context_text = "\n\n".join([format_chunk(chunk) for chunk in context_chunks])

    # Determine query type
    is_rookie_query = any(word in query.lower() for word in ['rookie', 'rookies', '2025 draft', 'first year'])
    is_matchup_question = any(keyword in query.lower() for keyword in [
        "matchup", "schedule", "season", "outlook", "ros", "rest of season",
        "upcoming", "future", "games", "weeks", "look", "looking"
    ])
    is_lineup_question = any(keyword in query.lower() for keyword in [
        "lineup", "draft", "pick", "roster", "team", "start", "bench", "flex"
    ])

    system_message = """You are an expert fantasy football analyst providing advice. 
When analyzing players:
1. Consider their current performance metrics and rankings
2. Evaluate their upcoming matchups and strength of schedule
3. Account for team situation, injuries, and offensive scheme
4. Look at historical performance and trends
5. Consider matchup-specific factors (e.g., home/away, defense vs. position)

For rookie analysis specifically:
1. Consider their draft position and college performance
2. Evaluate their team's offensive scheme and opportunity
3. Look at the depth chart and competition for targets/touches
4. Consider the team's investment in the player
5. Factor in their learning curve and NFL readiness

Provide clear, actionable advice with specific insights about:
- Player's situation and outlook
- Draft position and value
- Opportunity and role
- Relevant comparisons to established players

Be direct and specific in your recommendations. If discussing rookies, acknowledge their rookie status and the uncertainty that comes with first-year players."""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Using this context about fantasy football players:\n\n{context_text}\n\nAnswer this question: {query}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

