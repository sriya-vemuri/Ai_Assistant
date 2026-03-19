# LangChain Private Document QA Assistant

A privacy-compliant AI assistant that enables staff at a school, nonprofit, or community institution to upload internal documents and query them locally—no public GPT calls or external APIs.

---

## Table of Contents
1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running Locally](#running-locally)
6. [Running with Docker](#running-with-docker)
7. [API Endpoints](#api-endpoints)
8. [Agents](#agents)
   - [Document Analyzer Agent](#document-analyzer-agent)
   - [Faculty Onboarding Agent](#faculty-onboarding-agent)
9. [Guardrails](#guardrails)
10. [Project Structure](#project-structure)

---

## Features
- **Private Document QA**: Upload PDF/TXT, embed with sentence-transformers, index in FAISS, and query with Retrieval-Augmented Generation (RAG).
- **Local LLM Support**: Integrate open-source LLM (e.g., LLaMA2, Mistral) or GPT via OpenAI key—but no public internet retrieval.
- **Document Analyzer Agent**:
  - Flags outdated chunks (year < 2022)
  - Flags exact duplicates
  - Generates Excel report with `chunk_id`, issue, snippet, and details
- **Faculty Onboarding Agent**:
  - Generates a Week 1 onboarding checklist from policy excerpts
  - Creates a 5‑question multiple‑choice quiz from safety documents
- **Guardrails**: Enforce response schemas, ban sensitive words, and validate JSON output.
![image](https://github.com/user-attachments/assets/73e5940b-352a-481c-a075-6cc5165c81c2)

Video Recording Link : https://drive.google.com/file/d/1yD8Gf3tCeDO1pK9Z9Pmv85To2koiP91R/view?usp=sharing
## Prerequisites
- Python 3.8+
- pip (or Poetry)
- Docker & Docker Compose (optional)
- [Optional] OpenAI API key for GPT use

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Copy and edit the environment file:
```bash
cp .env.example .env
```
Populate `.env`:
```ini

# Persistence paths
VECTORSTORE_PATH=./faiss.index
CHUNKS_PATH=./chunks.npy
``` 

## Running Locally

1. **Start the FastAPI backend** (with Swagger UI available at `http://127.0.0.1:8000/docs`):

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Verify health check** by visiting:

   ```
   http://127.0.0.1:8000/health  # returns { "status": "ok" }
   ```

3. **Launch the Streamlit frontend** (accessible at `http://localhost:8501/`):

   ```bash
   streamlit run streamlit_app.py
   ```

## Running with Docker

Build and start all services (backend + frontend) via Docker Compose:

```bash
docker-compose up --build
```

By default:
- FastAPI backend → http://127.0.0.1:8000/docs  
- Streamlit frontend → http://localhost:8501/  


Build and start all services:
```bash
docker-compose up --build
```

## API Endpoints

### POST `/upload`
- **Description**: Upload PDF or TXT files
- **Form Data**: `files` (array of file objects)
- **Response**: `200 OK` with `{ "message": "Indexed X documents" }`

### POST `/query`
- **Description**: Ask a question using a specific agent
- **Body**:
  ```json
  {
    "question": "...",
    "agent": "doc_analyzer"  // or "onboarding"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "...",
    "source_docs": [ { "chunk_id": ..., "text": "..." } ]
  }
  ```

### GET `/health`
- **Description**: Health check
- **Response**: `200 OK` with `{ "status": "ok" }`

## Agents

### Document Analyzer Agent
- **File**: `agent.py`
- **Flow**:
  1. Extract and chunk text (`file_utils.py`)
  2. Embed with OpenAI or sentence-transformers (`llm.py`)
  3. Search FAISS index (`retrieval.py`)
  4. Post-process and apply guardrails (`guardrails.py`)
  5. Flag outdated (<2022) and duplicate chunks, output Excel report
![image](https://github.com/user-attachments/assets/7224f783-41ec-4ee1-ba58-868e2abfc8f9)

### Faculty Onboarding Agent
- A compact LangChain agent that turns policy excerpts into:
Week 1 Checklist: Retrieves relevant policies and outputs a concise bulleted onboarding plan.
Safety Quiz: Extracts safety rules and generates a 5-question multiple-choice quiz (options a–d + answer key).

How it works: loads docs → vectorizes → retrieves by prompt → feeds into an LLMChain with a tailored template → parses into clean Markdown.
![image](https://github.com/user-attachments/assets/8bb4e864-47dc-49dc-b803-063660620dab)


## Guardrails
- **File**: `guardrails.py`
- **Rules**: Ban sensitive words.

## Project Structure
```bash
AI ASSISTANT/
├── app/
│   ├── core/
│   │   ├── guardrails.py
│   │   ├── langchain_onboarding_agent.py
│   │   ├── llm.py
│   │   └── retrieval.py
│   ├── reports/
│   ├── routers/
│   │   ├── __pycache__/
│   │   ├── query.py
│   │   └── upload.py
│   ├── utils/
│   ├── chunks.npy
│   ├── faiss.index
│   ├── inspect_index.py
│   ├── main.py
│   └── streamlit_app.py
├── uploaded_docs/
│   ├── 9adb105d542c4851ad1ecf74eb1….pdf
│   ├── 02737c1a57a24cc1b7293180e07….pdf
│   ├── 476755727bb44f4fa99c531453a….pdf
│   ├── c31d0963b9ad40cabf49087ef1d….pdf
│   └── dfab988b4c044fa1ab9f0400bc5….pdf
├── venv/
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

