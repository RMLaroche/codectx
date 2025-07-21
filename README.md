# codectx

[![Development](https://img.shields.io/badge/status-development-orange.svg)](https://github.com/RMLaroche/codectx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**codectx** is an AI-powered code context and file summarization tool designed for developers who want to quickly understand codebases. It processes directories of files and generates structured summaries using AI, helping you grasp project architecture and individual file purposes without reading through every line of code.

## ✨ Features

- 🔄 **Smart Update Mode**: Only processes files that have changed since last summary (default behavior)
- 🤖 **AI-Powered Summarization**: Intelligent analysis of code files with structured output
- 📊 **Enhanced Tables**: Color-coded status indicators with emoji headers and real-time updates
- 🎯 **Dynamic Interactive Menu**: Shows file counts, greys out options when not needed
- 📅 **Timestamp Tracking**: Tracks when each file was last summarized with visual indicators
- 📁 **Smart File Processing**: Automatically handles different file types and encodings
- 🎯 **Ignore Patterns**: Configurable `.codectxignore` file with sensible defaults
- 📊 **Real-time Progress**: Beautiful console interface with live progress tracking
- 🔧 **Multiple Modes**: Update (default), scan all, mock (testing), and copy (raw content) modes
- 📝 **Structured Output**: Organized markdown summaries with timestamps and file metadata
- 🚀 **Easy Installation**: Install from source (PyPI coming soon)

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
- An AI API key (set as environment variable)

## 🔧 Configuration

### API Setup

codectx requires an AI API for summarization. Set your API key as an environment variable:

```bash
export CODECTX_API_KEY="your-api-key-here"
```

Optionally, configure a custom API endpoint:

```bash
export CODECTX_API_URL="https://your-api-endpoint.com"
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

### Processing Modes
```bash
# Update mode (default - fastest)
codectx /path/to/project

# Scan all files (when you need to reprocess everything)  
codectx --scan-all /path/to/project

# Testing and development
codectx --mock-mode .           # Test without API calls
codectx --copy-mode .           # Raw content only (no AI)

# Force interactive mode
codectx --interactive /path/to/project
```

### Custom Output Location
The tool automatically creates `codectx.md` in the current directory with all summaries.

## 🔍 How It Works

### Smart Update Mode (Default)
1. **File Discovery**: Scans directory and identifies all processable files
2. **Timestamp Analysis**: Checks existing `codectx.md` for file summary timestamps
3. **Smart Filtering**: Only processes files modified since their last summary
4. **Efficient Processing**: Dramatically faster on subsequent runs
5. **Output**: Updates `codectx.md` with new timestamps and summaries

### Interactive Mode  
1. **Enhanced Discovery**: Shows color-coded table with file status indicators
2. **Dynamic Menu**: Displays file counts and smart options based on current state
3. **Visual Feedback**: Red dates for outdated files, green for up-to-date
4. **User Selection**: Choose between update, scan all, mock, or copy modes
5. **Live Processing**: Real-time table updates showing progress
6. **Smart Completion**: Returns to menu with refreshed status

### File Processing Logic
- **Files < 200 estimated tokens**: Copied as raw content (small files)
- **Files ≥ 200 estimated tokens**: Sent to AI for intelligent summarization
- **Modified files**: Marked with red timestamps until re-summarized
- **Current files**: Shown with green timestamps and "Up to date" status

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

## ⚡ Performance Benefits

**Smart Update Mode dramatically improves performance:**

- **First run**: Processes all files (same as before)
- **Subsequent runs**: Only processes changed files (often 90%+ faster)
- **Large projects**: Massive time savings on iterative development
- **Visual feedback**: Instantly see which files need attention

**Example**: A 100-file project might have only 2-3 changed files, processing in seconds instead of minutes.

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

# Test on sample directory
mkdir test_dir
echo "print('hello')" > test_dir/test.py
codectx test_dir --mock-mode
```

## 🔒 Privacy & Security

- codectx sends file contents to the configured AI API for summarization
- No data is stored permanently by codectx itself
- Use `--mock-mode` for testing without API calls
- Review `.codectxignore` patterns to exclude sensitive files

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