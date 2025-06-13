# Fantasy Football RAG Advisor

A Retrieval-Augmented Generation (RAG) powered Fantasy Football advisor that provides personalized insights and recommendations using up-to-date player data and Sleeper league integration.

## Features

- **General Fantasy Advice**: Get expert answers about players, draft strategy, and fantasy football in general
- **Personal League Analysis**: Connect your Sleeper league for personalized advice
- **Full Season Analysis**: View complete season matchups and strength of schedule
- **Rookie Analysis**: Get insights on rookie players and their potential impact
- **Draft Helper**: Get draft recommendations based on your league settings
- **Keeper Analysis**: Analyze potential keepers based on draft position and current value

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd ragfant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key
OPENAI_PROJECT_ID=your_project_id
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Access the web interface at `http://localhost:8501`

3. Features:
   - Ask general fantasy football questions
   - Enter your Sleeper username for personalized advice
   - View full season matchup analysis
   - Get rookie player insights
   - Analyze your league's draft and keepers

## Project Structure

```
ragfant/
├── app.py                 # Main Streamlit application
├── ask_rag.py            # RAG query processing
├── retriever/
│   ├── search_index.py   # Vector search implementation
│   └── vector_search.py  # FAISS index operations
├── scrape/
│   ├── fantasypros_scraper.py  # Data scraping
│   ├── matchup_scraper.py      # Matchup data collection
│   └── vectorize_with_gpt4.py  # Data vectorization
├── sleeper/
│   ├── league_manager.py       # Sleeper league operations
│   └── sleeper_api.py         # Sleeper API client
└── data/                 # Data storage (gitignored)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web interface
- [OpenAI](https://openai.com/) for embeddings and completions
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [Sleeper API](https://docs.sleeper.app/) for fantasy league data
