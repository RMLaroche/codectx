"""
Direct mode implementation for codectx
"""
import os
import sys
from rich.console import Console
from rich.progress import Progress
from rich.live import Live

from ..core.discovery import discover_files
from ..core.processor import FileProcessor
from ..core.models import ProcessingConfig, ProcessingMode, FileInfo, ProcessingResult
from ..ui.components import (
    display_welcome_banner,
    create_file_table,
    display_processing_complete,
    display_error,
    display_info,
    display_warning
)
from ..utils.utils import get_timestamp


class DirectMode:
    """Direct processing mode for automation and scripts"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def run(self, config: ProcessingConfig) -> None:
        """
        Run direct processing mode.
        
        Args:
            config: Processing configuration
        """
        # Validate directory
        if not os.path.exists(config.directory_path):
            display_error(self.console, f"The directory {config.directory_path} does not exist.")
            sys.exit(1)

        if not os.path.isdir(config.directory_path):
            display_error(self.console, f"{config.directory_path} is not a directory.")
            sys.exit(1)
        
        try:
            # Display welcome
            display_welcome_banner(self.console, interactive=False)
            
            # Discover files
            display_info(self.console, "Discovering files...")
            discovery = discover_files(config.directory_path)
            
            # Show ignored files
            for ignored_file in discovery.ignored_files:
                display_warning(self.console, f"Ignoring {ignored_file}...")
            
            if not discovery.files_to_process:
                display_warning(self.console, f"No files to process in {config.directory_path}")
                return
            
            display_info(self.console, f"Found {len(discovery.files_to_process)} files to process")
            
            # Process files with progress display
            self._process_with_progress(discovery.files_to_process, config)
            
        except KeyboardInterrupt:
            display_warning(self.console, "Processing interrupted by user")
            sys.exit(1)
        except Exception as e:
            display_error(self.console, str(e))
            sys.exit(1)
    
    def _process_with_progress(self, files: list[FileInfo], config: ProcessingConfig) -> None:
        """
        Process files with progress display using the original table format.
        
        Args:
            files: List of files to process
            config: Processing configuration
        """
        # Create summary parser to preserve existing summaries
        from ..core.summary_parser import SummaryParser
        summary_parser = SummaryParser(config.output_file)
        processor = FileProcessor(config, getattr(self, 'codectx_config', None), summary_parser)
        
        # Initialize progress bar
        progress = Progress(console=self.console)
        task = progress.add_task("Processing files", total=len(files))
        
        # Create live table similar to original implementation
        def create_live_table():
            return create_file_table(files, show_all=True)
        
        with Live(create_live_table(), refresh_per_second=4, console=self.console) as live:
            for file_info in files:
                # Process the file
                result = processor.process_file(file_info)
                
                # Update progress and display
                progress.update(task, advance=1)
                live.update(create_live_table())
                
                # Handle errors
                if result.status.value == "error":
                    display_error(self.console, f"Error processing {file_info.path}: {result.error_message}")
        
        # Write output
        try:
            processor.write_output(files)
            display_processing_complete(
                self.console, 
                len(files), 
                config.output_file
            )
        except Exception as e:
            display_error(self.console, f"Error writing output: {e}")


def run_direct_mode(directory_path: str, mock_mode: bool = False, copy_mode: bool = False, 
                    codectx_config=None) -> None:
    """
    Run direct mode with the given parameters.
    
    Args:
        directory_path: Directory to process
        mock_mode: Whether to use mock mode
        copy_mode: Whether to use copy mode
        codectx_config: Optional CodectxConfig object with advanced settings
    """
    from ..utils.configuration import get_config
    
    # Use provided config or load default
    if codectx_config is None:
        codectx_config = get_config()
    
    # Determine processing mode
    if mock_mode:
        mode = ProcessingMode.MOCK
    elif copy_mode:
        mode = ProcessingMode.COPY
    else:
        mode = ProcessingMode.AI_SUMMARIZATION
    
    # Create configuration
    config = ProcessingConfig(
        mode=mode,
        directory_path=directory_path,
        output_file=codectx_config.output_filename
    )
    
    # Run direct mode
    direct_mode = DirectMode()
    direct_mode.codectx_config = codectx_config  # Pass the config to the mode
    direct_mode.run(config)