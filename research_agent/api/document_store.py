"""
DocumentStore — in-memory store for uploaded research paper content.
Uses pypdf for proper PDF text extraction.
"""
import re
import io
from typing import Dict, List, Any, Optional
from datetime import datetime


class DocumentStore:
    """Singleton in-memory document store."""

    _instance: Optional["DocumentStore"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._docs: Dict[str, Dict[str, Any]] = {}
        return cls._instance

    # ── Text extraction ──────────────────────────────────────────────────────

    @staticmethod
    def extract_text(raw_bytes: bytes, filename: str) -> str:
        fname = filename.lower()

        # Plain text formats
        if fname.endswith((".txt", ".md", ".rst", ".csv", ".tsv", ".json", ".jsonl")):
            return raw_bytes.decode("utf-8", errors="ignore")

        # PDF — use pypdf for proper text extraction
        if fname.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                pages = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text.strip())
                if pages:
                    return "\n\n".join(pages)
            except Exception:
                pass
            # Byte-strip fallback
            text = raw_bytes.decode("latin-1", errors="ignore")
            readable = re.findall(r"[ -~\n\r\t]{4,}", text)
            return re.sub(r"\s{3,}", "\n", " ".join(readable)).strip()

        # DOCX — use python-docx if available, fallback to XML strip
        if fname.endswith((".docx", ".doc")):
            try:
                import docx
                doc = docx.Document(io.BytesIO(raw_bytes))
                return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            except Exception:
                pass
            # XML fallback: strip XML tags from the zip contents
            try:
                import zipfile
                with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
                    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
                return re.sub(r"<[^>]+>", " ", xml)
            except Exception:
                pass

        # Fallback: try UTF-8
        return raw_bytes.decode("utf-8", errors="ignore")

    # ── Chunking ─────────────────────────────────────────────────────────────

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, Any]]:
        """Split text into overlapping word-level chunks."""
        words = text.split()
        chunks = []
        step = chunk_size - overlap
        for i in range(0, len(words), step):
            chunk_words = words[i: i + chunk_size]
            if len(chunk_words) < 30:
                break
            chunks.append({
                "chunk_id": f"chunk_{len(chunks):04d}",
                "text": " ".join(chunk_words),
                "start_word": i,
            })
        return chunks

    # ── Entity extraction ─────────────────────────────────────────────────────

    @staticmethod
    def extract_entities(text: str) -> List[Dict[str, Any]]:
        found: Dict[str, str] = {}
        for m in re.finditer(r"[A-Z][a-z]+ et al\.", text):
            found[m.group()] = "author"
        for m in re.finditer(r"[A-Z][a-z]+ (?:and|&) [A-Z][a-z]+", text):
            found[m.group()] = "author"
        for m in re.finditer(r"\b[A-Z]{2,8}(?:-?\d+)?\b", text):
            tok = m.group()
            if tok not in {"PDF","DOI","URL","HTTP","API","GPU","CPU","RAM","THE","AND","FOR"}:
                found[tok] = "method"
        for m in re.finditer(r"\b[A-Z][a-z]{2,}(?:[A-Z][a-z]{2,})+\b", text):
            found[m.group()] = "concept"
        for m in re.finditer(r"\b(19|20)\d{2}\b", text):
            found[m.group()] = "year"
        entities = [
            {"id": f"ent_{i:04d}", "name": name, "type": etype,
             "count": len(re.findall(re.escape(name), text))}
            for i, (name, etype) in enumerate(found.items())
        ]
        entities.sort(key=lambda e: e["count"], reverse=True)
        return entities[:80]

    @staticmethod
    def extract_relations(text: str, entities: List[Dict]) -> List[Dict[str, Any]]:
        sentences = re.split(r"[.!?]\s+", text)
        names = [e["name"] for e in entities[:30]]
        counts: Dict[str, int] = {}
        for s in sentences:
            present = [n for n in names if n in s]
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    key = f"{present[i]}|||{present[j]}"
                    counts[key] = counts.get(key, 0) + 1
        relations = []
        for pair, w in sorted(counts.items(), key=lambda x: -x[1])[:40]:
            src, tgt = pair.split("|||")
            relations.append({"source": src, "target": tgt, "type": "co-occurs", "weight": w})
        return relations

    # ── Keyword search ────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        if not self._docs:
            return []
        keywords = set(re.findall(r"\b\w{3,}\b", query.lower()))
        scored = []
        for doc_id, doc in self._docs.items():
            for chunk in doc["chunks"]:
                cw = set(chunk["text"].lower().split())
                score = len(keywords & cw) / (len(keywords) + 1e-9)
                if score > 0:
                    scored.append((score, doc_id, chunk))
        scored.sort(key=lambda x: -x[0])
        return [
            {
                "doc_id": doc_id,
                "filename": self._docs[doc_id]["filename"],
                "chunk_id": ch["chunk_id"],
                "text": ch["text"],
                "relevance_score": round(min(s * 2, 1.0), 3),
            }
            for s, doc_id, ch in scored[:top_k]
        ]

    def search_sentences(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find the most relevant individual sentences from all documents."""
        if not self._docs:
            return []
        keywords = set(re.findall(r"\b\w{3,}\b", query.lower()))
        # Common stop words to ignore in scoring
        stop = {"the","and","for","are","was","were","has","have","had","this","that",
                "with","from","they","its","into","than","then","been","also","will",
                "can","but","not","per","via","our","all","any","one","two","use",
                "used","using","each","more","most","some","such","both","other"}
        keywords -= stop

        sentences = []
        for doc_id, doc in self._docs.items():
            # Split into sentences
            raw_sents = re.split(r"(?<=[.!?])\s+", doc["text"])
            for sent in raw_sents:
                sent = sent.strip()
                if len(sent) < 30 or len(sent) > 800:
                    continue
                sw = set(re.findall(r"\b\w{3,}\b", sent.lower())) - stop
                overlap = len(keywords & sw)
                if overlap > 0:
                    score = overlap / (len(keywords) + 1e-9)
                    sentences.append((score, sent, doc["filename"]))

        sentences.sort(key=lambda x: -x[0])
        seen, out = set(), []
        for score, sent, fname in sentences:
            key = sent[:60]
            if key not in seen:
                seen.add(key)
                out.append({"text": sent, "filename": fname, "score": round(score, 3)})
            if len(out) >= top_k:
                break
        return out


    # ── Store / retrieve ──────────────────────────────────────────────────────

    def add_document(self, doc_id: str, filename: str, raw_bytes: bytes) -> Dict[str, Any]:
        text = self.extract_text(raw_bytes, filename)
        chunks = self.chunk_text(text)
        entities = self.extract_entities(text)
        relations = self.extract_relations(text, entities)
        self._docs[doc_id] = {
            "doc_id": doc_id, "filename": filename, "text": text,
            "word_count": len(text.split()), "chunks": chunks,
            "entities": entities, "relations": relations,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        return {
            "doc_id": doc_id, "filename": filename,
            "word_count": len(text.split()), "num_chunks": len(chunks),
            "entities_extracted": len(entities), "relations_extracted": len(relations),
        }

    def get_document(self, doc_id: str) -> Optional[Dict]:
        return self._docs.get(doc_id)

    def all_entities(self) -> List[Dict]:
        out = []
        for d in self._docs.values():
            out.extend(d["entities"])
        return out

    def all_relations(self) -> List[Dict]:
        out = []
        for d in self._docs.values():
            out.extend(d["relations"])
        return out

    def all_chunks(self) -> List[Dict]:
        out = []
        for d in self._docs.values():
            out.extend(d["chunks"])
        return out

    def full_text(self) -> str:
        """Return concatenated text from all uploaded documents (first 15000 chars)."""
        return "\n\n".join(
            f"=== {d['filename']} ===\n{d['text']}"
            for d in self._docs.values()
        )[:15000]

    @property
    def doc_count(self) -> int:
        return len(self._docs)

    @property
    def is_empty(self) -> bool:
        return len(self._docs) == 0


# Global singleton
store = DocumentStore()
