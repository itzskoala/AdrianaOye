# Adriana — Social Intelligence Agent

Adriana is a conversational AI agent that monitors Reddit, Instagram, Facebook, and the news in real time. Ask her what people are saying about any topic, analyze trends, and send findings by email.

---

## Architecture

```mermaid
flowchart TD
    User(["👤 User"])

    subgraph UI["Gradio UI  •  source/agent/app.py"]
        Gradio["Chat Interface"]
    end

    subgraph Agent["Agent Layer  •  source/agent/"]
        Adriana["Adriana\nadriana.py\nOrchestrates tool calls"]
        Formatter["Formatter\nformatter.py\nCleans & styles output"]
    end

    subgraph LLMs["LLMs"]
        Gemini["☁️ Gemini 2.5 Flash\nReasoning + tool calling"]
        Ollama["🦙 Ollama  qwen2.5:7b\nOutput formatting"]
    end

    subgraph External["External APIs  (direct)"]
        Serper["☁️ Serper\nWeb + News search"]
        SMTP["📧 Gmail SMTP\nEmail reports"]
    end

    subgraph Backend["FastAPI Backend  •  main.py  •  localhost:8000"]
        API["Routers: reddit · instagram · facebook · news · pipeline · chat"]
        DB[("PostgreSQL")]
        Cache[("Redis")]
    end

    subgraph Collectors["Data Sources  •  source/socialCollectors/"]
        Reddit["Reddit API"]
        Insta["Apify Instagram Scraper"]
        FB["Apify Facebook Scraper"]
        News["Serper News API"]
    end

    User -->|message| Gradio
    Gradio -->|chat_sync| Adriana
    Adriana <-->|tool calls + reasoning| Gemini
    Adriana -->|raw response| Formatter
    Formatter <-->|reformat| Ollama
    Formatter -->|styled response| Gradio
    Gradio -->|reply| User

    Adriana -->|search_web| Serper
    Adriana -->|send_email| SMTP
    Adriana -->|social data tools| Backend
    API --> DB
    API --> Cache
    API --> Collectors
    Collectors --> Reddit
    Collectors --> Insta
    Collectors --> FB
    Collectors --> News
```

---

## Prerequisites

| Tool | Purpose | Install |
|---|---|---|
| Python 3.12+ | Runtime | [python.org](https://python.org) |
| Docker Desktop | PostgreSQL + Redis | [docker.com](https://docker.com) |
| Ollama | Formatter LLM | [ollama.com](https://ollama.com) |

---

## Setup

**1. Clone and create a virtual environment**
```bash
git clone <repo-url>
cd AdrianaOye
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment variables**

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://adriana:adriana@localhost:5432/adriana
REDIS_URL=redis://localhost:6379

GOOGLE_API_KEY=        # Google AI Studio — for Adriana (Gemini 2.5 Flash)
SERPER_API_KEY=        # serper.dev — for web + news search
APIFY_TOKEN=           # apify.com — for Instagram + Facebook scraping

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

EMAIL_FROM=            # Gmail address
EMAIL_APP_PASSWORD=    # Gmail App Password (not your login password)
```

---

## Running

You need **four** things running. Open a terminal for each:

**Terminal 1 — Databases**
```bash
docker compose up -d
```

**Terminal 2 — Ollama (formatter)**
```bash
ollama serve
ollama pull qwen2.5:7b   # first time only
```

**Terminal 3 — FastAPI backend**
```bash
source .venv/bin/activate
uvicorn main:app --reload
```

**Terminal 4 — Gradio UI**
```bash
source .venv/bin/activate
python3 -m source.agent.app
```

Then open **http://localhost:7860** in your browser.

> **Minimal mode:** If you skip the backend, only web search and email work. Skip Ollama and responses are still formatted by Gemini.

---

## Example Questions

```
What are people saying about Tesla on Reddit?
What is Nike posting on Instagram?
What are people posting under #worldcup?
What has NASA been posting on Facebook?
What's the latest news on OpenAI?
Predict news trends for this week
Do a deep Reddit analysis on climate change
Search the web for Bitcoin's current price
Send a summary of AI trends to me@email.com
```

---

## Project Structure

```
AdrianaOye/
├── main.py                        # FastAPI app entry point
├── docker-compose.yml             # PostgreSQL + Redis
├── source/
│   ├── agent/
│   │   ├── adriana.py             # Core agent — Gemini + all tools
│   │   ├── formatter.py           # Ollama output formatter
│   │   └── app.py                 # Gradio UI launcher
│   ├── api/                       # FastAPI routers
│   │   ├── reddit.py
│   │   ├── instagram.py
│   │   ├── facebook.py
│   │   ├── newsSearch.py
│   │   ├── pipeline.py
│   │   └── chat.py
│   ├── socialCollectors/          # Data fetching logic
│   │   ├── instagram_collector.py
│   │   ├── news_collector.py
│   │   └── ...
│   ├── pipeline/                  # BERTopic trend analysis
│   └── db/                        # PostgreSQL + Redis clients
└── frontend/                      # Next.js UI (optional)
```
