# codectx

AI-powered code summarization tool that generates markdown documentation from your codebase.

## Quick Start

```bash
# Install from PyPI (recommended)
pip install codectx

# Or install from source
git clone https://github.com/RMLaroche/codectx.git
cd codectx
pip install .

# Set API key
export CODECTX_API_KEY="your-mistral-api-key"

# Run on current directory
codectx
```

## Usage

```bash
codectx                    # Update changed files only (default)
codectx --scan-all         # Process all files
codectx --mock-mode        # Test without API calls  
codectx --copy-mode        # Copy content without AI
codectx --status           # Show file status
```

## How it works

1. Scans your directory for code files
2. Only processes files that changed since last run (checksum-based)
3. Small files (<200 tokens) → copied as-is
4. Large files (≥200 tokens) → AI summarized
5. Generates `codectx.md` with structured summaries

## Configuration

### API Key (Required)
```bash
export CODECTX_API_KEY="your-mistral-api-key"
```

### Ignore Files
Create `.codectxignore`:
```
node_modules/
*.log
build/
```

### CLI Options
```bash
codectx [directory]                # Process directory (default: current directory)
codectx --help                     # Show all options
codectx --version                  # Show version

# Processing modes  
codectx --scan-all                 # Process all files (not just changed)
codectx --mock-mode                # Test without API calls
codectx --copy-mode                # Raw content only (no AI)
codectx --status                   # Show file status without processing

# Configuration
codectx --api-key KEY              # Override API key
codectx --token-threshold 100      # Files ≥N tokens get AI summary (default: 200)
codectx --timeout 60               # API timeout seconds (default: 30)
codectx --retry-attempts 5         # API retry count (default: 3)
codectx --max-file-size 20         # Skip files >N MB (default: 10)
codectx --output-file summary.md   # Output filename (default: codectx.md)

# API settings
codectx --api-url URL              # Custom API endpoint
codectx --model mistral-7b         # AI model (default: codestral-latest)
```

### Environment Variables
```bash
export CODECTX_API_KEY="your-key"           # Required for AI mode
export CODECTX_API_URL="custom-endpoint"    # Override API URL  
export CODECTX_MODEL="custom-model"         # Override AI model
```

**Note**: CLI arguments always override environment variables.

## Output

Creates `codectx.md` with:

```markdown
## src/main.py

Summarized on 2024-01-15 14:30:22 (checksum: abc123...)

- **Role**: Main application entry point
- **Classes**: App, Config
- **Functions**: main(), setup()
- **Dependencies**: requests, click
```

## Requirements

- Python 3.8+
- Mistral API key (free tier available)

## License

MIT License