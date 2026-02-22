# 🔬 Research Agent — AI-Powered Research Paper Assistant

An intelligent multi-agent system that reads your uploaded research papers and answers any question about them using Groq LLaMA AI.

---

## 📋 Requirements

- **Python 3.10+**
- **Node.js 18+** and **npm**
- A free **Groq API key** → [console.groq.com](https://console.groq.com/)

---

## ⚡ Quick Start

### Step 1 — Clone & install backend dependencies

```powershell
cd e:\pcl\research_agent
pip install -r requirements-api.txt
pip install groq pypdf
```

### Step 2 — Add your Groq API key

Create a file called `.env` in `e:\pcl\research_agent\`:

```
GROQ_API_KEY=gsk_your_key_here
```

> Get a free key at [console.groq.com](https://console.groq.com/) → Sign Up → API Keys → Create Key

### Step 3 — Start the backend (Terminal 1)

```powershell
cd e:\pcl\research_agent
python start_api.py
```

You should see:
```
✅ GROQ_API_KEY found — AI-powered answers enabled
✅ Uvicorn running on http://0.0.0.0:8000
```

### Step 4 — Install & start the frontend (Terminal 2)

```powershell
cd e:\pcl\research_agent\frontend-next
npm install
npm run dev
```

You should see:
```
✓ Ready on http://localhost:3000
```

### Step 5 — Open your browser

👉 **http://localhost:3000**

---

## 🖥️ How to Use

| Step | Action |
|------|--------|
| 1 | Go to **Upload** page (`/upload`) |
| 2 | Drag & drop your paper (PDF, DOCX, TXT, CSV, JSON) |
| 3 | Wait for indexing to complete (~5 seconds) |
| 4 | Go to **Chat** page (`/chat`) |
| 5 | Ask anything about your paper |

### Example questions you can ask:
- *"What is this paper about?"*
- *"What methods were used?"*
- *"What are the main results?"*
- *"Show me the knowledge graph"*
- *"Who are the authors?"*
- *"What are the limitations?"*
- *"Summarize the conclusion"*

---

## 📁 Supported File Formats

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Word Document | `.docx`, `.doc` |
| Plain Text | `.txt`, `.md` |
| CSV / TSV | `.csv`, `.tsv` |
| JSON | `.json`, `.jsonl` |

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/api/health |

---

## 🗂️ Project Structure

```
research_agent/
├── start_api.py              ← Start the backend server
├── .env                      ← Your Groq API key (create this)
├── .env.example              ← Template for .env
├── requirements-api.txt      ← Python dependencies
│
├── research_agent/
│   └── api/
│       ├── server.py         ← FastAPI backend (query pipeline)
│       └── document_store.py ← Document storage & text extraction
│
└── frontend-next/            ← Next.js frontend
    ├── app/
    │   ├── page.tsx          ← Landing page
    │   ├── upload/page.tsx   ← Upload documents
    │   └── chat/page.tsx     ← Ask questions
    └── package.json
```

---

## 🛠️ Troubleshooting

### Backend won't start
```powershell
pip install fastapi uvicorn groq pypdf python-multipart
python start_api.py
```

### Frontend won't start
```powershell
cd frontend-next
npm install
npm run dev
```

### Answers are not AI-powered
Make sure `.env` exists with a valid `GROQ_API_KEY`. The backend startup will print:
- ✅ `GROQ_API_KEY found` — AI answers enabled
- ⚠️ `GROQ_API_KEY not set` — showing extractive answers only

### Uploaded paper disappears after restart
The document store is **in-memory** — you need to re-upload after restarting the backend. The frontend will remember the file list but you must re-upload for the backend to process it again.

---

## 🤖 Agent Pipeline

Every query runs through 6 specialized agents:

1. **LiteratureReviewAgent** — retrieves relevant chunks from the paper
2. **DataProcessingAgent** — filters and ranks content
3. **KnowledgeGraphAgent** — extracts entities and relations
4. **AnalysisAgent** — identifies patterns and statistics
5. **WritingAssistantAgent** — generates the final answer via Groq LLM
6. **CollaborationAgent** — logs the session

---

## 📄 License

MIT License — see [LICENSE](LICENSE)