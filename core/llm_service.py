"""Local LLM Service for LazyDesk AI interfacing with Ollama."""
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
import requests
from core.config import DEFAULT_OLLAMA_HOST, DEFAULT_MODEL, FALLBACK_MODEL
from core.db import get_setting

class LLMService:
    def __init__(self, host: Optional[str] = None):
        self._host = host

    @property
    def host(self) -> str:
        if self._host:
            return self._host
        return get_setting("ollama_host", DEFAULT_OLLAMA_HOST) or DEFAULT_OLLAMA_HOST

    def check_connection(self) -> Tuple[bool, List[str], str, float]:
        """Check if local Ollama instance is alive, list models, and measure latency."""
        t0 = time.time()
        try:
            resp = requests.get(f"{self.host.rstrip('/')}/api/tags", timeout=2.0)
            latency = (time.time() - t0) * 1000
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return True, models, "Connected", round(latency, 1)
            return False, [], f"HTTP {resp.status_code}", round(latency, 1)
        except requests.exceptions.ConnectionError:
            return False, [], "Ollama daemon not reachable", 0.0
        except Exception as e:
            return False, [], str(e), 0.0

    def get_preferred_model(self) -> str:
        """Get currently selected or best available model."""
        pref = get_setting("preferred_model")
        connected, models, _, _ = self.check_connection()
        if connected and models:
            if pref and pref in models:
                return pref
            # Check for gemma or qwen
            for m in models:
                if "gemma" in m.lower():
                    return m
            for m in models:
                if "qwen" in m.lower():
                    return m
            return models[0]
        return pref or DEFAULT_MODEL

    def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None, max_tokens: int = 500) -> Optional[str]:
        """Generate response from local Ollama model."""
        target_model = model or self.get_preferred_model()
        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": max_tokens
            }
        }
        try:
            resp = requests.post(
                f"{self.host.rstrip('/')}/api/generate",
                json=payload,
                timeout=45.0
            )
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception:
            pass
        return None

    def analyze_document(self, text: str, file_name: str) -> Dict[str, Any]:
        """Generate summary, action items, and key dates from document text."""
        # Truncate text for context limits
        snippet = text[:4000]

        system_prompt = (
            "You are LazyDesk AI, an expert local document assistant. Analyze the document objectively. "
            "Return valid JSON ONLY with three keys: "
            "'summary' (2-3 concise editorial sentences), "
            "'action_items' (list of concrete actionable steps/todos extracted), "
            "'key_dates' (list of dates/deadlines mentioned). "
            "Do not include any greeting or conversational filler. JSON only."
        )

        user_prompt = f"Filename: {file_name}\n\nDocument Text:\n{snippet}\n\nProvide JSON response:"

        raw_output = self.generate(user_prompt, system_prompt=system_prompt)
        parsed = self._parse_json_or_fallback(raw_output, text, file_name)
        return parsed

    def _parse_json_or_fallback(self, raw_output: Optional[str], original_text: str, file_name: str) -> Dict[str, Any]:
        """Parse model JSON response, or use heuristic extraction if model output is missing or malformed."""
        if raw_output:
            try:
                # Remove code blocks if present
                clean = re.sub(r"^```(?:json)?\s*", "", raw_output.strip())
                clean = re.sub(r"\s*```$", "", clean)
                data = json.loads(clean)
                if isinstance(data, dict):
                    return {
                        "summary": str(data.get("summary", "")).strip(),
                        "action_items": [str(x) for x in data.get("action_items", []) if str(x).strip()],
                        "key_dates": [str(x) for x in data.get("key_dates", []) if str(x).strip()],
                        "source": "local_llm"
                    }
            except Exception:
                pass

        # Heuristic fallback (fast, deterministic, zero-dependency)
        lines = [line.strip() for line in original_text.splitlines() if line.strip()]
        
        # Summary: take first substantive paragraphs
        summary_sentences = []
        for line in lines[:8]:
            if len(line) > 30 and not line.startswith(("#", "-", "*", "1.", "2.")):
                summary_sentences.append(line)
            if len(summary_sentences) >= 2:
                break
        if not summary_sentences:
            summary = f"Document '{file_name}' contains {len(lines)} lines of text focusing on workspace records."
        else:
            summary = " ".join(summary_sentences[:2])
            if len(summary) > 280:
                summary = summary[:277] + "..."

        # Action items: look for todo, must, should, action, deadline lines
        actions = []
        todo_pattern = re.compile(r"^(?:TODO|FIXME|ACTION|TASK|\-\s*\[\s*\]|\*|\-)\s*(.+)", re.IGNORECASE)
        must_pattern = re.compile(r"\b(must|should|need to|assigned to|deadline|submit|review|complete)\b", re.IGNORECASE)
        for line in lines:
            m = todo_pattern.match(line)
            if m:
                actions.append(m.group(1).strip())
            elif must_pattern.search(line) and len(line) < 140:
                actions.append(line.strip(" -*#"))
            if len(actions) >= 5:
                break
        if not actions:
            actions = ["Review document for upcoming deliverables", "File document in proper archive directory"]

        # Key dates: match YYYY-MM-DD, Month DD, YYYY, etc.
        dates = []
        date_pattern = re.compile(
            r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b",
            re.IGNORECASE
        )
        for line in lines:
            matches = date_pattern.findall(line)
            for match in matches:
                if match not in dates:
                    dates.append(match)
            if len(dates) >= 5:
                break

        return {
            "summary": summary,
            "action_items": actions[:5],
            "key_dates": dates[:5],
            "source": "heuristic_fallback" if not raw_output else "local_llm_repaired"
        }

    def suggest_clean_filename(self, current_name: str, category: str, content_preview: str = "") -> str:
        """Propose a clean, standardized name for a file."""
        stem = Path(current_name).stem
        ext = Path(current_name).suffix

        # Remove common messy prefixes/suffixes like Screen Shot 2026-..., Untitled, (1), etc.
        cleaned = stem
        cleaned = re.sub(r"^Screenshot[-_\s]*\d{4}[-_\d\s]*", "screenshot", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^IMG[-_\s]*\d+", "photo", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[\s_]+", "_", cleaned).strip("_-")

        # Standardize lowercase with underscores
        cleaned = re.sub(r"[^\w\-\.]", "", cleaned).lower()

        if not cleaned:
            cleaned = f"file_{int(time.time())}"

        return f"{cleaned}{ext}"
