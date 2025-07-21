# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**codectx** is a Python package that provides AI-powered code context and file summarization for codebases. It's designed as a professional, pip-installable tool that developers can use to quickly understand project structure and file purposes.

## Common Commands

### Development Installation
```bash
# Install in development mode
pip install -e .

# Install dependencies only
pip install -r requirements.txt
```

### Running the Application
```bash
# After installation, use the CLI command
codectx

# Process specific directory
codectx /path/to/directory

# Mock mode (for testing without API calls)
codectx --mock-mode

# Copy mode (raw content without summarization)
codectx --copy-mode

# Show help
codectx --help
```

### Building and Distribution
```bash
# Build package
python -m build

# Install locally from build
pip install dist/codectx-*.whl
```

### Configuration
Configuration is done via environment variables:
- Set `CODECTX_API_KEY` environment variable with your AI API key
- Optionally set `CODECTX_API_URL` for custom API endpoints
- The tool uses the "codestral-latest" model by default

## Architecture and Key Components

### Core Workflow
1. **Directory Walking** (`cli.py`): Traverses directory structure, respecting ignore patterns
2. **File Processing** (`file_processor.py`): Reads file content and estimates token counts (rough estimation)
3. **AI Summarization** (`api_client.py`): Sends files to AI API for structured summaries
4. **Output Generation** (`file_writer.py`): Writes all summaries to `codectx.md`

### Package Structure

```
codectx/
├── __init__.py          # Package initialization and version info
├── cli.py              # Main CLI entry point and argument parsing
├── api_client.py       # AI API communication with error handling
├── config.py           # Configuration management via environment variables
├── file_processor.py   # File reading with encoding detection
├── ignore_handler.py   # .codectxignore processing with smart defaults
├── file_writer.py      # Output generation to codectx.md
├── progress_display.py # Rich console interface
└── utils.py           # Utility functions (timestamps, etc.)
```

### Key Modules

- **`cli.py`**: Main entry point with professional CLI interface and error handling
- **`api_client.py`**: Robust API communication with timeout handling and error recovery
- **`config.py`**: Environment-based configuration with sensible defaults
- **`ignore_handler.py`**: Smart file filtering with built-in patterns for common dev files
- **`file_processor.py`**: Enhanced file reading with encoding detection and binary file handling
- **`file_writer.py`**: Structured output generation with metadata headers
- **`progress_display.py`**: Improved Rich console interface with better formatting

### File Ignore System
The tool respects a `.codectxignore` file in the target directory using glob patterns:
```
logs/*
__pycache__/*
*.tmp
```

### AI Summarization Logic
- Files with <200 estimated tokens: copied as raw content
- Files with ≥200 estimated tokens: sent to AI for structured summary
- Token estimation: rough approximation (characters ÷ 4)
- Mock mode: simulates API calls with fake summaries for testing
- Copy mode: forces raw content output for all files

### Output Format
All summaries are written to `codectx.md` with structured markdown including:
- File path and processing type (SUMMARIZED/RAW CONTENT)
- Role/purpose description
- Classes and methods (for summarized files)
- Dependencies and imports

## Dependencies

- **requests**: HTTP client for AI API calls
- **rich**: Console formatting and progress display
- **InquirerPy**: Interactive prompts (imported but not actively used in current codebase)

## Development Notes

### Package Installation and Distribution
- Built with modern `pyproject.toml` configuration
- Console script entry point: `codectx = "codectx.cli:main"`
- Supports Python 3.8+ with type hints throughout
- Uses environment variables for configuration (no hardcoded API keys)

### Code Quality Features
- Comprehensive error handling and validation
- Proper encoding detection for file reading
- Timeout handling for API requests
- Type hints and docstrings throughout
- Rich console interface with real-time progress

### Testing and Development
- Mock mode for testing without API calls
- Copy mode for processing without summarization
- Extensive default ignore patterns for common dev environments
- Professional CLI with help text and examples

### Architecture Improvements
- Modular package structure with clear separation of concerns
- Environment-based configuration management
- Enhanced file processing with binary detection
- Structured output with metadata headers
- Better error messages and user feedback