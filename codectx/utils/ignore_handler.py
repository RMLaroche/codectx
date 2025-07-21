"""
File ignore pattern handling
"""
import os
import fnmatch
from typing import List

from rich.console import Console
from .utils import get_timestamp

console = Console()


def load_ignore_patterns(directory_path: str) -> List[str]:
    """
    Load ignore patterns from .codectxignore file.
    
    Args:
        directory_path: Directory to look for .codectxignore file
        
    Returns:
        List of ignore patterns
    """
    ignore_file_path = os.path.join(directory_path, '.codectxignore')
    
    if not os.path.exists(ignore_file_path):
        console.print(f"{get_timestamp()} [yellow].codectxignore not found, using default patterns[/yellow]")
        return get_default_ignore_patterns()

    try:
        with open(ignore_file_path, 'r', encoding='utf-8') as f:
            patterns = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
        
        # Add default patterns
        patterns.extend(get_default_ignore_patterns())
        
        console.print(f"{get_timestamp()} [cyan]Loaded {len(patterns)} ignore patterns[/cyan]")
        return patterns
        
    except Exception as e:
        console.print(f"{get_timestamp()} [red]Error reading ignore file: {e}[/red]")
        return get_default_ignore_patterns()


def get_default_ignore_patterns() -> List[str]:
    """
    Get default ignore patterns for common files that shouldn't be processed.
    
    Returns:
        List of default ignore patterns
    """
    return [
        # Python
        '__pycache__/*',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'build/*',
        'develop-eggs/*',
        'dist/*',
        'downloads/*',
        'eggs/*',
        '.eggs/*',
        'lib/*',
        'lib64/*',
        'parts/*',
        'sdist/*',
        'var/*',
        'wheels/*',
        '*.egg-info/*',
        '.installed.cfg',
        '*.egg',
        
        # Virtual environments
        'venv/*',
        'env/*',
        '.venv/*',
        '.env/*',
        
        # IDE and editors
        '.vscode/*',
        '.idea/*',
        '*.swp',
        '*.swo',
        '*~',
        '.DS_Store',
        'Thumbs.db',
        
        # Version control
        '.git/*',
        '.gitignore',
        '.svn/*',
        '.hg/*',
        
        # Logs and temporary files
        'logs/*',
        '*.log',
        '*.tmp',
        '*.temp',
        
        # Documentation and output
        'codectx.md',
        '.codectxignore',
        
        # Binary and media files
        '*.jpg',
        '*.jpeg',
        '*.png',
        '*.gif',
        '*.ico',
        '*.pdf',
        '*.zip',
        '*.tar',
        '*.gz',
        '*.rar',
        '*.7z',
        '*.exe',
        '*.dll',
        '*.so',
        '*.dylib',
        
        # Node.js
        'node_modules/*',
        'npm-debug.log',
        'yarn-error.log',
        
        # Package managers
        'Pipfile.lock',
        'poetry.lock',
        'package-lock.json',
        'yarn.lock',
    ]


def should_ignore(file_path: str, ignore_patterns: List[str], base_directory: str) -> bool:
    """
    Check if a file should be ignored based on patterns.
    
    Args:
        file_path: Absolute path to the file
        ignore_patterns: List of ignore patterns
        base_directory: Base directory for relative path calculation
        
    Returns:
        True if file should be ignored, False otherwise
    """
    try:
        relative_path = os.path.relpath(file_path, base_directory)
    except ValueError:
        # If paths are on different drives (Windows), use absolute path
        relative_path = file_path
    
    # Check against each pattern
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
        
        # Also check against just the filename
        filename = os.path.basename(relative_path)
        if fnmatch.fnmatch(filename, pattern):
            return True
    
    return False