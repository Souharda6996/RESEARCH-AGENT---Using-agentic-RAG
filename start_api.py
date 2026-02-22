"""
Research Agent API Server Launcher
Auto-loads .env file for GROQ_API_KEY, then starts the FastAPI server.
"""
import sys
import os
from pathlib import Path

# ── Load .env if present ──────────────────────────────────────────────────────
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())
    print(f"✅ Loaded environment from .env")

groq_key = os.environ.get("GROQ_API_KEY", "")
if groq_key and groq_key != "your_groq_api_key_here":
    print(f"✅ GROQ_API_KEY found — AI-powered answers enabled")
else:
    print("⚠️  GROQ_API_KEY not set — add it to .env for AI-powered answers")
    print("   Get a free key at: https://console.groq.com/")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║     Research Agent API Server v3.0     ║
    ║   6-Agent Pipeline — FastAPI + Groq    ║
    ╚════════════════════════════════════════╝

    API:  http://localhost:8000
    Docs: http://localhost:8000/docs

    Press Ctrl+C to stop.
    """)

    uvicorn.run(
        "research_agent.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
