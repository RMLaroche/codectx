"""
Core processing for codectx - file processing, AI calls, parsing, and output writing

This module handles the main processing pipeline:
- File content processing and token estimation
- AI API calls with retry logic and error handling
- Mock mode for testing without API dependencies
- Output file generation and summary management
- Checksum-based change detection for efficient updates
"""
import os
import re
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, NamedTuple
from datetime import datetime
from enum import Enum

from .discovery import FileInfo
from .constants import (
    DEFAULT_API_URL, DEFAULT_MODEL, DEFAULT_TIMEOUT, DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TOKEN_THRESHOLD, DEFAULT_MAX_FILE_SIZE_MB, DEFAULT_OUTPUT_FILE,
    MOCK_PROCESSING_DELAY, CHUNK_SIZE, AI_SYSTEM_PROMPT, MOCK_SUMMARY_TEMPLATE
)


class ProcessingMode(Enum):
    """Processing mode options"""
    AI_SUMMARIZATION = "ai"
    MOCK = "mock"
    COPY = "copy"


class ProcessingConfig(NamedTuple):
    """Configuration for processing"""
    mode: ProcessingMode
    api_key: Optional[str] = None
    api_url: str = DEFAULT_API_URL
    model: str = DEFAULT_MODEL
    token_threshold: int = DEFAULT_TOKEN_THRESHOLD
    timeout: float = DEFAULT_TIMEOUT
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS
    max_file_size_mb: float = DEFAULT_MAX_FILE_SIZE_MB
    output_file: str = DEFAULT_OUTPUT_FILE


class SummaryMetadata(NamedTuple):
    """Metadata about an existing summary"""
    file_path: str
    summary_date: datetime
    content: str
    checksum: str = None


class FileProcessor:
    """Main file processor that handles the entire pipeline"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.existing_summaries: Dict[str, SummaryMetadata] = {}
        self._load_existing_summaries()
    
    def process_files(self, files: List[FileInfo], mode: str = "all") -> List[str]:
        """
        Process files and return list of summary strings.
        
        Args:
            files: List of files to process
            mode: Processing mode ("all", "update", or "status")
            
        Returns:
            List of formatted summary strings
        """
        if mode == "update":
            files = self._filter_outdated_files(files)
        elif mode == "status":
            return []  # Status mode doesn't process files
        
        summaries = []
        for file_info in files:
            summary = self._process_single_file(file_info)
            if summary:
                summaries.append(summary)
        
        return summaries
    
    def write_output(self, new_summaries: List[str], current_files: List[FileInfo] = None) -> None:
        """Write summaries to output file, merging with existing summaries for current files only"""
        if not new_summaries and not current_files:
            return
        
        # When current_files is provided, only include summaries for files that still exist
        if current_files:
            all_summaries = []
            for file_info in sorted(current_files, key=lambda f: f.relative_path):
                # Check if we have a newly processed summary for this file
                found_new = False
                for summary in new_summaries:
                    if f"## {file_info.relative_path}\n" in summary:
                        all_summaries.append(summary)
                        found_new = True
                        break
                
                # If no new summary, use existing summary if available
                if not found_new and file_info.relative_path in self.existing_summaries:
                    existing = self.existing_summaries[file_info.relative_path]
                    all_summaries.append(self._format_summary(file_info.relative_path, existing.content, existing.summary_date, existing.checksum))
            summaries_to_write = all_summaries
            total_count = len(current_files)
        else:
            # For update mode without current_files list (legacy), merge new summaries with all existing ones
            # This preserves the old behavior when current_files is not provided
            all_summaries = {}
            
            # Add existing summaries
            for file_path, metadata in self.existing_summaries.items():
                all_summaries[file_path] = self._format_summary(file_path, metadata.content, metadata.summary_date, metadata.checksum)
            
            # Add/update with new summaries
            for summary in new_summaries:
                # Extract file path from summary
                lines = summary.split('\n')
                if lines and lines[0].startswith('## '):
                    file_path = lines[0][3:].strip()
                    all_summaries[file_path] = summary
            
            # Sort by file path
            summaries_to_write = [all_summaries[path] for path in sorted(all_summaries.keys())]
            total_count = len(summaries_to_write)
        
        # Create header with metadata
        header = f"""# Project Summary

Generated by codectx on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total files processed: {total_count}

---

"""
        
        try:
            with open(self.config.output_file, 'w', encoding='utf-8') as file:
                file.write(header)
                for summary in summaries_to_write:
                    file.write(summary)
                    if not summary.endswith('\n'):
                        file.write('\n')
                    file.write('\n')  # Extra newline between summaries
        except Exception as e:
            raise IOError(f"Failed to write to {self.config.output_file}: {e}")
    
    def _format_summary(self, file_path: str, content: str, summary_date: datetime = None, checksum: str = None) -> str:
        """Format a file summary with timestamp and checksum metadata"""
        if summary_date is None:
            summary_date = datetime.now()
        
        timestamp_str = summary_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Add checksum to timestamp line if available
        if checksum:
            timestamp_line = f"Summarized on {timestamp_str} (checksum: {checksum})"
        else:
            timestamp_line = f"Summarized on {timestamp_str}"
        
        # Remove duplicate header if content already starts with "## File:"
        cleaned_content = content
        if content.startswith(f"## File: {file_path}"):
            first_line_end = content.find('\n')
            if first_line_end != -1:
                cleaned_content = content[first_line_end + 1:].lstrip()
        
        return f"""## {file_path}

{timestamp_line}

{cleaned_content}"""
    
    def get_file_status(self, files: List[FileInfo]) -> Dict[str, str]:
        """Get status of files (up-to-date, outdated, new) based on checksums"""
        status = {}
        for file_info in files:
            if file_info.relative_path in self.existing_summaries:
                existing = self.existing_summaries[file_info.relative_path]
                # Compare checksums instead of dates
                if existing.checksum and file_info.checksum != existing.checksum:
                    status[file_info.relative_path] = "outdated"
                else:
                    status[file_info.relative_path] = "up-to-date"
            else:
                status[file_info.relative_path] = "new"
        
        return status
    
    def _load_existing_summaries(self) -> None:
        """Load existing summaries from output file"""
        if not os.path.exists(self.config.output_file):
            return
        
        try:
            with open(self.config.output_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse summaries using regex - now includes checksum
            # Pattern matches: ## filepath\n\nSummarized on date (checksum: hash)\n\ncontent
            pattern = r'## (.+?)\n\nSummarized on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?: \(checksum: ([a-f0-9]{64}|unreadable)\))?\n\n(.*?)(?=\n## |\Z)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for file_path, date_str, checksum, summary_content in matches:
                try:
                    summary_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    self.existing_summaries[file_path] = SummaryMetadata(
                        file_path=file_path,
                        summary_date=summary_date,
                        content=summary_content.strip(),
                        checksum=checksum or None
                    )
                except ValueError:
                    continue  # Skip malformed dates
                    
        except Exception as e:
            print(f"Warning: Could not parse existing {self.config.output_file}: {e}")
    
    def _filter_outdated_files(self, files: List[FileInfo]) -> List[FileInfo]:
        """Filter to only files that need updating based on checksums"""
        outdated = []
        for file_info in files:
            if file_info.relative_path not in self.existing_summaries:
                outdated.append(file_info)  # New file
            else:
                existing = self.existing_summaries[file_info.relative_path]
                # Compare checksums instead of dates
                if not existing.checksum or file_info.checksum != existing.checksum:
                    outdated.append(file_info)  # Content changed
        
        return outdated
    
    def _process_single_file(self, file_info: FileInfo) -> Optional[str]:
        """Process a single file and return formatted summary"""
        try:
            # Read file content
            content = self._read_file(file_info.path)
            if content is None:
                return None
            
            # Check file size
            file_size_mb = file_info.size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                summary_content = f"File size ({file_size_mb:.1f}MB) exceeds limit ({self.config.max_file_size_mb}MB)"
                return self._format_summary(file_info.relative_path, summary_content, checksum=file_info.checksum)
            
            # Estimate token count (rough approximation)
            token_count = len(content.split()) + len(content) // 4
            
            if token_count < self.config.token_threshold or self.config.mode == ProcessingMode.COPY:
                # Use raw content for small files or copy mode
                return self._format_summary(file_info.relative_path, content, checksum=file_info.checksum)
            else:
                # Process with AI or mock
                if self.config.mode == ProcessingMode.MOCK:
                    summary_content = self._generate_mock_summary()
                else:
                    summary_content = self._call_ai_api(file_info.relative_path, content)
                
                # If API call failed, don't create a summary
                if summary_content.startswith("Error:"):
                    return None
                
                return self._format_summary(file_info.relative_path, summary_content, checksum=file_info.checksum)
        
        except Exception as e:
            # Don't create error summaries - let file remain as "needs update"
            return None
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content with encoding detection"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Check if this looks like binary content
                if '\x00' in content or len([c for c in content if ord(c) < 32 and c not in '\n\r\t']) > len(content) * 0.1:
                    return None  # Skip binary files
                
                return content
            
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                return None
        
        return None  # Could not decode with any encoding
    
    def _call_ai_api(self, file_path: str, content: str) -> str:
        """Call AI API to generate summary"""
        if not self.config.api_key:
            return "Error: API key not provided"
        
        user_prompt = f"""Please analyze this code file and provide a structured summary.

File: {file_path}

Content:
```
{content}
```"""

        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': self.config.model,
            'messages': [
                {'role': 'system', 'content': AI_SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.1,
            'max_tokens': 500
        }
        
        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = requests.post(
                    self.config.api_url,
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        ai_content = result['choices'][0]['message']['content'].strip()
                        # Remove duplicate header if AI added one
                        if ai_content.startswith(f"## File: {file_path}"):
                            first_line_end = ai_content.find('\n')
                            if first_line_end != -1:
                                ai_content = ai_content[first_line_end + 1:].lstrip()
                        return ai_content
                    else:
                        last_error = "No summary available from API"
                else:
                    last_error = f"API error {response.status_code}: {response.text}"
                    
            except requests.exceptions.Timeout:
                last_error = f"API request timed out after {self.config.timeout}s"
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {e}"
            except requests.exceptions.RequestException as e:
                last_error = f"API request failed: {e}"
            except Exception as e:
                last_error = f"Unexpected error: {e}"
            
            if attempt < self.config.retry_attempts - 1:
                time.sleep(MOCK_PROCESSING_DELAY)  # Brief pause between retries
        
        return f"Error: {last_error}"
    
    def _generate_mock_summary(self) -> str:
        """Generate a mock summary for testing with simulated delay"""
        # Simulate HTTP call time
        time.sleep(MOCK_PROCESSING_DELAY)
        return MOCK_SUMMARY_TEMPLATE
    
