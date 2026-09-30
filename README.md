# AI News Research & Content Generator

A professional AI-powered news research and content-generation platform optimized for different content types (Short Form / Long Form), maximizing research quality while minimizing unnecessary API costs.

## Architecture & Principles
- **Backend**: Python (FastAPI). Chosen for excellent AI library support and ease of data processing.
- **Frontend**: Vanilla HTML/JS/CSS, keeping things minimal and highly maintainable without complex JavaScript frameworks.
- **Database**: SQLite (SQLAlchemy) mapped for easy migration to Postgres.
- **Search**: Google Custom Search JSON API for finding news and recent developments.
- **Data Processing**: `trafilatura` and `BeautifulSoup` for cleaning HTML locally before sending anything to the LLM.
- **AI Synthesis**: Google Gemini 2.5 Flash for fact extraction, aggregation, and script generation.

## Features
- **Content-Type Awareness**:
    - **Short Form**: Focuses on maximum speed, newest developments, short timelines, fewer sources, and consumes fewer credits.
    - **Long Form**: Deep dives into background context, historical facts, multiple source comparisons, and a detailed script. Consumes more credits.
- **Credit System**: 
    - Real-time ledger records usage (Short Form = 10, Long Form = 25).
    - Intelligent refunding on failure.
- **Deduplication**: Minimizes AI token usage by avoiding sending identical stories from different sources.

## Setup

1. **Virtual Environment**:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Environment Variables**:
Copy `.env.example` to `.env` and fill in:
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./news_scraper.db
```

3. **Run Server**:
```bash
cd backend
uvicorn app.main:app --reload
```
Navigate to `http://127.0.0.1:8000/`

## Cost Efficiency
This app strongly follows a "Python-first" data processing philosophy. Advertisements, navigation boilerplate, and cookie banners are stripped locally. Only strictly relevant context is sent to the Gemini API, significantly lowering token usage and error rates.
