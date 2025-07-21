# Development Workflow

## Version Management

### Semantic Versioning
- **Major** (2.0.0): Breaking changes
- **Minor** (1.1.0): New features, backward compatible  
- **Patch** (1.0.1): Bug fixes, backward compatible

### Development Cycle

#### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Develop and test
codectx --mock-mode  # Test locally
# Make changes...

# Commit changes
git add .
git commit -m "Add new feature: description"
```

#### 2. Version Bumping
Update version in TWO places:
- `pyproject.toml`: `version = "1.1.0"`
- `codectx/__init__.py`: `__version__ = "1.1.0"`

#### 3. Testing Before Release
```bash
# Test installation locally
pip install -e . --force-reinstall
codectx --version  # Should show new version
codectx --mock-mode  # Test functionality

# Test building
python -m build
```

#### 4. Release Process
```bash
# Merge to main
git checkout main
git merge feature/new-feature-name

# Tag release
git tag v1.1.0
git push origin main --tags

# Publish to PyPI
rm -rf dist/ build/ *.egg-info/  # Clean old builds
python -m build
python -m twine upload dist/*
```

## Branch Strategy

### Recommended Approach
```
main
├── feature/ai-model-selection     # New feature branches
├── feature/config-file-support
├── feature/export-formats
└── hotfix/api-timeout-fix         # Bug fixes
```

### Development Commands
```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Regular development
# ... make changes ...
git add .
git commit -m "Implement feature component"

# Ready for release
git checkout main
git merge feature/your-feature-name
# Update versions in both files
git add .
git commit -m "Bump version to 1.1.0"
git tag v1.1.0
git push origin main --tags

# Publish
python -m build && python -m twine upload dist/*
```

## Testing Strategy

### Before Each Release
1. **Local Testing**:
   ```bash
   codectx --mock-mode
   codectx test_project --mock-mode
   ```

2. **Installation Testing**:
   ```bash
   pip install -e . --force-reinstall
   codectx --version
   ```

3. **TestPyPI Testing**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   pip install --index-url https://test.pypi.org/simple/ codectx
   ```

## Feature Ideas for Future Releases

### v1.1.0 - Enhanced Configuration
- [ ] Config file support (`.codectx.yml`)
- [ ] Multiple AI model support
- [ ] Custom output templates

### v1.2.0 - Export Formats  
- [ ] JSON export
- [ ] HTML report generation
- [ ] Integration with documentation tools

### v1.3.0 - Advanced Features
- [ ] Watch mode for live updates
- [ ] Git integration (analyze changed files)
- [ ] Team collaboration features

### v2.0.0 - Major Improvements
- [ ] Plugin system
- [ ] Web interface
- [ ] Database storage options

## Automation Ideas

### GitLab CI/CD Pipeline
Create `.github/workflows/ci.yml`:
```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pip install -e .
    - codectx --version
    - codectx . --mock-mode

build:
  stage: build
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  script:
    - pip install twine
    - python -m twine upload dist/*
  only:
    - tags
  when: manual
```

## Release Checklist

Before each release:
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `codectx/__init__.py`
- [ ] Test locally with `--mock-mode`
- [ ] Test installation with `pip install -e .`
- [ ] Update CHANGELOG.md (if you create one)
- [ ] Test on TestPyPI
- [ ] Create git tag
- [ ] Publish to PyPI
- [ ] Verify installation: `pip install codectx`