# ContractIQ 🔍

### AI-Powered Legal Document Auditing & Risk Mitigation System

**AITHON 2026 — Team_404 | University of Moratuwa**
**Challenge Track:** D2D Corporate Use Cases | AI Powered Automation
**Target SBU:** Centre of Excellence (COE) — Hemas Holdings PLC

---

## Overview

ContractIQ is a multi-agent AI system that automates legal contract risk auditing for the Hemas Centre of Excellence. It replaces a manual 3–5 day contract review process with an adversarial AI pipeline that produces a structured risk report in under 2 minutes.

The system combines:

- **Microsoft Presidio + BERT NER** for local PII anonymization before any data leaves the environment
- **LangGraph multi-agent orchestration** with specialist Legal, Financial, and Compliance agents
- **DeepSeek / Groq LLM** for structured risk analysis with Pydantic output schemas
- **Fuzzy entity matching** via `thefuzz` to handle entity variations across a document

### Key Output (from live test run)

```
FINAL SCORE: 0.28 (Low-Moderate Risk)
Elapsed time: 83.78s

"This Mutual Non-Disclosure Agreement presents a moderate overall risk
profile... broad legal process exemptions with minimal 7-day notice,
unilateral withdrawal rights with only 10 days notice, no warranties
on information accuracy..."
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  LOCAL ENVIRONMENT (Secure Zone)             │
│                                                             │
│  [Contract PDF/DOCX]                                        │
│        │                                                    │
│        ▼                                                    │
│  ┌─────────────┐    Docling parses PDF/DOCX                 │
│  │  Ingestion  │    preserving structure & tables           │
│  └──────┬──────┘                                            │
│         │ raw text                                          │
│         ▼                                                   │
│  ┌──────────────────┐   Presidio Analyzer +                 │
│  │  PII Anonymizer  │   dslim/bert-base-NER transformer     │
│  │  (Presidio+BERT) │   thefuzz for entity deduplication    │
│  └──────┬───────────┘                                       │
│         │ anonymized text + entity_map                      │
│         │                                                   │
│  ░░░░░░ PRIVACY BOUNDARY ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
└─────────┼───────────────────────────────────────────────────┘
          │ (only anonymized text crosses boundary)
          ▼
┌─────────────────────────────────────────────────────────────┐
│                  LANGGRAPH AGENT PIPELINE                    │
│                                                             │
│  ┌──────────────┐                                           │
│  │ Legal Agent  │ → legal_risk (0-1) + comment             │
│  └──────┬───────┘                                           │
│         │                                                   │
│  ┌──────▼──────────┐                                        │
│  │ Financial Agent │ → financial_risk (0-1) + comment      │
│  └──────┬──────────┘                                        │
│         │                                                   │
│  ┌──────▼──────────────┐                                    │
│  │  Compliance Agent   │ → compliance_risk (0-1) + comment │
│  └──────┬──────────────┘                                    │
│         │                                                   │
│  ┌──────▼──────────┐                                        │
│  │    Evaluator    │ → final_score + risk_report            │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │ De-anonymize │ → restore original entity values
   └──────┬───────┘
          ▼
   [ Final Risk Report ]
```

---

## Tech Stack

| Layer                | Technology                                  | Purpose                                     |
| -------------------- | ------------------------------------------- | ------------------------------------------- |
| Document Ingestion   | `docling`                                   | Parse PDF/DOCX preserving layout and tables |
| PII Detection        | `presidio-analyzer` + `presidio-anonymizer` | Enterprise-grade entity detection           |
| NER Model            | `dslim/bert-base-NER` (HuggingFace)         | Transformer-based named entity recognition  |
| Entity Deduplication | `thefuzz`                                   | Fuzzy matching to catch entity variations   |
| Agent Orchestration  | `LangGraph`                                 | Stateful multi-agent workflow graph         |
| LLM                  | `DeepSeek` / `Groq (Llama 3.3 70B)`         | Structured risk analysis                    |
| Structured Output    | `Pydantic` + `langchain structured_output`  | Type-safe agent responses                   |
| Runtime              | `Google Colab` (Python 3.12)                | Development and execution environment       |

---

## Agent Design

The pipeline uses a **LangGraph StateGraph** with four sequential nodes:

### State Schema

```python
class ContractState(TypedDict):
    text: str                    # anonymized contract text
    comments: List[BaseMessage]  # accumulated agent comments
    legal_risk: float            # 0-1 score from legal agent
    financial_risk: float        # 0-1 score from financial agent
    compliance_risk: float       # 0-1 score from compliance agent
    final_score: float           # aggregated final score
    final_report: str            # narrative risk report
```

### Agent Responsibilities

**Legal Agent**
Analyzes clauses for unfair terms, one-sided obligations, missing protections, and liability exposure. Returns `legal_risk` (0–1) and a brief explanation.

**Financial Agent**
Examines payment terms, penalty clauses, monetary obligations, and financial liability caps. Returns `financial_risk` (0–1) and a brief explanation.

**Compliance Agent**
Reviews regulatory alignment, governance requirements, and legal obligation gaps. Returns `compliance_risk` (0–1) and a brief explanation.

**Evaluator**
Receives all three risk scores and agent comments. Produces a 100–200 word final risk report in markdown and an aggregated `final_score` (0–1).

### Graph Flow

```
START → legal → financial → compliance → evaluator → END
```

---

## Anonymization Pipeline

ContractIQ uses **Microsoft Presidio** with a **BERT transformer backbone** (`dslim/bert-base-NER`) for high-accuracy PII detection. This is significantly more reliable than regex-only approaches.

### Detected Entity Types

```python
entity_types = [
    "CREDIT_CARD", "CRYPTO", "EMAIL_ADDRESS", "IBAN_CODE",
    "IP_ADDRESS", "MAC_ADDRESS", "NRP", "LOCATION",
    "PERSON", "PHONE_NUMBER", "MEDICAL_LICENSE",
    "URL", "ORGANIZATION"
]
```

### Fuzzy Entity Deduplication

The `find_similar_entity` function uses `thefuzz` to match variations of the same entity (e.g. "Hemas" and "Hemas Ltd" both map to the same token), preventing redundant placeholder creation:

```python
def find_similar_entity(entity_text, entity_map, threshold=80):
    choices = list(entity_map.keys())
    closest = process.extractOne(entity_text, choices)
    if closest and closest[1] > threshold:
        return closest[0]
    return None
```

### Overlap Resolution

Nested or overlapping entity detections are resolved before replacement to prevent malformed output:

```python
def remove_overlaps(results):
    results = sorted(results, key=lambda x: (x.start, -(x.end - x.start)))
    filtered = []
    for r in results:
        if not any(not (r.end <= f.start or r.start >= f.end) for f in filtered):
            filtered.append(r)
    return filtered
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Google Colab (recommended) or local environment with GPU for BERT inference

### Install Dependencies

```bash
pip install presidio-analyzer
pip install presidio-anonymizer
pip install "presidio-analyzer[transformers]"
pip install docling
pip install thefuzz
pip install langgraph
pip install langchain-deepseek
pip install langchain-google-genai
pip install langchain-groq
pip install torch
```

### API Keys Required

The notebook reads API keys from Google Colab Secrets (`userdata`). Add the following secrets in your Colab environment:

| Secret Name        | Description                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| `DEEPSEEK_API_KEY` | DeepSeek API key — get free at [platform.deepseek.com](https://platform.deepseek.com)           |
| `GOOGLE_API_KEY`   | Google Gemini API key — get free at [aistudio.google.com](https://aistudio.google.com)          |
| `GROQ_API_KEY`     | Groq API key (recommended for speed) — get free at [console.groq.com](https://console.groq.com) |

---

## Usage

### Running in Google Colab

1. Open `Hemas_project.ipynb` in Google Colab
2. Add your API keys to Colab Secrets
3. Run all cells in order:
   - **Cell 1:** Install dependencies
   - **Cell 2:** Load and parse contract document using Docling
   - **Cell 3:** Run Presidio PII anonymization
   - **Cell 4:** Run LangGraph multi-agent audit pipeline
4. Final output prints the risk report and score

### Switching LLM Provider

The notebook currently uses DeepSeek. To switch to Groq (recommended — significantly faster):

```python
# Replace DeepSeek with Groq
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0,
    api_key=GROQ_API_KEY
)
```

---

## Sample Output

Tested on a **Cyber Mutual Assistance NDA**:

```
──────────────────────────────────────────────────
This Mutual Non-Disclosure Agreement for a Cyber
Mutual Assistance Program presents a moderate overall
risk profile with balanced protections and concerning
provisions.

Key risks identified:
• Broad legal process exemptions with minimal 7-day notice
• Unilateral withdrawal rights with only 10 days notice
• No warranties on information accuracy
• Potential conflicts with regulatory reporting requirements
• Elevated compliance risks due to mandatory cybersecurity
  reporting obligation conflicts
──────────────────────────────────────────────────

FINAL SCORE: 0.28
──────────────────────────────────────────────────
Elapsed time: 83.78s
```

---

## Known Issues & Planned Improvements

| Issue                               | Status     | Plan                                       |
| ----------------------------------- | ---------- | ------------------------------------------ |
| 83s execution time with DeepSeek    | 🔴 Active  | Switch to Groq API — expected <15s         |
| No de-anonymization of final report | 🔴 Active  | Add token re-mapping after evaluator node  |
| No RAG knowledge base               | 🟡 Planned | Add ChromaDB with Sri Lankan legal corpus  |
| AUDITOR/ATTACKER adversarial loop   | 🟡 Planned | Restructure to match proposal architecture |
| No frontend UI                      | 🟡 Planned | Streamlit or React dashboard               |
| Risk score on 0–1 scale             | 🟡 Planned | Convert to 0–100 for display consistency   |

---

## Project Structure

```
contractiq/
├── Hemas_project.ipynb     # Main notebook — full pipeline
├── README.md               # This file
└── knowledge_base/         # (planned)
    ├── sl_laws/            # Sri Lankan legal documents
    ├── past_contracts/     # Annotated historical contracts
    └── templates/          # COE standard clause templates
```

---

## Team

**Team_404 — University of Moratuwa**
AITHON 2026 | Hemas Holdings PLC AI Innovation Challenge
Target: Centre of Excellence (COE) | D2D Track

---

## Competition Context

This project was built for **AITHON 2026**, an enterprise AI innovation challenge by Hemas Holdings PLC's Technology & Transformation Team. The solution targets the COE's legal and procurement operations, where manual contract review currently takes 3–5 days per document across six Strategic Business Units.

**Functional Contract (Grand Finale deliverables):**

1. Anonymized Contract Upload & Processing Pipeline
2. Multi-Agent Adversarial Audit Loop with RAG Grounding
3. Structured Risk Report Generation & Dashboard
