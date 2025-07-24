# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**codectx** is a Python package that provides AI-powered code context and file summarization for codebases. It's designed as a professional, pip-installable tool that developers can use to quickly understand project structure and file purposes.

## Common Commands

### Development Installation
```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]
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

### Testing
```bash
# Run all tests (26 tests total)
pytest tests/

# Run specific test categories
pytest tests/unit/          # Unit tests (18 tests)
pytest tests/integration/   # Integration tests (2 tests)

# Run tests with coverage report
make test-coverage

# Run tests using Makefile shortcuts
make test                   # All tests
make test-unit             # Unit tests only
```

### Configuration
Configuration is done via environment variables:
- Set `CODECTX_API_KEY` environment variable with your AI API key
- Optionally set `CODECTX_API_URL` for custom API endpoints
- Optionally set `CODECTX_MODEL` for custom model selection
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
- **PyYAML**: YAML configuration file parsing
- **pytest**: Testing framework (development dependency)

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
- **Comprehensive test suite**: 26 tests covering unit, integration, and smoke testing
- **pytest framework**: Configured with proper markers and CI/CD integration
- **Mock mode** for testing without API calls
- **Copy mode** for processing without summarization
- Extensive default ignore patterns for common dev environments
- Professional CLI with help text and examples

### Architecture Improvements
- Modular package structure with clear separation of concerns
- Environment-based configuration management
- Enhanced file processing with binary detection
- Structured output with metadata headers
- Better error messages and user feedback

## Testing Infrastructure

### Test Suite Overview
The project includes a comprehensive test suite with **26 tests** providing excellent coverage:

- **Unit Tests (18 tests)**: Cover individual modules and functions
  - `test_discovery.py`: File discovery, ignore patterns, checksum calculation
  - `test_smoke.py`: Basic import validation and functionality checks
- **Integration Tests (2 tests)**: End-to-end functionality testing
  - `test_basic.py`: CLI testing with mock mode and status mode

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures for all tests
├── unit/
│   ├── test_discovery.py    # 18 tests for discovery module
│   └── test_smoke.py        # 6 basic functionality tests
└── integration/
    └── test_basic.py        # 2 end-to-end tests
```

### Running Tests
```bash
# All tests (recommended)
pytest tests/ -v

# By category
pytest tests/unit/ -v        # Unit tests only
pytest tests/integration/ -v # Integration tests only

# With coverage
make test-coverage
coverage run -m pytest tests/
coverage report -m

# Specific test
pytest tests/unit/test_discovery.py::TestFileInfo::test_file_info_creation -v
```

### Test Features
- **Fast execution**: All 26 tests run in ~0.6 seconds
- **No external dependencies**: Uses mock mode to avoid API calls
- **Isolated testing**: Each test uses temporary directories
- **Shared fixtures**: Consistent test data via `conftest.py`
- **CI/CD ready**: GitHub Actions workflow configured

### Test Coverage Areas
✅ File discovery and directory traversal  
✅ `.codectxignore` pattern matching and filtering  
✅ FileInfo class with SHA256 checksum calculation  
✅ Binary file handling and size formatting  
✅ Error handling for missing/unreadable files  
✅ Mock mode end-to-end CLI testing  
✅ Status mode integration testing  
✅ Module imports and basic functionality

### Adding New Tests
1. **Unit tests**: Add to appropriate file in `tests/unit/`
2. **Integration tests**: Add to `tests/integration/`
3. **Fixtures**: Add shared test data to `tests/conftest.py`
4. **Run tests**: `pytest tests/ -v` to verify

### Test Configuration Files
- `pytest.ini`: Pytest configuration and markers
- `.github/workflows/tests.yml`: CI/CD pipeline
- `Makefile`: Convenient test commands
- `tests/README.md`: Detailed test documentation

## Git Workflow and Development Guidelines

### Branch Strategy (GitFlow)

This project follows **GitFlow** branching model:

#### Main Branches
- **`main`**: Production-ready code, tagged releases only
- **`develop`**: Integration branch for features, always deployable

#### Supporting Branches
- **`feature/*`**: New features (branch from `develop`, merge to `develop`)
- **`release/*`**: Preparation of new releases (branch from `develop`, merge to `main` and `develop`)
- **`hotfix/*`**: Critical fixes for production (branch from `main`, merge to `main` and `develop`)

### Development Workflow

#### 1. Starting a New Feature
```bash
# Always start from latest develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Examples:
# feature/config-file-support
# feature/json-export
# feature/improved-ui
```

#### 2. Feature Development
```bash
# Regular development cycle
git add .
git commit -m "feat: implement feature component"

# Push feature branch for backup/collaboration
git push -u origin feature/your-feature-name
```

#### 3. Completing a Feature
```bash
# Switch to develop and update
git checkout develop
git pull origin develop

# Merge feature (use --no-ff to preserve branch history)
git merge --no-ff feature/your-feature-name

# Clean up
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name

# Push updated develop
git push origin develop
```

#### 4. Creating a Release
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/1.1.0

# Update version numbers in:
# - pyproject.toml: version = "1.1.0"
# - codectx/__init__.py: __version__ = "1.1.0"

git add .
git commit -m "chore: bump version to 1.1.0"

# Test the release
pip install -e . --force-reinstall
codectx --version
codectx --mock-mode

# Merge to main
git checkout main
git merge --no-ff release/1.1.0

# Tag the release
git tag -a v1.1.0 -m "Release version 1.1.0"

# Merge back to develop
git checkout develop
git merge --no-ff release/1.1.0

# Clean up
git branch -d release/1.1.0

# Push everything
git push origin main develop --tags
```

#### 5. Hotfix Process
```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# Fix the issue and update version (patch)
# Update version to 1.0.1 in both files

git add .
git commit -m "fix: resolve critical bug"

# Merge to main
git checkout main
git merge --no-ff hotfix/critical-bug-fix
git tag -a v1.0.1 -m "Hotfix version 1.0.1"

# Merge to develop
git checkout develop
git merge --no-ff hotfix/critical-bug-fix

# Clean up
git branch -d hotfix/critical-bug-fix
git push origin main develop --tags
```

### Commit Message Guidelines

Use **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Types:
- **feat**: New feature
- **fix**: Bug fix  
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (build, dependencies, etc.)

#### Examples:
```bash
git commit -m "feat(cli): enhance update mode performance"
git commit -m "fix(api): handle timeout errors gracefully"
git commit -m "docs: update installation instructions"
git commit -m "chore: bump version to 1.1.0"
```

### Code Quality Standards

#### Before Each Commit
```bash
# Run test suite (preferred method)
pytest tests/ -v

# Test locally (manual testing)
codectx --mock-mode
codectx . --mock-mode

# Test installation
pip install -e . --force-reinstall
codectx --version
```

#### Before Each Release
```bash
# Run full test suite
pytest tests/ -v
make test-coverage

# Full testing
python -m build
pip install dist/codectx-*.whl --force-reinstall
codectx --help
codectx . --mock-mode
```

### GitHub Integration

#### Pull Request Process
- Create PR from `feature/*` to `develop`
- Include clear description of changes
- Reference any related issues
- Ensure CI passes (when implemented)

#### Release Process
```bash
# After merging release branch to main
gh release create v1.1.0 --title "v1.1.0 - Feature Release" --generate-notes
```

### Branch Protection (Recommended Settings)

Configure GitHub branch protection for `main` and `develop`:

#### Main Branch Protection
- Require pull request reviews (1+ reviewers)
- Require status checks to pass
- Require linear history
- Do not allow force pushes
- Restrict pushes to specific users/teams

#### Develop Branch Protection  
- Require pull request reviews (1+ reviewers)
- Require status checks to pass
- Allow merge commits (for GitFlow)

### Quick Reference Commands

```bash
# Start new feature
git checkout develop && git pull origin develop
git checkout -b feature/my-feature

# Finish feature
git checkout develop && git pull origin develop  
git merge --no-ff feature/my-feature
git push origin develop
git branch -d feature/my-feature

# Create release
git checkout -b release/1.1.0
# ... update versions ...
git checkout main && git merge --no-ff release/1.1.0
git tag v1.1.0 && git checkout develop
git merge --no-ff release/1.1.0
git push origin main develop --tags

# Emergency hotfix
git checkout main && git checkout -b hotfix/fix-name
# ... make fix, update patch version ...
git checkout main && git merge --no-ff hotfix/fix-name  
git tag v1.0.1 && git checkout develop
git merge --no-ff hotfix/fix-name
git push origin main develop --tags
```

### Development Environment Setup

When working on this project, Claude should:
1. Always create feature branches from `develop`
2. Use conventional commit messages  
3. Test changes with `--mock-mode` before committing
4. Update both version files when bumping versions
5. Follow the merge strategy (no fast-forward for feature merges)
6. Create GitHub releases with proper release notes