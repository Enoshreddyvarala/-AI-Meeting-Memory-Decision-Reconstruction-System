# AI Meeting Memory & Decision Reconstruction System — Implementation Plan

## 1. Project Overview

### Problem Statement

Conventional meeting summarizers provide summaries but fail to preserve the reasoning behind important decisions.

Build a GenAI system that converts meetings into **persistent organizational memory** and reconstructs the context behind previous decisions.

The system should answer questions such as:

> "Why did we choose PostgreSQL instead of MongoDB three months ago?"

Instead of returning only the decision, it should reconstruct:

- What was decided
- Why it was decided
- What alternatives were considered
- Who participated
- What constraints influenced the decision
- What actions followed
- Which meetings contain supporting evidence
- Whether the decision changed later

---

# 2. Project Objective

Build an AI-powered organizational memory platform using:

**Meeting Audio → Speech-to-Text → Meeting Understanding → Persistent Memory → Vector Search → RAG → Decision Reconstruction → Source-Based Answer**

The system should support:

1. Audio-to-text conversion
2. Meeting summarization
3. Decision extraction
4. Action-item extraction
5. Participant identification
6. Semantic search
7. Historical context retrieval
8. Decision reconstruction
9. Meeting memory creation
10. Source-based answers

Advanced features:

11. Decision timeline reconstruction
12. Alternative tracking
13. Decision status tracking
14. Cross-meeting linking
15. Confidence scoring
16. Contradiction detection
17. Decision evolution tracking
18. Follow-up meeting discovery
19. Speaker-aware retrieval
20. Source-grounded RAG responses

---

# 3. Core Scenario

A project team asks:

> **"Why did we choose PostgreSQL instead of MongoDB three months ago?"**

The system searches previous meeting transcripts and reconstructs:

```text
Decision:
PostgreSQL was selected.

Reasons:
- Strong transaction support
- Relational data requirements
- Complex joins
- Existing team expertise
- Infrastructure compatibility

Alternative:
MongoDB

Participants:
- Tech Lead
- Backend Engineer
- Product Manager

Actions:
- Create PostgreSQL schema
- Configure staging database
- Migrate prototype data

Sources:
- Architecture Review
- Backend Design Discussion
- Architecture Decision Meeting
```

---

# 4. Technology Stack

| Layer | Technology |
|---|---|
| Programming | Python |
| LLM | Gemini API / OpenAI API |
| Speech-to-Text | Whisper |
| LLM Framework | LangChain |
| Embeddings | OpenAI / Gemini / Sentence Transformers |
| Vector Database | FAISS / ChromaDB |
| Retrieval | RAG |
| Data Processing | Pandas |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite / PostgreSQL |
| Configuration | `.env` |
| Testing | Pytest / Swagger / Postman |
| Deployment | Docker + Cloud |

### Recommended prototype architecture

```text
Streamlit
    ↓
FastAPI
    ↓
Meeting Processing Pipeline
    ↓
Whisper
    ↓
Gemini / OpenAI
    ↓
ChromaDB / FAISS
    ↓
RAG
    ↓
Decision Reconstruction
```

---

# 5. High-Level System Architecture

```text
                         USER
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      Upload Meeting                Ask Question
             │                           │
             ▼                           ▼
       ┌─────────────┐             ┌──────────────┐
       │ Whisper STT │             │ Query Parser │
       └──────┬──────┘             └──────┬───────┘
              │                           │
              ▼                           │
       Meeting Transcript                 │
              │                           │
              ▼                           │
      ┌─────────────────┐                 │
      │ Meeting         │                 │
      │ Understanding   │                 │
      │ LLM             │                 │
      └────────┬────────┘                 │
               │                          │
       ┌───────┼────────┐                 │
       ▼       ▼        ▼                 │
    Summary Decisions Actions             │
       │       │        │                 │
       └───────┼────────┘                 │
               ▼                          │
      ┌──────────────────┐                │
      │ Meeting Memory   │                │
      └────────┬─────────┘                │
               ▼                          │
      ┌──────────────────┐                │
      │ Embeddings       │                │
      └────────┬─────────┘                │
               ▼                          │
      ┌──────────────────┐                │
      │ FAISS / ChromaDB │◄───────────────┘
      └────────┬─────────┘
               ▼
      Historical Retrieval
               ▼
      Decision Reconstruction
               ▼
      Source-Based Answer
```

---

# 6. Module 1 — Audio-to-Text Conversion

Accept meeting recordings such as:

```text
.mp3
.wav
.m4a
.mp4
.webm
```

Use Whisper to generate a timestamped transcript.

Example:

```text
00:02:14 — Speaker 1:
We need to decide which database to use.

00:04:32 — Speaker 2:
MongoDB is easier for flexible schemas.

00:06:10 — Speaker 3:
But our transactions require strong consistency.

00:08:25 — Speaker 1:
I think PostgreSQL is safer for the current architecture.
```

The transcript should preserve:

- Speaker
- Start timestamp
- End timestamp
- Text
- Meeting ID

---

# 7. Module 2 — Participant Identification

Participant identification can use multiple levels.

## Level 1 — Meeting Metadata

If participant names are available:

```text
Speaker 1 → Rahul
Speaker 2 → Priya
Speaker 3 → Arjun
```

## Level 2 — Speaker Diarization

Identify:

```text
Speaker A
Speaker B
Speaker C
```

## Level 3 — Role Identification

The LLM may infer roles from context:

```text
Speaker A → Tech Lead
Speaker B → Backend Engineer
Speaker C → Product Manager
```

The system must distinguish between:

- Known participant
- Detected speaker
- Inferred role

It must not claim an identity without sufficient evidence.

---

# 8. Module 3 — Transcript Processing

Raw transcripts should be cleaned before further processing.

Pipeline:

```text
Raw Transcript
      ↓
Noise Removal
      ↓
Text Normalization
      ↓
Timestamp Preservation
      ↓
Speaker Metadata Preservation
      ↓
Semantic Chunking
      ↓
Embedding
```

Recommended metadata:

```text
meeting_id
meeting_date
speaker
start_time
end_time
text
topic
```

---

# 9. Module 4 — Transcript Chunking

Long meetings should be divided into meaningful chunks.

Example:

```text
Chunk 1:
Project Status

Chunk 2:
Database Architecture

Chunk 3:
PostgreSQL vs MongoDB

Chunk 4:
Authentication Architecture

Chunk 5:
Deployment Strategy
```

Prefer:

- Topic-aware chunking
- Speaker-aware chunking
- Timestamp preservation
- Small overlap between chunks

Example:

```json
{
  "meeting_id": "M001",
  "meeting_date": "2026-05-20",
  "topic": "Database Selection",
  "start_time": "00:18:42",
  "end_time": "00:26:10",
  "speakers": [
    "Tech Lead",
    "Backend Engineer"
  ]
}
```

---

# 10. Module 5 — Meeting Summarization

The LLM generates a structured summary containing:

```text
Meeting Objective
Key Discussion Points
Important Decisions
Action Items
Risks
Open Questions
Participants
Next Steps
```

Example:

```text
Meeting Objective:
Finalize database architecture.

Key Discussion:
The team compared PostgreSQL and MongoDB.

Decision:
PostgreSQL was selected.

Reason:
The project requires transactional consistency,
complex relationships, and strong SQL support.

Next Step:
Backend team will create the initial schema.
```

---

# 11. Module 6 — Decision Extraction

This is the most important extraction module.

Use structured LLM output validated with Pydantic.

```python
class Decision(BaseModel):
    decision_id: str
    title: str
    decision: str
    rationale: list[str]
    alternatives: list[str]
    participants: list[str]
    timestamp: str
    confidence: float
    source_meeting_id: str
```

Example:

```json
{
  "decision_id": "D001",
  "title": "Database Selection",
  "decision": "Use PostgreSQL",
  "rationale": [
    "Strong transaction support",
    "Complex relational queries",
    "Existing team expertise",
    "Infrastructure compatibility"
  ],
  "alternatives": [
    "MongoDB"
  ],
  "participants": [
    "Tech Lead",
    "Backend Engineer",
    "Product Manager"
  ],
  "timestamp": "00:24:10",
  "confidence": 0.94,
  "source_meeting_id": "M001"
}
```

---

# 12. Explicit vs Implicit Decisions

The system should distinguish between explicit and inferred decisions.

### Explicit

```text
"We have decided to use PostgreSQL."
```

### Implicit

```text
"Given the transaction requirements, PostgreSQL
makes more sense."

"Agreed."

"Okay, let's proceed with PostgreSQL."
```

An inferred decision should have a lower confidence score if evidence is weaker.

---

# 13. Module 7 — Action-Item Extraction

Extract tasks created by meeting discussions and decisions.

```python
class ActionItem(BaseModel):
    action_id: str
    description: str
    owner: str | None
    due_date: str | None
    priority: str
    source_meeting_id: str
    timestamp: str
```

Example:

```text
Action:
Create PostgreSQL schema

Owner:
Backend Team

Due:
Friday

Priority:
High

Source:
Architecture Meeting
```

The system should preserve whether the owner and deadline were explicitly stated.

---

# 14. Module 8 — Meeting Memory Creation

Do not store only the summary.

Create a persistent **Meeting Memory**.

```text
Meeting Memory
│
├── Metadata
│   ├── Meeting ID
│   ├── Date
│   ├── Title
│   └── Participants
│
├── Summary
├── Topics
├── Decisions
├── Alternatives
├── Reasons
├── Action Items
├── Risks
├── Open Questions
├── Follow-up Meetings
└── Transcript References
```

This becomes the organization's persistent memory layer.

---

# 15. Meeting Memory JSON

```json
{
  "meeting_id": "M001",
  "title": "Architecture Review",
  "date": "2026-05-20",
  "participants": [
    "Rahul",
    "Priya",
    "Arjun"
  ],
  "summary": "The team finalized the database architecture.",
  "topics": [
    "Database selection",
    "Scalability",
    "Transactions"
  ],
  "decisions": [
    {
      "title": "Database Selection",
      "decision": "Use PostgreSQL",
      "reasons": [
        "Transactional consistency",
        "Relational data model",
        "Team expertise"
      ],
      "alternatives": [
        "MongoDB"
      ]
    }
  ],
  "actions": [
    "Create PostgreSQL schema",
    "Configure staging database"
  ]
}
```

---

# 16. Module 9 — Embedding Generation

Generate embeddings for:

- Transcript chunks
- Meeting summaries
- Decisions
- Action items
- Topics
- Risks
- Meeting memories

Example:

```text
"PostgreSQL was selected because the application
requires strong transaction consistency."
```

↓

```text
Embedding Vector
[0.023, -0.117, 0.884, ...]
```

---

# 17. Module 10 — Vector Database

Use either:

- FAISS
- ChromaDB

### Recommendation

Use **ChromaDB** for the prototype because it simplifies persistent storage and metadata filtering.

Store:

```text
Vector
+
Text
+
Metadata
```

Example:

```json
{
  "meeting_id": "M001",
  "meeting_date": "2026-05-20",
  "document_type": "decision",
  "topic": "database",
  "speaker": "Tech Lead"
}
```

---

# 18. Module 11 — Semantic Search

Users should be able to ask natural-language questions:

```text
Why did we choose PostgreSQL?

Who participated in the database decision?

What alternatives did we consider?

What were the concerns about MongoDB?

When was the database decision made?

What actions followed the decision?
```

The question is embedded and matched against stored meeting memories.

---

# 19. Hybrid Search

Use three retrieval strategies together.

## Semantic Search

Find conceptually related content.

## Keyword Search

Useful for exact technical terms:

```text
PostgreSQL
MongoDB
Kafka
Redis
API Gateway
```

## Metadata Filtering

Filter by:

```text
Date
Meeting
Participant
Topic
Decision
Project
```

Combining these improves retrieval quality.

---

# 20. Module 12 — Historical Context Retrieval

A decision may span several meetings.

Example:

```text
Meeting 1:
Problem introduced

Meeting 2:
PostgreSQL vs MongoDB discussed

Meeting 3:
Decision finalized

Meeting 4:
Implementation issues discussed
```

The system should retrieve all relevant meetings and create a timeline.

```text
Problem Identified
      ↓
Alternatives Discussed
      ↓
Technical Evaluation
      ↓
Decision Made
      ↓
Implementation
      ↓
Follow-up
```

---

# 21. Module 13 — Decision Reconstruction

This is the core GenAI functionality.

Input:

```text
User Question
+
Retrieved Meeting Evidence
+
Decision Records
+
Related Historical Context
```

Output:

```text
Decision
Why it was made
Alternatives considered
Participants
Evidence
Actions
Follow-up context
Confidence
```

---

# 22. Decision Reconstruction Pipeline

```text
User Question
      ↓
Query Understanding
      ↓
Semantic Retrieval
      ↓
Metadata Filtering
      ↓
Retrieve Related Meetings
      ↓
Retrieve Decisions
      ↓
Build Historical Timeline
      ↓
Rerank Evidence
      ↓
LLM Reasoning
      ↓
Source-Based Answer
```

---

# 23. PostgreSQL vs MongoDB Example

### User Query

> Why did we choose PostgreSQL instead of MongoDB three months ago?

### Retrieved Evidence

```text
Meeting M001:
MongoDB was considered because of schema flexibility.

Meeting M002:
Backend team raised concerns about transaction handling.

Meeting M003:
The team preferred PostgreSQL because of relational
data requirements and complex joins.

Meeting M004:
The architecture decision was finalized.
```

### Reconstructed Answer

```text
The team chose PostgreSQL because the project required
strong transactional consistency, relational data modeling,
and complex joins.

MongoDB was considered because of its flexible schema and
document-oriented model, but the team determined that those
advantages were less important for the application's current
requirements.

The decision involved the Tech Lead, Backend Engineer,
and Product Manager.

Following the decision, the backend team was assigned to
create the PostgreSQL schema and staging environment.

Sources:
- Architecture Review — May 20
- Backend Design Discussion — May 22
- Architecture Decision Meeting — May 25
```

---

# 24. Source-Based Answers

The system must not generate unsupported claims.

Every important claim should have a source.

Example:

```text
Reason:
Strong transaction requirements
[Source: Architecture Review, 00:22:14]

Alternative:
MongoDB
[Source: Backend Discussion, 00:18:42]

Decision:
PostgreSQL
[Source: Architecture Decision Meeting, 00:31:20]
```

Every transcript chunk should preserve:

```text
meeting_id
meeting_title
meeting_date
speaker
timestamp
chunk_id
```

This enables traceability back to the original recording.

---

# 25. RAG Architecture

```text
                    USER QUERY
                        │
                        ▼
                Query Embedding
                        │
                        ▼
              ┌─────────────────┐
              │ Vector Database │
              └────────┬────────┘
                       │
                       ▼
               Relevant Chunks
                       │
                       ▼
               Metadata Filtering
                       │
                       ▼
                    Reranker
                       │
                       ▼
              Historical Context
                       │
                       ▼
                    LLM
                       │
                       ▼
             Source-Based Answer
```

---

# 26. RAG Prompt Design

Use a grounding-focused prompt.

```text
You are an organizational memory assistant.

Answer the user's question using only the supplied
meeting evidence.

For each important claim:
- identify the supporting meeting
- preserve the decision timeline
- distinguish explicit facts from inference
- do not invent participants, dates, reasons, or actions

If the evidence is insufficient, say that the available
meeting records do not provide enough information.

User Question:
{question}

Retrieved Evidence:
{context}
```

---

# 27. Module 14 — Decision Timeline

Create a chronological view.

```text
May 10
Problem identified
       │
       ▼
May 15
MongoDB proposed
       │
       ▼
May 20
PostgreSQL evaluated
       │
       ▼
May 25
PostgreSQL selected
       │
       ▼
May 30
Implementation started
       │
       ▼
June 15
Schema review completed
```

---

# 28. Module 15 — Alternative Tracking

Maintain alternatives for every decision.

```text
Decision:
Database Selection

Chosen:
PostgreSQL

Alternatives:
MongoDB
MySQL

Reasons for PostgreSQL:
- Transactions
- SQL support
- Existing expertise

Reasons against MongoDB:
- Less suitable for relational workload
- Additional consistency considerations
```

---

# 29. Module 16 — Decision Evolution Tracking

Decisions can change over time.

Example:

```text
Decision V1:
Use PostgreSQL

Later:
PostgreSQL + Redis

Later:
PostgreSQL → Managed PostgreSQL

Current:
AWS RDS PostgreSQL
```

The system should distinguish:

```text
Original Decision
Modified Decision
Current Decision
```

This prevents outdated decisions from being returned as current truth.

---

# 30. Module 17 — Contradiction Detection

Example:

### Meeting A

```text
Use PostgreSQL.
```

### Meeting B

```text
Let's move to MongoDB.
```

The system should detect this as a potential decision change.

```text
Potential Decision Change Detected

Original:
PostgreSQL

Later Discussion:
MongoDB

Status:
Requires confirmation
```

---

# 31. Module 18 — Confidence Scoring

Each extracted decision should have a confidence score.

Example:

```text
Decision Confidence: 94%
```

Possible evidence factors:

```text
Explicit decision statement
+ Participant agreement
+ Follow-up action
+ Multiple supporting meetings
+ Consistent later references
```

Lower confidence when:

```text
Only one ambiguous statement
No explicit agreement
Conflicting later evidence
Missing participants
```

---

# 32. Data Models

Recommended Pydantic models:

```python
class Meeting(BaseModel):
    meeting_id: str
    title: str
    date: str
    participants: list[str]
    transcript: str


class Decision(BaseModel):
    decision_id: str
    title: str
    decision: str
    rationale: list[str]
    alternatives: list[str]
    participants: list[str]
    timestamp: str
    confidence: float
    source_meeting_id: str


class ActionItem(BaseModel):
    action_id: str
    description: str
    owner: str | None
    due_date: str | None
    priority: str
    source_meeting_id: str


class MeetingMemory(BaseModel):
    meeting_id: str
    summary: str
    topics: list[str]
    decisions: list[Decision]
    actions: list[ActionItem]
    participants: list[str]
```

---

# 33. Recommended Project Structure

```text
ai-meeting-memory/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── meeting_routes.py
│   │   ├── search_routes.py
│   │   ├── decision_routes.py
│   │   └── memory_routes.py
│   │
│   ├── models/
│   │   ├── meeting.py
│   │   ├── transcript.py
│   │   ├── decision.py
│   │   ├── action.py
│   │   └── memory.py
│   │
│   ├── services/
│   │   ├── speech_to_text.py
│   │   ├── llm_service.py
│   │   ├── summarizer.py
│   │   ├── decision_extractor.py
│   │   ├── action_extractor.py
│   │   ├── participant_identifier.py
│   │   └── memory_builder.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   └── answer_generator.py
│   │
│   ├── analysis/
│   │   ├── decision_reconstruction.py
│   │   ├── decision_timeline.py
│   │   ├── contradiction_detector.py
│   │   └── confidence.py
│   │
│   └── database/
│       ├── sqlite_db.py
│       └── repositories.py
│
├── frontend/
│   └── streamlit_app.py
│
├── prompts/
│   ├── summary_prompt.txt
│   ├── decision_prompt.txt
│   ├── action_prompt.txt
│   ├── reconstruction_prompt.txt
│   └── rag_prompt.txt
│
├── data/
│   ├── audio/
│   ├── transcripts/
│   ├── memories/
│   └── vector_store/
│
├── tests/
│   ├── test_transcription.py
│   ├── test_extraction.py
│   ├── test_retrieval.py
│   ├── test_reconstruction.py
│   └── test_api.py
│
├── .env
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# 34. API Design

## Upload Meeting

```text
POST /meetings/upload
```

Uploads meeting audio.

## Transcribe Meeting

```text
POST /meetings/{meeting_id}/transcribe
```

Converts audio into text.

## Process Meeting

```text
POST /meetings/{meeting_id}/process
```

Generates summary, decisions, actions, participants, and memory.

## Search Meetings

```text
POST /search
```

Performs semantic/hybrid search.

## Ask Historical Question

```text
POST /ask
```

Performs RAG and returns a source-based answer.

## Retrieve Decision

```text
GET /decisions/{decision_id}
```

Returns decision details.

## Decision Timeline

```text
GET /decisions/{decision_id}/timeline
```

Returns chronological decision evolution.

## Meeting Memory

```text
GET /meetings/{meeting_id}/memory
```

Returns persistent meeting memory.

---

# 35. Example `/ask` Request

```json
{
  "question": "Why did we choose PostgreSQL instead of MongoDB three months ago?",
  "project": "AI Platform"
}
```

## Response

```json
{
  "answer": "PostgreSQL was selected because...",
  "decision": "Use PostgreSQL",
  "reasons": [
    "Strong transaction support",
    "Relational data requirements",
    "Existing team expertise"
  ],
  "alternatives": [
    "MongoDB"
  ],
  "participants": [
    "Tech Lead",
    "Backend Engineer"
  ],
  "confidence": 0.94,
  "sources": [
    {
      "meeting_id": "M001",
      "title": "Architecture Review",
      "date": "2026-05-20",
      "timestamp": "00:24:10"
    }
  ]
}
```

---

# 36. Frontend Design

## Page 1 — Upload Meeting

```text
AI MEETING MEMORY

Upload Meeting Recording

[ Choose File ]

Meeting Title
Meeting Date
Project
Participants

[Process Meeting]
```

## Page 2 — Meeting Memory

```text
Meeting: Architecture Review

Date:
20-May-2026

Participants:
Rahul
Priya
Arjun

Summary:
The team finalized the database architecture.

Key Decisions:
✓ PostgreSQL selected

Action Items:
✓ Create database schema
✓ Configure staging environment

Topics:
Database
Transactions
Scalability
```

## Page 3 — Decision Explorer

```text
DECISION EXPLORER

Decision:
Database Selection

Chosen:
PostgreSQL

Alternatives:
MongoDB
MySQL

Confidence:
94%

Why?
────────────────────────
Strong transaction support
Relational data requirements
Existing team expertise

[View Timeline]
[View Source Meetings]
```

## Page 4 — Ask Organizational Memory

```text
ASK ORGANIZATIONAL MEMORY

Why did we choose PostgreSQL instead of MongoDB
three months ago?

[Ask]

ANSWER

PostgreSQL was selected because...

Reasons:
1. Strong transaction consistency
2. Relational data requirements
3. Complex joins
4. Existing team expertise

Alternatives:
MongoDB

Participants:
Tech Lead
Backend Engineer
Product Manager

SOURCES
────────────────────────────────────────────
Architecture Review — May 20
Backend Discussion — May 22
Decision Meeting — May 25
```

## Page 5 — Historical Timeline

```text
Decision Timeline

May 10
Problem identified
     │
     ▼
May 15
MongoDB proposed
     │
     ▼
May 20
Technical comparison
     │
     ▼
May 25
PostgreSQL selected
     │
     ▼
May 30
Implementation started
```

---

# 37. Meeting Processing Pipeline

When a meeting is uploaded:

```text
1. Upload Audio
       ↓
2. Store File
       ↓
3. Whisper Transcription
       ↓
4. Clean Transcript
       ↓
5. Identify Speakers
       ↓
6. Chunk Transcript
       ↓
7. Generate Embeddings
       ↓
8. Store in Vector DB
       ↓
9. Generate Summary
       ↓
10. Extract Decisions
       ↓
11. Extract Action Items
       ↓
12. Identify Participants
       ↓
13. Create Meeting Memory
       ↓
14. Store Structured Metadata
```

---

# 38. Query Processing Pipeline

```text
User Question
      ↓
Query Understanding
      ↓
Extract Entities
      ↓
Generate Query Embedding
      ↓
Semantic Search
      ↓
Keyword Search
      ↓
Metadata Filtering
      ↓
Retrieve Top-K Results
      ↓
Rerank Results
      ↓
Find Related Meetings
      ↓
Build Historical Timeline
      ↓
Decision Reconstruction
      ↓
Source Validation
      ↓
Final Answer
```

---

# 39. Query Understanding

For:

> Why did we choose PostgreSQL instead of MongoDB three months ago?

Extract:

```json
{
  "intent": "decision_reconstruction",
  "entities": [
    "PostgreSQL",
    "MongoDB"
  ],
  "time_range": "three months ago",
  "topic": "database selection",
  "requested_information": [
    "decision",
    "reasons",
    "alternatives",
    "participants",
    "actions"
  ]
}
```

This improves retrieval.

---

# 40. Historical Retrieval Strategy

For decision questions, do not retrieve only the top few chunks.

Retrieve:

1. Original discussion
2. Alternatives discussion
3. Technical evaluation
4. Decision confirmation
5. Follow-up actions
6. Later references
7. Potential contradictory decisions

This creates a complete context window.

---

# 41. Decision Graph

An advanced implementation can represent decisions as a graph.

```text
Problem
   │
   ▼
Database Requirement
   │
   ├──────────────┐
   ▼              ▼
PostgreSQL      MongoDB
   │              │
   │              └── Flexible schema
   │
   ├── Transactions
   ├── SQL
   ├── Complex joins
   └── Team expertise
   │
   ▼
Final Decision
   │
   ▼
PostgreSQL
   │
   ▼
Implementation Actions
```

---

# 42. Persistent Organizational Memory

Store knowledge at three levels.

## Level 1 — Raw Memory

```text
Audio
Transcript
Timestamp
Speaker
```

## Level 2 — Structured Memory

```text
Summary
Decision
Action
Participant
Topic
Risk
```

## Level 3 — Semantic Memory

```text
Embeddings
Relationships
Historical Context
Decision Links
```

---

# 43. Database Design

## Meetings

```text
meeting_id
title
date
project
audio_path
transcript_path
```

## Participants

```text
participant_id
meeting_id
name
role
```

## Decisions

```text
decision_id
meeting_id
title
decision
confidence
timestamp
status
```

## Decision Reasons

```text
reason_id
decision_id
reason
source_chunk_id
```

## Alternatives

```text
alternative_id
decision_id
name
evaluation
```

## Actions

```text
action_id
meeting_id
description
owner
due_date
status
```

## Transcript Chunks

```text
chunk_id
meeting_id
speaker
start_time
end_time
text
```

---

# 44. Hallucination Prevention

This is critical.

Implement:

## Grounded RAG

The LLM receives retrieved evidence.

## Structured Extraction

Use Pydantic models.

## Source Attribution

Every important claim has a source.

## Confidence Score

Expose confidence.

## Insufficient Evidence

Return:

```text
I could not find sufficient evidence in the
available meeting records to establish why
this decision was made.
```

## No Unsupported Facts

Do not invent:

- Participant names
- Dates
- Reasons
- Actions
- Decision status

---

# 45. Advanced Feature — Decision Status

Each decision can have:

```text
Proposed
Under Review
Approved
Implemented
Superseded
Cancelled
Unknown
```

Example:

```text
PostgreSQL

Status:
Superseded

Original Decision:
PostgreSQL

Current Decision:
AWS RDS PostgreSQL
```

---

# 46. Advanced Feature — Cross-Meeting Linking

Automatically connect meetings discussing the same topic.

```text
M001
Database Requirements
   │
   ▼
M005
PostgreSQL vs MongoDB
   │
   ▼
M007
Database Decision
   │
   ▼
M010
Database Implementation
```

---

# 47. Advanced Feature — Decision Impact Tracking

Track what happened after a decision.

```text
Decision:
Use PostgreSQL

Result:
Implementation completed

Impact:
Query performance improved

Issue:
Schema migration took longer than expected

Follow-up:
Database optimization meeting
```

This turns meeting memory into organizational learning.

---

# 48. Evaluation Strategy

## 48.1 Transcription Quality

Metrics:

- Word Error Rate (WER)
- Speaker attribution accuracy

## 48.2 Summary Quality

Evaluate:

- Coverage
- Factual consistency
- Relevance
- Conciseness

## 48.3 Decision Extraction

Evaluate:

- Precision
- Recall
- F1-score

Example:

```text
Actual Decisions: 20
Correctly Extracted: 18

Recall = 90%
```

## 48.4 Retrieval Quality

Measure:

- Precision@K
- Recall@K
- MRR
- Context relevance

## 48.5 Answer Quality

Evaluate:

- Faithfulness
- Citation correctness
- Completeness
- Relevance
- Hallucination rate

---

# 49. Testing Strategy

## Unit Tests

Test:

```text
Transcript parser
Pydantic models
Decision extraction
Action extraction
Embedding creation
Retriever
Timeline builder
```

## Integration Tests

Test:

```text
Audio
→ Transcript
→ Memory
→ Vector DB
→ RAG
→ Answer
```

## Edge Cases

Test:

- Empty audio
- Poor-quality audio
- Multiple speakers
- Missing participant names
- Conflicting decisions
- Very long meetings
- No decision found
- No relevant historical evidence
- Duplicate meetings
- Ambiguous questions

---

# 50. Example Test Cases

## Test Case 1

Question:

```text
Why was PostgreSQL selected?
```

Expected:

```text
Correct decision
Correct reasons
Correct sources
```

## Test Case 2

Question:

```text
Who participated in the decision?
```

Expected:

```text
Only evidence-supported participants
```

## Test Case 3

Question:

```text
What alternatives were considered?
```

Expected:

```text
Only alternatives supported by meeting evidence
```

## Test Case 4

Question:

```text
Did the decision change later?
```

Expected:

```text
Current decision status
Relevant later meeting
Source
```

---

# 51. Implementation Milestones

## Milestone 1 — Project Setup

- Create Python environment
- Install dependencies
- Configure Gemini/OpenAI API
- Configure Whisper
- Create Git repository
- Create project structure
- Configure `.env`

## Milestone 2 — Audio Processing

Implement:

- Audio upload
- File storage
- Whisper transcription
- Transcript cleanup
- Timestamp preservation
- Speaker metadata

## Milestone 3 — Meeting Understanding

Implement:

- Meeting summarization
- Topic extraction
- Participant extraction
- Decision extraction
- Action-item extraction
- Risk extraction

## Milestone 4 — Meeting Memory

Implement:

- Meeting memory schema
- Structured JSON
- Database persistence
- Transcript references
- Source metadata

## Milestone 5 — Vector Search

Implement:

- Text chunking
- Embedding generation
- ChromaDB/FAISS
- Metadata storage
- Semantic search

## Milestone 6 — RAG

Implement:

- Query embedding
- Retrieval
- Metadata filtering
- Reranking
- Context construction
- Grounded answer generation

## Milestone 7 — Decision Reconstruction

Implement:

- Decision retrieval
- Historical context retrieval
- Decision timeline
- Alternative tracking
- Reason extraction
- Participant identification
- Action tracking
- Confidence scoring

## Milestone 8 — Advanced Memory

Implement:

- Cross-meeting linking
- Decision evolution
- Contradiction detection
- Decision status
- Impact tracking

## Milestone 9 — FastAPI

Create:

```text
/meetings/upload
/meetings/transcribe
/meetings/process
/search
/ask
/decisions
/decisions/{id}/timeline
/memory/{meeting_id}
```

## Milestone 10 — Streamlit UI

Build:

```text
Upload Meeting
      ↓
Meeting Memory
      ↓
Decision Explorer
      ↓
Historical Search
      ↓
Ask Organizational Memory
      ↓
Decision Timeline
```

## Milestone 11 — Evaluation

Evaluate:

- Transcription
- Extraction
- Retrieval
- RAG
- Source grounding
- Hallucination rate

## Milestone 12 — Deployment

```text
Docker
   ↓
FastAPI
   ↓
Streamlit
   ↓
ChromaDB / PostgreSQL
   ↓
Cloud Deployment
```

---

# 52. Final Feature Set

| Feature | Implementation |
|---|---|
| Audio-to-text | Whisper |
| Meeting Summarization | Gemini/OpenAI |
| Decision Extraction | LLM + Pydantic |
| Action Extraction | LLM + Pydantic |
| Participant Identification | Metadata + diarization |
| Semantic Search | Embeddings + ChromaDB/FAISS |
| Historical Context | RAG |
| Decision Reconstruction | LLM + retrieved evidence |
| Meeting Memory | Structured database |
| Source-Based Answers | RAG + source metadata |
| Decision Timeline | Pandas + database |
| Alternative Tracking | Structured decision model |
| Decision Evolution | Cross-meeting linking |
| Contradiction Detection | LLM + rules |
| Confidence Scoring | Evidence-based scoring |
| API | FastAPI |
| UI | Streamlit |
| Persistence | SQLite/PostgreSQL |
| Deployment | Docker |

---

# 53. Recommended End-to-End Demo

## Step 1 — Upload Historical Meetings

Upload:

```text
Architecture Discussion
Backend Design Meeting
Database Review
Architecture Decision Meeting
Implementation Review
```

## Step 2 — Convert Audio to Text

Whisper produces timestamped transcripts.

## Step 3 — Process Meetings

The LLM extracts:

```text
Summary
Topics
Decisions
Reasons
Alternatives
Participants
Actions
Risks
```

## Step 4 — Create Meeting Memory

Store structured information.

## Step 5 — Generate Embeddings

Store transcript chunks and meeting memories in ChromaDB/FAISS.

## Step 6 — Ask a Historical Question

```text
Why did we choose PostgreSQL instead of MongoDB
three months ago?
```

## Step 7 — Retrieve Evidence

Retrieve:

```text
Initial database requirements
MongoDB discussion
PostgreSQL evaluation
Final decision
Follow-up implementation meeting
```

## Step 8 — Reconstruct Decision

Return:

```text
Decision:
PostgreSQL

Reasons:
1. Strong transactions
2. Relational data model
3. Complex joins
4. Existing expertise

Alternative:
MongoDB

Participants:
Tech Lead
Backend Engineer
Product Manager

Actions:
Create schema
Configure staging database
```

## Step 9 — Show Sources

```text
Architecture Review
May 20, 2026
00:24:10

Backend Design Meeting
May 22, 2026
00:18:42

Architecture Decision Meeting
May 25, 2026
00:31:20
```

## Step 10 — Show Timeline

```text
Problem
  ↓
Alternatives
  ↓
Evaluation
  ↓
Decision
  ↓
Implementation
  ↓
Follow-up
```

---

# 54. Most Important Architecture Principle

The project should **not** be:

```text
Meeting Audio
      ↓
LLM
      ↓
Summary
```

Instead:

```text
Meeting Audio
      ↓
Speech-to-Text
      ↓
Structured Meeting Understanding
      ↓
Persistent Meeting Memory
      ↓
Embeddings + Metadata
      ↓
Vector Database
      ↓
Semantic / Hybrid Retrieval
      ↓
Historical Context
      ↓
Decision Reconstruction
      ↓
Source-Based Answer
```

The key idea is that the system should preserve **not just what was said, but why a decision was made and how that decision evolved over time**.

---

# 55. Final Project Value

This project demonstrates:

- Generative AI
- Speech-to-text
- Prompt engineering
- Structured LLM output
- Pydantic validation
- RAG
- Vector databases
- Semantic search
- Hybrid retrieval
- Historical reasoning
- Decision reconstruction
- Organizational memory
- Source grounding
- Hallucination prevention
- Knowledge extraction
- FastAPI
- Streamlit
- Data processing
- Persistent storage

The key differentiator is:

**Meeting Transcription + Structured Memory + RAG + Historical Context + Decision Reconstruction + Source-Based Answers**

This makes the application more than a meeting summarizer. It becomes an **AI organizational memory system capable of explaining the reasoning behind past decisions.**
