# TailorTalk — Google Drive File Discovery Agent

A conversational AI agent that helps you search, filter, and discover files in a designated Google Drive folder through natural language chat.

## Features

- Natural language file search ("Find the financial report from last week")
- Search by name, file type, content, or date
- Recursive subfolder search
- Clickable file links and download links in chat
- Multi-turn conversation with memory
- Powered by Gemini LLM + LangGraph agent framework

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Agent | LangGraph + LangChain |
| LLM | Google Gemini (via `langchain-google-genai`) |
| Frontend | Streamlit |
| Drive Integration | Google Drive API v3 (Service Account) |

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI app + chat endpoint
│   ├── agent.py         # LangGraph agent + Gemini LLM
│   └── google_drive.py  # Drive API search logic
├── frontend/
│   └── app.py           # Streamlit chat UI
├── shared/
│   └── schemas.py       # Pydantic request/response models
├── Dockerfile           # Backend container
├── Procfile             # Railway/Heroku start command
├── render.yaml          # Render deployment blueprint
└── requirements.txt
```

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/vinayakkoli2005/Google-drive-agent.
cd Google-drive-agent.
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Required variables:
```
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=service_account.json
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Add your service account
Place your `service_account.json` in the project root and share your Google Drive folder with the service account email.

### 6. Run locally
```bash
# Terminal 1 — Backend
uvicorn backend.main:app --reload

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser.

## Example Queries

- "Show me all files"
- "Find all PDFs"
- "Search for invoices"
- "Find files modified this week"
- "Show me images"
- "Find anything with 'report' in the name"

## Deployment

The app is deployable on Render using the included `render.yaml` blueprint, or on any platform supporting Python web services.

Set the following environment variables on your hosting platform:
- `GOOGLE_API_KEY`
- `GOOGLE_DRIVE_FOLDER_ID`
- `GEMINI_MODEL`
- Upload `service_account.json` as a secret file
