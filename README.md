# AI Meeting Memory & Decision Reconstruction System

An AI-powered organizational memory platform that converts raw meeting recordings and transcripts into **persistent organizational memory** and reconstructs the historical context, reasoning, and evidence behind past decisions.

---

## 🌟 Core Feature Matrix

- 🎙️ **Audio-to-Text & Transcript Parsing**: Powered by Whisper STT & timestamped segment parsing.
- 🧠 **Structured Meeting Understanding**: Summaries, key discussion points, risks, open questions, and participant identification.
- ⚖️ **Decision Extraction**: Extracts explicit & implicit decisions, rationale, alternatives considered, participants, and confidence scores.
- ✅ **Action Item Extraction**: Assignees, deadlines, and task priority tracking.
- 📦 **Persistent Organizational Memory**: SQLite structured database + ChromaDB vector database.
- 🔍 **Hybrid Retrieval RAG**: Vector similarity search + keyword search + metadata filtering.
- 🕵️ **Decision Reconstruction Engine**: Answers historical questions like *"Why did we choose PostgreSQL instead of MongoDB three months ago?"* with complete grounded evidence.
- 📅 **Chronological Decision Timelines**: Visual evolution of decisions and implementation milestones.
- 🌐 **Interactive Streamlit UI & FastAPI Microservice**: Multi-page web dashboard and RESTful APIs.

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Note: If no API key is set, the system seamlessly operates using built-in intelligent fallback/heuristic engines for offline testing!)*

### 3. Run FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI Swagger Docs: `http://127.0.0.1:8000/docs`

### 4. Run Streamlit UI
```bash
streamlit run frontend/streamlit_app.py
```
Streamlit Web UI: `http://localhost:8501`

---

## 🧪 Running Automated Tests

Run the test suite:
```bash
python -m pytest tests/ -v
```

---

## 💡 Core Scenario Demo

Ask the system:
> **"Why did we choose PostgreSQL instead of MongoDB three months ago?"**

### System Reconstructed Response:
- **Decision**: Selected PostgreSQL over MongoDB.
- **Rationale**: 1) Strong transaction consistency, 2) Relational structure & complex joins, 3) Infrastructure compatibility, 4) Team expertise.
- **Alternatives**: MongoDB.
- **Participants**: Tech Lead, Backend Engineer, Product Manager.
- **Actions Followed**: Create initial PostgreSQL schema & configure staging DB.
- **Sources**: Architecture Review (May 20), Backend Evaluation (May 15), Decision Meeting (May 20).
