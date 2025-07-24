# Release Notes - v3.0.0

## 🚀 Major Release: Package Modernization & Critical Bug Fixes

Version 3.0.0 represents a significant modernization of the codectx package, removing legacy installation methods and fixing critical bugs while maintaining all core functionality.

### 💥 BREAKING CHANGES

#### Removed Legacy Installation Files
- **Removed**: `setup.py` (legacy compatibility shim)
- **Removed**: `requirements.txt` (duplicate dependency specification)  
- **Removed**: `MANIFEST.in` (legacy file inclusion rules)
- **Removed**: `codectx.egg-info/` directory (generated setuptools files)

**Migration Guide**: 
- **Old**: `pip install -r requirements.txt` 
- **New**: `pip install -e .[dev]` (for development dependencies)
- All installations now use modern `pyproject.toml` specification only

### 🐛 Critical Bug Fixes

#### Fixed: Deleted File Summary Persistence (Major)
- **Issue**: When files were deleted from a project, their summaries remained indefinitely in `codectx.md`, making documentation inaccurate
- **Fix**: Modified `write_output` method to accept `current_files` parameter and filter out summaries for non-existent files
- **Impact**: Update mode now accurately reflects the current project state
- **Files Modified**: 
  - `codectx/processing.py:370` - Enhanced `write_output` method
  - `codectx/cli.py:332` - Updated to pass current files list

### ✨ Major Improvements

#### Code Organization & Refactoring
- **New**: Created centralized `codectx/constants.py` module (108 lines)
- **Refactored**: Eliminated hardcoded values throughout codebase
- **Enhanced**: Module documentation and docstrings
- **Improved**: Code maintainability and consistency

#### Centralized Configuration Constants
```python
# API Configuration
DEFAULT_API_URL = "https://codestral.mistral.ai/v1/chat/completions"
DEFAULT_MODEL = "codestral-latest"
DEFAULT_TIMEOUT = 30.0

# Processing Configuration  
DEFAULT_TOKEN_THRESHOLD = 200
DEFAULT_OUTPUT_FILE = "codectx.md"
```

### 🧪 Testing Enhancements

#### New Test Coverage
- **Added**: Test for file discovery after deletion
- **Added**: End-to-end test for deleted file summary removal  
- **Verified**: All 28 tests pass with new changes
- **Coverage**: Comprehensive integration testing for bug fixes

### 📚 Documentation Updates

#### Modern Installation Instructions
- **Updated**: README.md with PyPI installation as primary method
- **Updated**: CLAUDE.md development guide
- **Added**: Proper development dependency installation instructions
- **Removed**: References to legacy installation files

#### Updated Quick Start
```bash
# Install from PyPI (recommended)
pip install codectx

# Or install from source
git clone https://github.com/RMLaroche/codectx.git
cd codectx
pip install .
```

### 🔧 Technical Details

#### Package Structure Improvements
- **Modern**: 100% `pyproject.toml`-based packaging
- **Clean**: Removed all legacy setuptools compatibility
- **Streamlined**: Single source of truth for dependencies
- **Professional**: Industry-standard Python packaging

#### Compatibility & Requirements
- **Maintained**: Python 3.8+ support
- **Dependencies**: No changes to runtime dependencies
- **Development**: Added modern development tools (black, flake8, mypy)

### 📊 Statistics

- **Files Modified**: 7 core modules
- **Files Removed**: 4 legacy installation files  
- **Files Added**: 1 constants module
- **Tests Added**: 2 new integration tests
- **Total Tests**: 28 tests (all passing)
- **Test Coverage**: Unit, integration, and smoke testing

### 🔄 Migration Path

#### For End Users
- **No changes required** for existing API usage
- **Update installation commands** if using development setup
- **Benefit**: More accurate project summaries with deleted file handling

#### For Developers
- **Update**: Development environment setup commands
- **Use**: Modern `pip install -e .[dev]` for development dependencies
- **Reference**: Updated CLAUDE.md for development guidelines

### 🏷️ Version History Context

- **v2.2.0**: Previous stable release with comprehensive test suite
- **v3.0.0**: Major modernization and critical bug fixes (**this release**)

### 🔮 Future Roadmap

This modernization sets the foundation for:
- Enhanced configuration file support
- Improved export formats (JSON, YAML)  
- Advanced filtering and categorization features
- Integration with popular development tools

---

**Full Changelog**: https://github.com/RMLaroche/codectx/compare/v2.2.0...v3.0.0

**Installation**: `pip install codectx==3.0.0`

**GitHub Release**: [v3.0.0](https://github.com/RMLaroche/codectx/releases/tag/v3.0.0)