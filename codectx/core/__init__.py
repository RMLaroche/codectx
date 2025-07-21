"""
Core functionality for codectx
"""
from .discovery import discover_files
from .processor import FileProcessor
from .models import (
    FileInfo,
    DiscoveryResult,
    ProcessingResult,
    ProcessingConfig,
    ProcessingStats,
    ProcessingStatus,
    ProcessingMode
)

__all__ = [
    "discover_files",
    "FileProcessor",
    "FileInfo",
    "DiscoveryResult", 
    "ProcessingResult",
    "ProcessingConfig",
    "ProcessingStats",
    "ProcessingStatus",
    "ProcessingMode"
]