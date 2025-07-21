# codectx

[![Development](https://img.shields.io/badge/status-development-orange.svg)](https://github.com/RMLaroche/codectx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**codectx** is an AI-powered code context and file summarization tool designed for developers who want to quickly understand codebases. It processes directories of files and generates structured summaries using AI, helping you grasp project architecture and individual file purposes without reading through every line of code.

## ✨ Features

### Core Functionality
- 🔄 **Smart Update Mode**: Only processes files that have changed since last summary (default behavior)
- 🤖 **AI-Powered Summarization**: Intelligent analysis of code files with structured output
- 📊 **Enhanced Tables**: Color-coded status indicators with emoji headers and real-time updates
- 🎯 **Dynamic Interactive Menu**: Shows file counts, greys out options when not needed
- 📅 **Timestamp Tracking**: Tracks when each file was last summarized with visual indicators

### Advanced Configuration System
- ⚙️ **Multiple Config Sources**: Global YAML file, environment variables, CLI arguments
- 🔄 **API Retry Logic**: Configurable retry attempts (default: 3) with exponential backoff
- 🤖 **Flexible LLM Support**: Extensible for multiple AI providers (Mistral, future: Claude, OpenAI, local models)
- 📝 **Custom System Prompts**: Personalize AI summarization behavior
- 📊 **Configurable Thresholds**: Adjust token limits, file sizes, and processing behavior
- 🎛️ **Rich CLI Options**: Override any setting via command-line arguments

### File Processing
- 📁 **Smart File Processing**: Automatically handles different file types and encodings
- 🎯 **Ignore Patterns**: Configurable `.codectxignore` file with sensible defaults
- 📊 **Real-time Progress**: Beautiful console interface with live progress tracking
- 🔧 **Multiple Modes**: Update (default), scan all, mock (testing), and copy (raw content) modes
- 📝 **Structured Output**: Organized markdown summaries with timestamps and file metadata

## 🚀 Quick Start

### Installation

> **Note**: codectx is currently in development and not yet published to PyPI.

**For now, install from source:**

```bash
git clone https://github.com/RMLaroche/codectx.git
cd codectx
pip install -e .
```

**Coming soon to PyPI:**
```bash
pip install codectx  # Not yet available
```

### Basic Usage

```bash
# Interactive mode - explore files and choose options
codectx

# Update changed files only (default, fastest)
codectx /path/to/your/project

# Process all files (override update mode)
codectx --scan-all /path/to/your/project

# Test without API calls
codectx --mock-mode

# Copy files without summarization
codectx --copy-mode
```

## 📋 Prerequisites

- Python 3.8 or higher
- An AI API key (see configuration section)
- PyYAML (automatically installed)

## ⚙️ Configuration

**Simple global config**: One file (`~/.config/codectx/config.yml`) for all projects.

**Priority**: CLI arguments > Environment variables > Config file > Defaults

### Quick Setup

```bash
codectx --init-config    # Create config file  
codectx --edit-config    # Edit your settings
codectx --show-config    # View current settings
```

### Configuration File

Located at `~/.config/codectx/config.yml` (auto-created on first run):

```yaml
# API Configuration (REQUIRED)
api_key: "your-api-key-here"
api_url: "https://codestral.mistral.ai/v1/chat/completions" 
api_retry_attempts: 3
api_timeout: 30.0

# Processing Preferences  
token_threshold: 200      # Files above this get AI-summarized
max_file_size_mb: 10.0   # Skip files larger than this
concurrent_requests: 5    # Parallel API requests
log_level: "INFO"
```

### Environment Variables

```bash
export CODECTX_API_KEY="your-api-key-here"
export CODECTX_TOKEN_THRESHOLD=150
export CODECTX_API_RETRY_ATTEMPTS=5
```

### CLI Overrides

```bash
codectx --token-threshold 50 --retry-attempts 5 /path/to/project
codectx --output-file "project-summary.md" .
```

### Ignore Patterns

Create a `.codectxignore` file in your project root to specify files and patterns to ignore:

```gitignore
# Dependencies
node_modules/
venv/
__pycache__/

# Build artifacts
dist/
build/
*.pyc

# IDE files
.vscode/
.idea/

# Custom patterns
logs/
*.tmp
```

codectx includes sensible defaults for common files (`.git/`, `node_modules/`, `__pycache__/`, etc.), so you only need to specify project-specific patterns.

## 📖 Usage Examples

```bash
# Interactive mode (auto-creates config on first run)
codectx

# Update changed files only (default, fastest)  
codectx /path/to/project

# Process all files
codectx --scan-all /path/to/project  

# Test without API calls
codectx --mock-mode .

# Configuration management
codectx --edit-config           # Edit global settings
codectx --show-config           # View current settings

# One-time overrides
codectx --token-threshold 50 --output-file "summary.md" .
```

## 🔍 How It Works

1. **File Discovery**: Scans directory, respecting ignore patterns
2. **Smart Update**: Only processes files changed since last summary (timestamps)
3. **Token Analysis**: Files < 200 tokens → raw content, ≥200 tokens → AI summary
4. **API Retry**: Automatic retry with exponential backoff on failures
5. **Output**: Generates `codectx.md` with structured summaries and timestamps

## 📊 Output Format

codectx generates a `codectx.md` file with timestamps:

```markdown
# Project Summary

Generated by codectx on 2024-01-15 14:30:22

Total files processed: 15

---

## src/main.py

Summarized on 2024-01-15 14:30:22

- **Role**: Main application entry point handling CLI arguments and orchestration
- **Classes**: None
- **Global Functions**:
  - main(args): Initializes application and processes command line arguments
  - setup_logging(): Configures application logging
- **Dependencies**: config, utils, processor

## config.py

Summarized on 2024-01-15 14:29:45

[Full file content for smaller files]
```

### New Timestamp Features
- **Precise tracking**: Each file shows exactly when it was last summarized
- **Smart updates**: Only files modified after their summary date are reprocessed
- **Visual indicators**: UI shows file status with color-coded timestamps

## ⚡ Performance & Reliability

- **Smart Updates**: Only processes changed files (often 90%+ faster on subsequent runs)
- **API Retry Logic**: Automatic retry with exponential backoff on failures  
- **Concurrent Processing**: Configurable parallel requests for speed
- **File Size Protection**: Skip oversized files automatically

**Example**: 100-file project with 2-3 changes processes in seconds, not minutes.

## 🛠️ Development

```bash
# Install from source
git clone https://github.com/RMLaroche/codectx.git
cd codectx
pip install -e .

# Test
codectx --init-config          # Setup config  
codectx --mock-mode .          # Test without API calls
```

## 🔒 Privacy & Security

- File contents sent to your configured AI API for summarization
- No data stored permanently by codectx
- Use `.codectxignore` and file size limits to exclude sensitive files  
- Use `--mock-mode` for testing without API calls
- All settings stored locally, no telemetry

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📋 [Report issues](https://github.com/RMLaroche/codectx/issues)
- 💬 [Discussions](https://github.com/RMLaroche/codectx/discussions)
- 📖 [Documentation](https://github.com/RMLaroche/codectx/wiki)

---

Made with ❤️ for developers who love clean, documented code.