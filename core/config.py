"""Configuration and Theme Tokens for LazyDesk AI."""
from pathlib import Path
from typing import Dict, Any

# Base storage paths
APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "lazydesk.db"

# Exact Design Tokens specified by Design Direction
THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "name": "Warm Paper",
        "app_bg": "#F3F0E8",
        "primary_surface": "#FAF8F2",
        "secondary_surface": "#E7E2D6",
        "primary_accent": "#496B50",
        "accent_hover": "#3C5942",
        "soft_accent_surface": "#E0E9DC",
        "main_text": "#252C25",
        "secondary_text": "#696D62",
        "borders": "#DCD7CA",
        "success": "#397653",
        "warning": "#A56B2B",
        "error": "#B44E45",
        "card_shadow": "0 1px 3px rgba(37, 44, 37, 0.05)",
        "badge_border": "rgba(73, 107, 80, 0.2)",
    },
    "dark": {
        "name": "Forest Graphite",
        "app_bg": "#18231F",
        "primary_surface": "#202C25",
        "secondary_surface": "#24322B",
        "primary_accent": "#A6C69A",
        "accent_hover": "#BCD7B0",
        "soft_accent_surface": "#304337",
        "main_text": "#E8E8DB",
        "secondary_text": "#AAB6AB",
        "borders": "#35443A",
        "success": "#91C9A0",
        "warning": "#E5B66E",
        "error": "#F09A90",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.3)",
        "badge_border": "rgba(166, 198, 154, 0.25)",
    }
}

# File categorization mapping
CATEGORY_MAP: Dict[str, list[str]] = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt", ".epub", ".pages"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".tsv", ".ods", ".numbers"],
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tiff", ".avif", ".ico"],
    "Code": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".json", ".yaml", ".yml", ".sh", ".sql", ".toml", ".xml"],
    "Audio & Video": [".mp3", ".wav", ".m4a", ".flac", ".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm", ".aac"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".xz", ".bz2", ".tgz"],
}

# Ollama local settings
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:8b"
FALLBACK_MODEL = "gemma:2b"
