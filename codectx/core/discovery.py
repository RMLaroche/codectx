"""
File discovery and ignore handling
"""
import os
from typing import List
from ..utils.ignore_handler import load_ignore_patterns, should_ignore
from .models import DiscoveryResult, FileInfo


def discover_files(directory_path: str = ".") -> DiscoveryResult:
    """
    Discover files in directory and return comprehensive results.
    
    Args:
        directory_path: Directory to scan
        
    Returns:
        DiscoveryResult with all discovery information
    """
    ignore_patterns = load_ignore_patterns(directory_path)
    
    files_to_process = []
    ignored_files = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if should_ignore(file_path, ignore_patterns, directory_path):
                ignored_files.append(file_path)
            else:
                file_info = FileInfo.from_path(file_path)
                files_to_process.append(file_info)
    
    return DiscoveryResult(
        directory=os.path.abspath(directory_path),
        files_to_process=files_to_process,
        ignored_files=ignored_files,
        ignore_patterns_count=len(ignore_patterns)
    )