"""
Summary parsing and update detection for codectx
"""
import os
import re
from typing import Dict, List, Optional
from datetime import datetime

from .models import FileInfo, SummaryMetadata, ProcessingStatus


class SummaryParser:
    """Parser for existing codectx.md files to detect outdated summaries"""
    
    def __init__(self, output_file: str = "codectx.md"):
        self.output_file = output_file
        self.existing_summaries: Dict[str, SummaryMetadata] = {}
    
    def load_existing_summaries(self) -> None:
        """Load and parse existing summaries from codectx.md"""
        if not os.path.exists(self.output_file):
            return
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Split content into sections by "## " headers
            sections = re.split(r'\n## ', content)
            
            current_file_section = ""
            current_file_path = ""
            
            for i, section in enumerate(sections):
                if i == 0:
                    # Skip the header section
                    continue
                
                # Add back the "## " prefix (except for first section after split)
                section = "## " + section
                
                # Extract section header 
                header_match = re.match(r'## (.+)', section)
                if not header_match:
                    continue
                
                header_line = header_match.group(1).strip()
                
                # Check if this is a file path section (timestamp pattern) or content section
                if re.search(r'Summarized on \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', section):
                    # This is a main file section with timestamp
                    # Save previous file if we have one
                    if current_file_section and current_file_path:
                        metadata = SummaryMetadata.parse_from_content(current_file_section, current_file_path)
                        if metadata:
                            self.existing_summaries[current_file_path] = metadata
                    
                    # Start new file section
                    current_file_path = header_line
                    current_file_section = section
                    
                elif current_file_section and header_line.startswith("File: "):
                    # This is a content section belonging to the current file
                    current_file_section += "\n\n" + section
            
            # Don't forget the last file
            if current_file_section and current_file_path:
                metadata = SummaryMetadata.parse_from_content(current_file_section, current_file_path)
                if metadata:
                    self.existing_summaries[current_file_path] = metadata
                    
        except Exception as e:
            # If we can't parse existing file, treat as if no summaries exist
            print(f"Warning: Could not parse existing {self.output_file}: {e}")
    
    def update_file_status(self, files: List[FileInfo]) -> None:
        """Update file status based on existing summaries"""
        self.load_existing_summaries()
        
        for file_info in files:
            existing_summary = self.existing_summaries.get(file_info.path)
            
            if existing_summary:
                # File has been summarized before
                file_info.update_summary_date(existing_summary.summary_date)
            else:
                # File has never been summarized
                file_info.status = ProcessingStatus.OUTDATED
    
    def get_outdated_files(self, files: List[FileInfo]) -> List[FileInfo]:
        """Get list of files that need updating"""
        self.update_file_status(files)
        return [f for f in files if f.is_outdated()]
    
    def get_updated_files(self, files: List[FileInfo]) -> List[FileInfo]:
        """Get list of files that are up to date"""
        self.update_file_status(files)
        return [f for f in files if not f.is_outdated()]