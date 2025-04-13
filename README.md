# Real Estate Analysis Assistant

## Setup Instructions

1. Clone this repository
2. Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
3. Install required dependencies:
   ```bash
   pip install -e .
   ```
4. Install and start Ollama:
   ```bash
   # Install Ollama (Mac/Linux)
   curl https://ollama.ai/install.sh | sh
   
   # Start Ollama server
   ollama serve
   ```
5. Pull required model:
   ```bash
   ollama pull llama2
   ```

<!-- ## Data Collection -->

<!-- 1. Scrape Redfin data:
   ```bash
   python redfin_scrape.py
   ```
2. Scrape news articles:
   ```bash
   python news_scrape.py
   ```
3. Run text analysis:
   ```bash
   python text_analysis.py
   ``` -->

<!-- The scraped data will be automatically saved to the `data/` directory. -->

## Usage

1. Run the application:
   ```bash
   python run.py
   ```
   This will:
   - Start the Ollama server
   - Launch the data service
   - Open the chat interface

2. Wait for all services to initialize (this may take a few seconds)

3. The interface provides:
   - Left sidebar for managing chat sessions
   - Main chat area for interacting with the AI
   - Choice between Gemini and Ollama models
   - Automatic saving of chat history

4. Features:
   - Create new chat sessions
   - Switch between existing sessions
   - Real-time streaming responses
   - Markdown formatting support
   - Excel data context integration
   - SQLite chat history storage

## Data Format

The assistant uses data from:
- Redfin scraping results (data/redfin_*.xlsx)
- News article analysis (data/news_*.xlsx)
- Text analysis results (data/analysis_*.xlsx)

All data files are automatically generated during the data collection process.
