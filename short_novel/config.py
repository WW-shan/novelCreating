"""
Short Novel Generator - Configuration
"""
import os
from pathlib import Path

# API Configuration
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-opus-4-6"
MAX_TOKENS_PER_CHAPTER = 4096
MAX_TOKENS_ANALYSIS = 8192

# Directory paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STORIES_DIR = BASE_DIR / "stories"
SOURCES_DIR = BASE_DIR / "sources"
PROMPTS_DIR = BASE_DIR / "core" / "prompts"

# Generation settings
DEFAULT_CHAPTERS = 10
MIN_WORDS_PER_CHAPTER = 1200
MAX_WORDS_PER_CHAPTER = 2000

# Ensure directories exist
TEMPLATES_DIR.mkdir(exist_ok=True)
STORIES_DIR.mkdir(exist_ok=True)
SOURCES_DIR.mkdir(exist_ok=True)
