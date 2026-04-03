# ContractIQ

An AI-powered contract risk analysis tool. Upload a contract PDF, anonymize PII, then run a multi-agent adversarial audit that scores legal, financial, compliance, operational, data, and termination risk — with a full downloadable PDF report.

---

## Architecture

```
contractiq/
├── ai/                         # AI pipeline (LangGraph agents + helpers)
│   ├── evaluator.py            # Multi-agent LangGraph risk evaluation graph
│   ├── helper.py               # PDF→Markdown, PII anonymizer, RAG/ChromaDB utils
│   └── chroma_hemas/           # ChromaDB vector store (auto-created on first run)
│
├── backend/                    # FastAPI backend
│   ├── main.py                 # App entry point + CORS config
│   ├── requirements.txt        # Python dependencies
│   └── src/app/
│       ├── api/contracts.py    # REST endpoints (anonymize, evaluate, download)
│       └── services/
│           ├── anonymization_service.py
│           ├── rag_service.py
│           └── pdf_service.py
│
├── frontend/                   # React + Vite + Tailwind frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── types.ts
│   │   └── components/
│   │       ├── Anonymizer.tsx
│   │       ├── AuditDashboard.tsx
│   │       ├── Layout.tsx
│   │       └── Report.tsx
│   └── package.json
│
└── storage/                    # Runtime file storage (auto-created)
    ├── uploads/                # Uploaded contract PDFs
    └── processed/              # Anonymized JSON + generated PDFs
```

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10 – 3.12 | 3.11 recommended |
| Node.js | 18+ | 20 LTS recommended |
| npm | 9+ | Comes with Node |

You also need a **Groq API key** (free): https://console.groq.com

---

## Setup

### 1. Clone / unzip the project

```bash
unzip contractiq.zip
cd contractiq
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Set up the Python backend

```bash
python -m venv-ai
```

Activate the virtual environment:

- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```

Install dependencies:
```bash
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

### 4. Seed the ChromaDB vector store

The evaluator needs a populated ChromaDB to retrieve risk rules. Seed it with at least one contract before the first use:

```bash
cd ../ai
python - <<'EOF'
from helper import process_contract, pdf_to_markdown
# Point this at any contract PDF you have, or use the sample below
text = """
This Software License Agreement is entered into between Licensor and Licensee.
Licensor grants a non-exclusive, non-transferable license to use the software.
Licensee shall not sublicense, sell, or redistribute the software.
The agreement may be terminated by either party with 30 days written notice.
Licensor's liability shall not exceed the fees paid in the preceding 12 months.
Licensee shall indemnify Licensor against third-party claims arising from misuse.
All disputes shall be resolved by binding arbitration under AAA rules.
"""
process_contract(text)
print("ChromaDB seeded successfully.")
EOF
```

> **Tip:** If you have sample contract PDFs, you can seed from them using `feed_rules("path/to/contracts/folder")` in `helper.py`.

### 5. Set up the frontend

```bash
cd ../frontend
npm install
```

---

## Running the App

You need **two terminals** running simultaneously.

### Terminal 1 — Backend

```bash
source venv/bin/activate   # Windows: venv\Scripts\activate.bat
python uvicorn backend.src.app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

The app will be available at: http://localhost:3000

---

## Usage

1. **Upload & Anonymize** — Drop a contract PDF. The app extracts text and strips PII (names, orgs, emails, etc.) using Presidio + BERT NER. The original and anonymized versions are shown side-by-side.

2. **Run Audit** — Click "Run adversarial audit". A LangGraph multi-agent pipeline evaluates the anonymized contract across 6 risk dimensions, streaming results live.

3. **View Report** — See the structured risk report with scores, risk areas, and recommendations. Download a PDF copy.

---

## Troubleshooting

**`collection does not exist` error on startup**
→ You haven't seeded ChromaDB yet. Run the seed script in Step 4.

**Presidio / transformers model download slow on first run**
→ The `dslim/bert-base-NER` model is downloaded from HuggingFace on first use (~400MB). This is normal.

**CORS errors in the browser**
→ Make sure the backend is running on port 8000 and the frontend on port 3000. Both ports are pre-configured.

**`ModuleNotFoundError: No module named 'backend'`**
→ Always run uvicorn from the `backend/` directory, not the project root.

**Windows: `venv\Scripts\Activate.ps1` blocked by execution policy**
→ Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | API key from https://console.groq.com |

---

## Tech Stack

**Backend:** FastAPI · Uvicorn · Presidio · Docling · LangGraph · LangChain · ChromaDB · Groq (Llama 4 Scout) · ReportLab

**Frontend:** React 18 · TypeScript · Vite · Tailwind CSS · Framer Motion · Lucide Icons
