"""
Update mode implementation for codectx - processes only changed files
"""
from typing import List
from rich.console import Console

from ..core.discovery import discover_files
from ..core.processor import FileProcessor
from ..core.summary_parser import SummaryParser
from ..core.models import ProcessingConfig, ProcessingMode, FileInfo, ProcessingStatus
from ..ui.components import (
    display_welcome_banner,
    create_file_table,
    create_discovery_summary_panel,
    display_processing_complete,
    display_error,
    display_info,
    display_warning
)
from ..utils.utils import get_timestamp


def run_update_mode(
    directory_path: str = ".", 
    mock_mode: bool = False, 
    copy_mode: bool = False,
    codectx_config=None,
    console: Console = None
) -> None:
    """
    Run update mode - only process files that have changed since last summary.
    
    Args:
        directory_path: Directory to process
        mock_mode: Whether to run in mock mode
        copy_mode: Whether to run in copy mode
        console: Rich Console object
    """
    from ..utils.configuration import get_config
    
    console = console or Console()
    
    # Use provided config or load default
    if codectx_config is None:
        codectx_config = get_config()
    
    # Display banner
    display_welcome_banner(console, interactive=False)
    display_info(console, "🔄 Update Mode: Processing only changed files")
    
    # Discover files
    display_info(console, "Discovering files...")
    discovery = discover_files(directory_path)
    
    if not discovery.files_to_process:
        display_warning(console, "No files found to process")
        return
    
    # Parse existing summaries and determine which files need updating
    display_info(console, "Checking for existing summaries...")
    summary_parser = SummaryParser()
    
    # Update file status based on existing summaries
    summary_parser.update_file_status(discovery.files_to_process)
    
    # Filter to only outdated files
    outdated_files = summary_parser.get_outdated_files(discovery.files_to_process)
    updated_files = summary_parser.get_updated_files(discovery.files_to_process)
    
    # Show summary of what we found
    console.print()
    console.print(f"[green]📊 File Analysis Complete[/green]")
    console.print(f"[yellow]⚠️  Outdated files:[/yellow] {len(outdated_files)}")
    console.print(f"[green]✅ Up-to-date files:[/green] {len(updated_files)}")
    console.print()
    
    if not outdated_files:
        display_info(console, "✅ All files are up to date! No processing needed.")
        return
    
    # Show the files that will be processed
    if len(outdated_files) <= 10:
        # Show all files if not too many
        table = create_file_table(
            discovery.files_to_process, 
            title=f"📂 Files Overview ({len(outdated_files)} need updates)",
            show_all=True
        )
        console.print(table)
    else:
        # Show summary table
        summary_panel = create_discovery_summary_panel(discovery)
        console.print(summary_panel)
        console.print(f"[yellow]⚠️  Processing {len(outdated_files)} outdated files...[/yellow]")
    
    console.print()
    
    # Determine processing mode
    if mock_mode:
        mode = ProcessingMode.MOCK
        display_info(console, "🤖 Running in mock mode (no API calls)")
    elif copy_mode:
        mode = ProcessingMode.COPY
        display_info(console, "📄 Running in copy mode (raw content only)")
    else:
        mode = ProcessingMode.AI_SUMMARIZATION
        display_info(console, "🤖 Running AI summarization")
    
    # Create configuration
    config = ProcessingConfig(
        mode=mode,
        directory_path=directory_path,
        output_file=codectx_config.output_filename
    )
    
    # Process only the outdated files
    processor = FileProcessor(config, codectx_config)
    
    try:
        display_info(console, f"🚀 Processing {len(outdated_files)} outdated files...")
        
        for i, file_info in enumerate(outdated_files, 1):
            console.print(f"{get_timestamp()} [cyan]Processing ({i}/{len(outdated_files)}): {file_info.display_path}[/cyan]")
            
            # Update status to processing
            file_info.status = ProcessingStatus.PROCESSING
            
            # Process the file
            result = processor.process_file(file_info)
            
            if result.status in [ProcessingStatus.COMPLETED, ProcessingStatus.COPIED]:
                console.print(f"{get_timestamp()} [green]✅ {file_info.display_path}[/green]")
            else:
                console.print(f"{get_timestamp()} [red]❌ {file_info.display_path}: {result.error_message}[/red]")
        
        # Write output
        console.print()
        display_info(console, "📝 Writing output...")
        processor.write_output()
        
        # Show completion message
        display_processing_complete(
            console,
            len(outdated_files),
            config.output_file
        )
        
        # Show final summary
        successful = len([f for f in outdated_files if f.status in [ProcessingStatus.COMPLETED, ProcessingStatus.COPIED]])
        failed = len(outdated_files) - successful
        
        console.print()
        console.print(f"[green]✅ Successfully processed: {successful} files[/green]")
        if failed > 0:
            console.print(f"[red]❌ Failed: {failed} files[/red]")
        console.print(f"[blue]📄 {len(updated_files)} files were already up to date[/blue]")
        
    except KeyboardInterrupt:
        display_warning(console, "⚠️ Processing interrupted by user")
    except Exception as e:
        display_error(console, f"Processing failed: {e}")
        raise