"""
Core file processing logic (mode-agnostic)
"""
from typing import List, Callable, Optional
from ..utils.api_client import summarize_file
from ..utils.file_writer import write_summaries_to_file, format_file_summary
from ..utils.configuration import CodectxConfig, get_config
from .models import FileInfo, ProcessingResult, ProcessingConfig, ProcessingStatus
from .summary_parser import SummaryParser


class FileProcessor:
    """Core file processor that can work with different UI modes"""
    
    def __init__(self, config: ProcessingConfig, codectx_config: Optional[CodectxConfig] = None, summary_parser: Optional[SummaryParser] = None):
        self.config = config
        self.codectx_config = codectx_config or get_config()
        self.summaries: List[str] = []
        self.summary_parser = summary_parser
        
    def process_file(self, file_info: FileInfo) -> ProcessingResult:
        """
        Process a single file and return the result.
        
        Args:
            file_info: File to process
            
        Returns:
            ProcessingResult with summary and status
        """
        try:
            # Update file status
            file_info.status = ProcessingStatus.PROCESSING
            
            # Process the file with configuration
            summary = summarize_file(
                file_info.path, 
                self.config.mock_mode, 
                self.config.copy_mode,
                self.codectx_config
            )
            
            # Determine final status
            if "RAW CONTENT" in summary:
                status = ProcessingStatus.COPIED
            else:
                status = ProcessingStatus.COMPLETED
                
            # Update file info
            file_info.status = status
            
            # Store summary for later writing with timestamp format
            if summary:
                formatted_summary = format_file_summary(file_info.path, summary)
                self.summaries.append(formatted_summary)
            
            return ProcessingResult(
                file_info=file_info,
                summary=summary,
                status=status
            )
            
        except Exception as e:
            # Update file info with error
            file_info.status = ProcessingStatus.ERROR
            file_info.error_message = str(e)
            
            return ProcessingResult(
                file_info=file_info,
                summary="",
                status=ProcessingStatus.ERROR,
                error_message=str(e)
            )
    
    def process_files(
        self, 
        files: List[FileInfo], 
        progress_callback: Optional[Callable[[FileInfo, ProcessingResult], None]] = None
    ) -> List[ProcessingResult]:
        """
        Process multiple files with optional progress callback.
        
        Args:
            files: List of files to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processing results
        """
        results = []
        
        for file_info in files:
            result = self.process_file(file_info)
            results.append(result)
            
            # Summary is already stored in process_file method
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(file_info, result)
        
        return results
    
    def write_output(self, all_files: Optional[List[FileInfo]] = None) -> None:
        """Write all summaries to output file, including existing up-to-date summaries"""
        final_summaries = self._merge_summaries(all_files) if all_files and self.summary_parser else self.summaries
        
        if final_summaries:
            write_summaries_to_file(final_summaries, self.config.output_file)
    
    def _merge_summaries(self, all_files: List[FileInfo]) -> List[str]:
        """Merge new summaries with existing up-to-date summaries"""
        final_summaries = []
        processed_files = {summary.split('\n')[0].replace('## ', ''): summary for summary in self.summaries}
        
        # Add summaries for all files, preserving order
        for file_info in all_files:
            if file_info.path in processed_files:
                # Use new summary for processed files
                final_summaries.append(processed_files[file_info.path])
            elif self.summary_parser and file_info.path in self.summary_parser.existing_summaries:
                # Use existing summary for up-to-date files
                existing_meta = self.summary_parser.existing_summaries[file_info.path]
                final_summaries.append(existing_meta.content)
        
        return final_summaries
    
    def get_summary_count(self) -> int:
        """Get number of summaries collected"""
        return len(self.summaries)