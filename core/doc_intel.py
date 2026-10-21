"""Document Intelligence module for extracting, summarizing, and parsing documents."""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pypdf
from core.scanner import compute_full_sha256
from core.llm_service import LLMService
from core.db import get_document_summary, save_document_summary

def extract_text_from_file(file_path: str, max_chars: int = 50000) -> Dict[str, Any]:
    """
    Extract readable text and metadata from supported file formats (PDF, TXT, MD, Code, CSV, etc.).
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return {"text": "", "error": "File does not exist", "metadata": {}}

    ext = path.suffix.lower()
    text = ""
    error = None
    page_count = 1

    try:
        if ext == ".pdf":
            try:
                reader = pypdf.PdfReader(str(path))
                page_count = len(reader.pages)
                extracted_pages = []
                for i, page in enumerate(reader.pages):
                    extracted = page.extract_text() or ""
                    extracted_pages.append(extracted)
                    if sum(len(p) for p in extracted_pages) >= max_chars:
                        break
                text = "\n\n".join(extracted_pages)
                if not text.strip():
                    text = f"Document '{path.name}' was scanned or contains image/vector content without embedded text."
            except Exception as pdf_err:
                text = f"Document '{path.name}' could not be parsed as standard PDF text ({str(pdf_err)})."
        else:
            # Plain text, Markdown, Code, CSV, etc.
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read(max_chars)
    except Exception as e:
        error = f"Extraction failed: {str(e)}"

    stat = path.stat()
    lines = text.splitlines()
    words = text.split()

    metadata = {
        "file_name": path.name,
        "file_path": str(path),
        "extension": ext,
        "file_size": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "line_count": len(lines),
        "word_count": len(words),
        "char_count": len(text),
        "page_count": page_count if ext == ".pdf" else None
    }

    return {
        "text": text,
        "error": error,
        "metadata": metadata
    }

def analyze_document_file(file_path: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Full pipeline: extract text, check cache, query LLMService, and return
    structured editorial intelligence.
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": "File not found"}

    file_hash = compute_full_sha256(path)

    # Check cache unless force refresh
    if not force_refresh:
        cached = get_document_summary(str(path), file_hash)
        if cached:
            cached["cached"] = True
            return cached

    extraction = extract_text_from_file(str(path))
    if extraction.get("error"):
        return {"error": extraction["error"], "metadata": extraction.get("metadata", {})}

    raw_text = extraction["text"]
    if not raw_text.strip():
        return {
            "summary": "Document appears to be empty or contains non-extractable media content.",
            "action_items": [],
            "key_dates": [],
            "metadata": extraction["metadata"],
            "model_used": "none",
            "cached": False
        }

    llm = LLMService()
    active_model = llm.get_preferred_model()
    analysis = llm.analyze_document(raw_text, path.name)

    # Save to DB cache
    save_document_summary(
        file_path=str(path),
        file_hash=file_hash,
        file_name=path.name,
        summary=analysis["summary"],
        action_items=analysis["action_items"],
        key_dates=analysis["key_dates"],
        metadata=extraction["metadata"],
        model_used=active_model
    )

    return {
        "file_path": str(path),
        "file_name": path.name,
        "file_hash": file_hash,
        "summary": analysis["summary"],
        "action_items": analysis["action_items"],
        "key_dates": analysis["key_dates"],
        "metadata": extraction["metadata"],
        "model_used": active_model,
        "source": analysis.get("source", "local_llm"),
        "cached": False
    }
