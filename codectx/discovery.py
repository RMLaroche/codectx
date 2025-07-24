"""
File discovery and ignore handling for codectx

This module handles:
- Recursive directory traversal and file discovery
- .codectxignore pattern matching and file filtering
- File metadata extraction (size, modification time, checksum)
- Comprehensive default ignore patterns for common development files
"""
import os
import fnmatch
import hashlib
from pathlib import Path
from typing import List, Set, NamedTuple
from datetime import datetime

from .constants import CHUNK_SIZE, DEFAULT_IGNORE_PATTERNS


class FileInfo:
    """Information about a discovered file"""
    def __init__(self, path: str, relative_path: str, size: int, modified_time: datetime, checksum: str = None):
        self.path = path
        self.relative_path = relative_path
        self.size = size
        self.modified_time = modified_time
        self.checksum = checksum or self._calculate_checksum()
        # Processing status tracking
        self._processing_status = 'pending'
        self._summary_date_str = '[dim]Never[/dim]'
    
    def _calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of file content"""
        try:
            with open(self.path, 'rb') as f:
                file_hash = hashlib.sha256()
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except (OSError, IOError):
            # If we can't read the file, return a placeholder
            return "unreadable"
    
    @property
    def size_str(self) -> str:
        """Human readable file size"""
        if self.size < 1024:
            return f"{self.size}B"
        elif self.size < 1024 * 1024:
            return f"{self.size // 1024}K"
        else:
            return f"{self.size // (1024 * 1024)}M"
    
    @property
    def modified_str(self) -> str:
        """Human readable modification time"""
        return self.modified_time.strftime("%m-%d %H:%M")


class DiscoveryResult(NamedTuple):
    """Result of file discovery"""
    directory: str
    files_to_process: List[FileInfo]
    ignored_files: List[str]
    ignore_patterns_count: int


def discover_files(directory: str = ".") -> DiscoveryResult:
    """
    Discover all files in directory that should be processed.
    
    Args:
        directory: Directory to scan
        
    Returns:
        DiscoveryResult with files to process and ignored files
    """
    directory = os.path.abspath(directory)
    
    if not os.path.exists(directory):
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not os.path.isdir(directory):
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Load ignore patterns
    ignore_patterns = _load_ignore_patterns(directory)
    
    files_to_process = []
    ignored_files = []
    
    # Walk through directory
    for root, dirs, files in os.walk(directory):
        # Filter directories in-place to avoid traversing ignored dirs
        dirs[:] = [d for d in dirs if not _should_ignore(os.path.join(root, d), directory, ignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            
            if _should_ignore(file_path, directory, ignore_patterns):
                ignored_files.append(relative_path)
                continue
            
            # Get file info
            try:
                stat_info = os.stat(file_path)
                file_info = FileInfo(
                    path=file_path,
                    relative_path=relative_path,
                    size=stat_info.st_size,
                    modified_time=datetime.fromtimestamp(stat_info.st_mtime)
                )
                files_to_process.append(file_info)
            except (OSError, IOError):
                # Skip files we can't read
                ignored_files.append(relative_path)
    
    return DiscoveryResult(
        directory=directory,
        files_to_process=sorted(files_to_process, key=lambda f: f.relative_path),
        ignored_files=sorted(ignored_files),
        ignore_patterns_count=len(ignore_patterns)
    )


def _load_ignore_patterns(directory: str) -> Set[str]:
    """Load ignore patterns from .codectxignore file and defaults"""
    patterns = set()
    
    # Use default ignore patterns from constants
    patterns.update(DEFAULT_IGNORE_PATTERNS)
    
    # Load custom patterns from .codectxignore
    ignore_file = os.path.join(directory, ".codectxignore")
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except (OSError, IOError):
            pass  # Continue with default patterns if we can't read the file
    
    return patterns


def _should_ignore(file_path: str, base_directory: str, patterns: Set[str]) -> bool:
    """Check if a file should be ignored based on patterns"""
    relative_path = os.path.relpath(file_path, base_directory)
    
    # Always ignore codectx.md output file
    if os.path.basename(file_path) == "codectx.md":
        return True
    
    # Check against each pattern
    for pattern in patterns:
        # Handle directory patterns (ending with /*)
        if pattern.endswith("/*"):
            dir_pattern = pattern[:-2]  # Remove /*
            if fnmatch.fnmatch(relative_path, dir_pattern) or relative_path.startswith(dir_pattern + "/"):
                return True
        # Handle file patterns
        elif fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    
    return False