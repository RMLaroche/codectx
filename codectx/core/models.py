"""
Data models for codectx
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


class ProcessingStatus(Enum):
    """Status of file processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    COPIED = "copied"
    UPDATED = "updated"
    OUTDATED = "outdated"


class ProcessingMode(Enum):
    """Processing mode for files"""
    AI_SUMMARIZATION = "ai"
    MOCK = "mock"
    COPY = "copy"
    UPDATE_CHANGED = "update"


@dataclass
class FileInfo:
    """Information about a discoverable file"""
    path: str
    display_path: str
    size: int
    size_str: str
    modified: datetime
    modified_str: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    summary_date: Optional[datetime] = None
    summary_date_str: Optional[str] = None
    
    @classmethod
    def from_path(cls, file_path: str) -> 'FileInfo':
        """Create FileInfo from file path"""
        import os
        from datetime import datetime
        
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Format size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size // 1024}KB"
            else:
                size_str = f"{size // (1024 * 1024)}MB"
            
            # Format modification time
            modified_str = modified.strftime('%m-%d %H:%M')
            
            # Format display path
            display_path = file_path if len(file_path) < 48 else f"...{file_path[-45:]}"
            
        except OSError:
            size = 0
            size_str = "?"
            modified = datetime.now()
            modified_str = "Unknown"
            display_path = file_path if len(file_path) < 48 else f"...{file_path[-45:]}"
        
        return cls(
            path=file_path,
            display_path=display_path,
            size=size,
            size_str=size_str,
            modified=modified,
            modified_str=modified_str
        )
    
    def is_outdated(self) -> bool:
        """Check if file is outdated (modified after last summary)"""
        if self.summary_date is None:
            return True  # Never summarized = outdated
        return self.modified > self.summary_date
    
    def update_summary_date(self, summary_date: datetime) -> None:
        """Update summary date and formatted string"""
        self.summary_date = summary_date
        self.summary_date_str = summary_date.strftime('%m-%d %H:%M')
        
        # Update status based on whether file is outdated
        if self.is_outdated():
            self.status = ProcessingStatus.OUTDATED
        else:
            self.status = ProcessingStatus.UPDATED


@dataclass
class DiscoveryResult:
    """Result of file discovery process"""
    directory: str
    files_to_process: List[FileInfo]
    ignored_files: List[str]
    ignore_patterns_count: int
    
    @property
    def total_files(self) -> int:
        """Total files found"""
        return len(self.files_to_process) + len(self.ignored_files)


@dataclass
class ProcessingResult:
    """Result of processing a single file"""
    file_info: FileInfo
    summary: str
    status: ProcessingStatus
    error_message: Optional[str] = None


@dataclass
class ProcessingConfig:
    """Configuration for processing"""
    mode: ProcessingMode
    directory_path: str
    output_file: str = "codectx.md"
    
    @property
    def mock_mode(self) -> bool:
        """Whether this is mock mode"""
        return self.mode == ProcessingMode.MOCK
    
    @property
    def copy_mode(self) -> bool:
        """Whether this is copy mode"""
        return self.mode == ProcessingMode.COPY


@dataclass
class ProcessingStats:
    """Live statistics during processing"""
    total: int
    completed: int = 0
    processing: int = 0
    pending: int = 0
    errors: int = 0
    
    def __post_init__(self):
        """Calculate pending on initialization"""
        self.pending = self.total - self.completed - self.processing - self.errors
    
    def update_from_files(self, files: List[FileInfo]) -> None:
        """Update stats from file list"""
        self.completed = sum(1 for f in files if f.status in [ProcessingStatus.COMPLETED, ProcessingStatus.COPIED])
        self.processing = sum(1 for f in files if f.status == ProcessingStatus.PROCESSING)
        self.errors = sum(1 for f in files if f.status == ProcessingStatus.ERROR)
        self.pending = self.total - self.completed - self.processing - self.errors


@dataclass
class SummaryMetadata:
    """Metadata extracted from existing summaries"""
    file_path: str
    summary_date: datetime
    content: str
    
    @classmethod
    def parse_from_content(cls, content: str, file_path: str) -> Optional['SummaryMetadata']:
        """Parse summary metadata from codectx.md content"""
        # Look for timestamp in summary content
        # Pattern: "Summarized on YYYY-MM-DD HH:MM:SS"
        timestamp_pattern = r'Summarized on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        match = re.search(timestamp_pattern, content)
        
        if match:
            try:
                summary_date = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                return cls(
                    file_path=file_path,
                    summary_date=summary_date,
                    content=content
                )
            except ValueError:
                pass
        
        return None