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
- ⚙️ **Multiple Config Sources**: YAML/JSON/TOML files, environment variables, CLI arguments
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

## ⚙️ Simple Global Configuration

codectx uses a **global user configuration** that applies to all your projects. Configuration priority:
1. **CLI arguments** (highest priority - for one-time overrides)
2. **Global config file** (`~/.config/codectx/config.yml`)  
3. **Environment variables** (backward compatibility)
4. **Default values** (fallback)

### Quick Setup

codectx automatically creates your global config file on first run. You can also:

```bash
# Create/initialize global config file
codectx --init-config

# Edit your global configuration  
codectx --edit-config

# View current configuration
codectx --show-config
```

### CLI Configuration Options

Override any setting via command-line:

```bash
# API Configuration
codectx --api-key "your-key" --api-url "https://api.example.com"
codectx --retry-attempts 5 --api-timeout 45.0

# Processing Configuration  
codectx --token-threshold 100 --max-file-size 20.0
codectx --concurrent-requests 10 --output-file "my-summary.md"

# LLM Configuration
codectx --llm-provider mistral --llm-model "codestral-latest"
codectx --log-level DEBUG

# Configuration management
codectx --edit-config     # Open global config in your editor
codectx --show-config     # Display current settings
```

### Environment Variables (Legacy Support)

Still supported for backward compatibility:
```bash
export CODECTX_API_KEY="your-api-key-here"
export CODECTX_API_URL="https://your-api-endpoint.com"
export CODECTX_API_RETRY_ATTEMPTS=5
export CODECTX_TOKEN_THRESHOLD=150
export CODECTX_LLM_MODEL="codestral-latest"
```

### Global Configuration File

Your global config file is located at `~/.config/codectx/config.yml` (or `~/.codectx.yml`):

```yaml
# codectx - Global Configuration File
# This file stores your personal preferences for codectx

# API Configuration (most important settings)
api_key: "your-api-key-here"  # REQUIRED for AI summarization
api_url: "https://codestral.mistral.ai/v1/chat/completions"
api_retry_attempts: 3
api_timeout: 30.0

# LLM Configuration  
llm_provider: "mistral"
llm_model: "codestral-latest"

# Processing Preferences
token_threshold: 200  # Files above this get AI-summarized
max_file_size_mb: 10.0  # Skip files larger than this
concurrent_requests: 5  # Parallel API requests

# Output Preferences
output_filename: "codectx.md"  # Default output filename
log_level: "INFO"
show_progress: true

# Global ignore patterns (in addition to project .codectxignore files)
ignore_patterns:
  - "__pycache__/*"
  - "*.pyc"
  - ".git/*"
  - "node_modules/*"

# Uncomment to use custom AI prompt:
# custom_system_prompt: |
#   Your custom prompt here...
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

### Smart Update Mode (Default)
```bash
# Only updates files that have changed - much faster!
codectx /path/to/project         

# First run: processes all files
# Subsequent runs: only processes modified files
```

### Interactive Mode
```bash
cd my-project
codectx  # Explore files with enhanced UI and dynamic menus
```

**Interactive features:**
- 📊 **Enhanced Tables**: Color-coded dates, emoji headers, status indicators
- 🎯 **Dynamic Menu**: Shows file counts, greys out "Update" when all files are current
- 📅 **Visual Status**: Red dates for outdated files, green for up-to-date
- ⚡ **Smart Defaults**: Automatically focuses on the most relevant action

### Processing Modes with Configuration
```bash
# Update mode (default - fastest)
codectx /path/to/project

# Scan all files (when you need to reprocess everything)  
codectx --scan-all /path/to/project

# Testing and development
codectx --mock-mode .           # Test without API calls
codectx --copy-mode .           # Raw content only (no AI)

# Advanced configuration examples (one-time overrides)
codectx --token-threshold 50 --retry-attempts 3 /path/to/project
codectx --output-file project-summary.md --llm-model "different-model" .
codectx --api-timeout 60.0 --log-level DEBUG .

# Force interactive mode
codectx --interactive /path/to/project
```

### Configuration Management Examples

```bash
# First time setup
codectx --init-config                    # Create global config file
codectx --edit-config                    # Open config in your editor
# (Edit your API key and preferences)
codectx .                               # Run with your global settings

# Check current configuration
codectx --show-config                   # Display all current settings

# One-time overrides (don't change your global config)
codectx --token-threshold 25 --concurrent-requests 8 /my/project
codectx --api-key "temp-key" --retry-attempts 1 --mock-mode .
codectx --output-file "special-analysis.md" /important/project
```

## 🔍 How It Works

### Simple Configuration System (New!)
1. **Global Config**: One config file in `~/.config/codectx/config.yml` for all projects
2. **Auto-Creation**: Automatically created on first run with sensible defaults
3. **Priority System**: CLI args → global config → env vars → defaults
4. **Easy Management**: `--edit-config` to modify, `--show-config` to view

### Smart Update Mode (Default)
1. **File Discovery**: Scans directory and identifies all processable files
2. **Timestamp Analysis**: Checks existing summary file for timestamps
3. **Smart Filtering**: Only processes files modified since their last summary
4. **Efficient Processing**: Dramatically faster on subsequent runs with retry logic
5. **Output**: Updates summary file with new timestamps and summaries

### Interactive Mode  
1. **Enhanced Discovery**: Shows color-coded table with file status indicators
2. **Dynamic Menu**: Displays file counts and smart options based on current state
3. **Visual Feedback**: Red dates for outdated files, green for up-to-date
4. **User Selection**: Choose between update, scan all, mock, or copy modes
5. **Live Processing**: Real-time table updates showing progress
6. **Smart Completion**: Returns to menu with refreshed status

### File Processing Logic (Configurable!)
- **Configurable Token Threshold**: Default 200 tokens, customize via `--token-threshold`
- **Below Threshold**: Files copied as raw content (small files)
- **Above Threshold**: Sent to AI for intelligent summarization with retry logic
- **API Resilience**: Automatic retry with exponential backoff on failures
- **Custom Prompts**: Use your own AI prompts for specialized summarization
- **File Size Limits**: Skip files above configured size limit (default 10MB)

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

## ⚡ Performance & Reliability Benefits

### Smart Update Mode Performance
- **First run**: Processes all files (same as before)
- **Subsequent runs**: Only processes changed files (often 90%+ faster)
- **Large projects**: Massive time savings on iterative development
- **Visual feedback**: Instantly see which files need attention

### Enhanced Reliability (New!)
- **API Retry Logic**: Automatically retries failed API calls with exponential backoff
- **Configurable Timeouts**: Adjust timeout values for different network conditions
- **Error Recovery**: Graceful handling of temporary network issues
- **File Size Protection**: Skip oversized files to prevent processing issues
- **Concurrent Processing**: Configurable parallel requests for faster processing

**Example**: A 100-file project might have only 2-3 changed files, processing in seconds instead of minutes. With retry logic, temporary network issues won't stop your analysis.

## 🛠️ Development

### Local Installation

```bash
git clone https://github.com/RMLaroche/codectx.git
cd codectx
pip install -e .
```

### Running Tests

```bash
# Mock mode for testing
codectx --mock-mode

# Test configuration features
codectx --generate-config yaml
codectx --token-threshold 10 --mock-mode .

# Test on sample directory
mkdir test_dir
echo "print('hello')" > test_dir/test.py
codectx test_dir --mock-mode
```

### Configuration Testing

```bash
# Setup and test global configuration
codectx --init-config           # Create config if needed
codectx --show-config          # Verify your settings
codectx --mock-mode .          # Test with your global config

# Test CLI overrides
codectx --token-threshold 1 --retry-attempts 1 --mock-mode test_dir
```

## 🔒 Privacy & Security

- codectx sends file contents to your configured AI API for summarization
- No data is stored permanently by codectx itself
- **File Size Limits**: Configurable max file size to prevent accidental large file processing
- **Ignore Patterns**: Multiple ways to exclude sensitive files (`.codectxignore`, config files)
- **Mock Mode**: Use `--mock-mode` for testing without any API calls
- **Local Configuration**: All settings stored locally, no telemetry or tracking
- **API Key Security**: Support for environment variables and secure config files

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