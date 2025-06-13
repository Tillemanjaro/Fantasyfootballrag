from ask_rag import ask_rag

sample_context = [
    {"player_name": "Puka Nacua", "team": "LAR", "rank_ecr": 12, "note": "Explosive WR2 with high target share"},
    {"player_name": "CeeDee Lamb", "team": "DAL", "rank_ecr": 4, "note": "Elite WR1 matchup this week"}
]

question = "Is Puka worth starting over CeeDee?"
print("🤖", ask_rag(question, sample_context))
