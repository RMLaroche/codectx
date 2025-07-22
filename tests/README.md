# Test Suite for codectx

This directory contains a comprehensive test suite for the codectx tool.

## Structure

```
tests/
├── README.md           # This file
├── conftest.py         # Shared fixtures for all tests
├── unit/               # Unit tests for individual modules
│   ├── test_discovery.py  # Tests for file discovery functionality
│   └── test_smoke.py       # Basic smoke tests to verify imports work
└── integration/        # Integration tests
    └── test_basic.py       # Basic end-to-end functionality tests
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### With Coverage
```bash
make test-coverage
```

### Specific Test
```bash
pytest tests/unit/test_discovery.py::TestFileInfo::test_file_info_creation -v
```

## Test Categories

### Unit Tests

#### Discovery Tests (`test_discovery.py`)
- **FileInfo Tests**: Test file information extraction, checksum calculation, size formatting
- **Ignore Patterns Tests**: Test `.codectxignore` file parsing and pattern matching
- **File Discovery Tests**: Test directory traversal, filtering, and file collection

#### Smoke Tests (`test_smoke.py`)
- Basic import verification
- Module availability checks
- Simple functionality validation

### Integration Tests

#### Basic Integration (`test_basic.py`)
- End-to-end CLI testing in mock mode
- Status mode integration
- Output file generation verification

## Test Fixtures

All tests use shared fixtures from `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_files`: Pre-created sample files for testing
- `sample_ignore_file`: Sample `.codectxignore` for testing
- `mock_config`, `ai_config`, `copy_config`: Processing configurations
- `existing_codectx_md`: Existing output file for update testing
- `mock_api_response`: Mock AI API response
- `env_vars`: Environment variable management

## Configuration

Tests are configured via:
- `pytest.ini`: Pytest configuration and markers
- `.github/workflows/tests.yml`: CI/CD pipeline
- `Makefile`: Convenient test running commands

## Coverage

The test suite covers:
- ✅ File discovery and ignore pattern handling
- ✅ Basic module imports and smoke tests  
- ✅ Integration testing with mock mode
- ✅ Error handling and edge cases

## Adding New Tests

1. **Unit Tests**: Add to appropriate module in `tests/unit/`
2. **Integration Tests**: Add to `tests/integration/`
3. **Fixtures**: Add shared test data to `tests/conftest.py`
4. **Markers**: Use `@pytest.mark.unit` or `@pytest.mark.integration`

## Test Development Notes

- Tests use the actual codectx architecture (function-based, not class-based)
- Mock mode is used for API-dependent tests to avoid external dependencies
- Temporary directories ensure test isolation
- All tests should be fast and deterministic