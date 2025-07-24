"""
Constants and configuration defaults for codectx

This module centralizes all hardcoded values and configuration defaults
used throughout the application to improve maintainability and consistency.
"""

# API Configuration
DEFAULT_API_URL = "https://codestral.mistral.ai/v1/chat/completions"
DEFAULT_MODEL = "codestral-latest"
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRY_ATTEMPTS = 3

# Processing Configuration
DEFAULT_TOKEN_THRESHOLD = 200
DEFAULT_MAX_FILE_SIZE_MB = 10.0
DEFAULT_OUTPUT_FILE = "codectx.md"

# Mock Processing
MOCK_PROCESSING_DELAY = 0.5

# File Processing
CHUNK_SIZE = 4096

# UI Configuration
DEFAULT_TABLE_WIDTH = 50
PROCESSING_REFRESH_RATE = 4

# Ignore Patterns
DEFAULT_IGNORE_PATTERNS = {
    # Version control
    ".git/*", ".svn/*", ".hg/*", ".bzr/*",
    
    # Python
    "__pycache__/*", "*.pyc", "*.pyo", "*.pyd", ".Python",
    "build/*", "develop-eggs/*", "dist/*", "downloads/*", "eggs/*", ".eggs/*",
    "lib/*", "lib64/*", "parts/*", "sdist/*", "var/*", "wheels/*",
    "*.egg-info/*", ".installed.cfg", "*.egg", "MANIFEST",
    
    # Virtual environments
    "venv/*", "env/*", ".venv/*", ".env/*", "ENV/*", "env.bak/*", "venv.bak/*",
    
    # IDEs
    ".vscode/*", ".idea/*", "*.swp", "*.swo", "*~",
    ".DS_Store", "Thumbs.db",
    
    # Logs and databases
    "*.log", "*.sql", "*.sqlite", "*.db",
    
    # Compiled files
    "*.com", "*.class", "*.dll", "*.exe", "*.o", "*.so",
    
    # Archives
    "*.7z", "*.dmg", "*.gz", "*.iso", "*.jar", "*.rar", "*.tar", "*.zip",
    
    # Media files
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", "*.svg",
    "*.mp3", "*.mp4", "*.avi", "*.mov", "*.wmv", "*.flv",
    
    # Documentation (often auto-generated)
    "docs/_build/*", "site/*", ".mkdocs/*",
    
    # Node.js
    "node_modules/*", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
    
    # Java
    "target/*", "*.jar", "*.war", "*.ear",
    
    # C/C++
    "*.o", "*.so", "*.a", "*.lib", "*.dll",
    
    # Rust
    "target/*", "Cargo.lock",
    
    # Go
    "vendor/*", "*.exe",
    
    # Ruby
    ".bundle/*", "vendor/bundle/*", ".byebug_history",
    
    # OS generated
    ".DS_Store*", "ehthumbs.db", "Icon\r", "Thumbs.db",
    
    # Temporary files
    "*.tmp", "*.temp", "*.bak", "*.backup", "*.old",
    
    # Coverage reports
    "htmlcov/*", ".coverage", ".coverage.*", "coverage.xml", "*.cover",
    
    # Testing
    ".pytest_cache/*", ".tox/*", ".nox/*",
    
    # Jupyter
    ".ipynb_checkpoints/*",
    
    # Environment files
    ".env", ".env.local", ".env.*.local",
}

# AI Prompt Templates
AI_SYSTEM_PROMPT = """You are a code analysis expert. Your task is to analyze the provided code file and create a concise, structured summary.

Format your response EXACTLY as follows:
- **Role**: Brief description of what this file does
- **Classes**: List main classes (or "None")  
- **Global Functions**: List main functions (or "None")
- **Dependencies**: List main imports/dependencies (or "None")

Keep the summary concise and focused on the most important aspects."""

MOCK_SUMMARY_TEMPLATE = """- **Role**: This is a mocked summary of the file.
- **Classes**: None
- **Global Functions**: None
- **Dependencies**: None"""