"""
Main CLI for codectx - all modes, configuration, and command handling
"""
import os
import argparse
from pathlib import Path
from typing import Optional

from . import __version__
from .discovery import discover_files
from .processing import FileProcessor, ProcessingConfig, ProcessingMode
from .ui import (
    display_welcome, display_info, display_success, display_warning, display_error,
    display_file_stats, display_file_table, display_processing_progress, 
    display_completion_stats, display_status_summary, create_live_processing_context
)


def main() -> None:
    """Main CLI entry point"""
    try:
        args = _parse_arguments()
        config = _create_config(args)
        
        if args.status:
            _run_status_mode(args.directory_path, config)
        elif args.scan_all:
            _run_scan_all_mode(args.directory_path, config)
        else:
            _run_update_mode(args.directory_path, config)
            
    except KeyboardInterrupt:
        display_warning("Operation interrupted by user")
    except Exception as e:
        display_error(str(e))
        exit(1)


def _parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="codectx - AI-powered code context and file summarization tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codectx                    # Update changed files in current directory (default)
  codectx /path/to/project   # Update changed files in specified directory  
  codectx --status .         # Show file status summary without processing
  codectx --scan-all .       # Process all files (override update mode)
  codectx --mock-mode .      # Test without API calls
  codectx --copy-mode .      # Copy content without AI summarization
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'directory_path',
        nargs='?',
        default='.',
        help='The directory to process (default: current directory)'
    )
    
    # Mode arguments
    parser.add_argument(
        '--scan-all',
        action='store_true',
        help='Process all files instead of just changed files'
    )
    parser.add_argument(
        '--status',
        action='store_true', 
        help='Show file status summary table without processing'
    )
    parser.add_argument(
        '--mock-mode',
        action='store_true',
        help='Enable mock mode for testing without API calls'
    )
    parser.add_argument(
        '--copy-mode',
        action='store_true',
        help='Copy file content without AI summarization'
    )
    
    # Configuration arguments
    parser.add_argument(
        '--api-key',
        help='API key (overrides CODECTX_API_KEY env var)'
    )
    parser.add_argument(
        '--api-url',
        help='API URL (default: Mistral Codestral API)'
    )
    parser.add_argument(
        '--model',
        help='AI model to use (default: codestral-latest)'
    )
    parser.add_argument(
        '--token-threshold',
        type=int,
        default=200,
        help='Token threshold for AI summarization (default: 200)'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=30.0,
        help='API timeout in seconds (default: 30.0)'
    )
    parser.add_argument(
        '--retry-attempts', 
        type=int,
        default=3,
        help='Number of API retry attempts (default: 3)'
    )
    parser.add_argument(
        '--max-file-size',
        type=float,
        default=10.0,
        help='Maximum file size in MB to process (default: 10.0)'
    )
    parser.add_argument(
        '--output-file',
        default='codectx.md',
        help='Output filename (default: codectx.md)'
    )
    
    # Info arguments
    parser.add_argument(
        '--version',
        action='version',
        version=f'codectx {__version__}'
    )
    
    return parser.parse_args()


def _create_config(args: argparse.Namespace) -> ProcessingConfig:
    """Create processing configuration from arguments"""
    # Determine processing mode
    if args.mock_mode:
        mode = ProcessingMode.MOCK
    elif args.copy_mode:
        mode = ProcessingMode.COPY
    else:
        mode = ProcessingMode.AI_SUMMARIZATION
    
    # Get configuration from args or environment
    api_key = args.api_key or os.getenv('CODECTX_API_KEY')
    api_url = args.api_url or os.getenv('CODECTX_API_URL', 'https://codestral.mistral.ai/v1/chat/completions')
    model = args.model or os.getenv('CODECTX_MODEL', 'codestral-latest')
    
    return ProcessingConfig(
        mode=mode,
        api_key=api_key,
        api_url=api_url,
        model=model,
        token_threshold=args.token_threshold,
        timeout=args.timeout,
        retry_attempts=args.retry_attempts,
        max_file_size_mb=args.max_file_size,
        output_file=args.output_file
    )


def _run_status_mode(directory: str, config: ProcessingConfig) -> None:
    """Run status mode - show file status without processing"""
    display_welcome()
    display_info("🔍 Analyzing project files...")
    
    # Discover files
    discovery = discover_files(directory)
    if not discovery.files_to_process:
        display_info("❌ No files found to analyze!")
        return
    
    # Get file status
    processor = FileProcessor(config)
    file_status = processor.get_file_status(discovery.files_to_process)
    
    # Display status summary
    display_status_summary(discovery, file_status)


def _run_update_mode(directory: str, config: ProcessingConfig) -> None:
    """Run update mode - process only changed files"""
    # Check API key requirement for AI mode
    if config.mode == ProcessingMode.AI_SUMMARIZATION and not config.api_key:
        raise ValueError(
            "API key required for AI summarization. "
            "Set CODECTX_API_KEY environment variable or use --api-key argument. "
            "Use --mock-mode for testing without API calls."
        )
    
    display_welcome()
    display_info("🔄 Update Mode: Processing only changed files")
    display_info("Discovering files...")
    
    # Discover files
    discovery = discover_files(directory)
    if not discovery.files_to_process:
        display_info("❌ No files found to process!")
        return
    
    # Get file status and filter to outdated files
    processor = FileProcessor(config)
    file_status = processor.get_file_status(discovery.files_to_process)
    
    outdated_files = [
        f for f in discovery.files_to_process
        if file_status[f.relative_path] in ["outdated", "new"]
    ]
    
    display_info("Checking for existing summaries...")
    display_file_stats(discovery, file_status)
    
    if not outdated_files:
        display_info("✅ All files are up to date!")
        return
    
    # Show files to be processed
    if len(outdated_files) <= 10:
        display_file_table(outdated_files, file_status, f"📂 Files to Update ({len(outdated_files)} files)")
    else:
        display_info(f"📋 Updating {len(outdated_files)} files...")
    
    # Show processing mode
    mode_messages = {
        ProcessingMode.MOCK: "🤖 Running in mock mode (no API calls)",
        ProcessingMode.COPY: "📄 Running in copy mode (raw content only)",
        ProcessingMode.AI_SUMMARIZATION: "🤖 Running AI summarization"
    }
    display_info(mode_messages[config.mode])
    
    # Process files with live table display
    display_info(f"🚀 Updating {len(outdated_files)} files...")
    
    summaries = []
    with create_live_processing_context(outdated_files, discovery.directory) as live_ctx:
        for file_info in outdated_files:
            # Update file status to processing
            live_ctx.update_file_status(file_info, 'processing')
            
            # Process the file
            summary = processor._process_single_file(file_info)
            if summary:
                summaries.append(summary)
                live_ctx.update_file_status(file_info, 'completed')
            else:
                live_ctx.update_file_status(file_info, 'error')
            
            # Advance progress
            live_ctx.advance_progress()
    
    # Write output
    display_info("📝 Writing output...")
    processor.write_output(summaries)
    
    # Show completion stats
    up_to_date_count = len([f for f in discovery.files_to_process if file_status[f.relative_path] == "up-to-date"])
    display_completion_stats(len(summaries), config.output_file, up_to_date_count)


def _run_scan_all_mode(directory: str, config: ProcessingConfig) -> None:
    """Run scan-all mode - process all files"""
    # Check API key requirement for AI mode
    if config.mode == ProcessingMode.AI_SUMMARIZATION and not config.api_key:
        raise ValueError(
            "API key required for AI summarization. "
            "Set CODECTX_API_KEY environment variable or use --api-key argument. "
            "Use --mock-mode for testing without API calls."
        )
    
    display_welcome()
    display_info("🔄 Scan-All Mode: Processing all files")
    display_info("Discovering files...")
    
    # Discover files
    discovery = discover_files(directory)
    if not discovery.files_to_process:
        display_info("❌ No files found to process!")
        return
    
    # Get file status for display
    processor = FileProcessor(config)
    file_status = processor.get_file_status(discovery.files_to_process)
    
    display_file_stats(discovery, file_status)
    
    # Show files to be processed
    if len(discovery.files_to_process) <= 10:
        display_file_table(discovery.files_to_process, file_status, f"📂 All Files ({len(discovery.files_to_process)} files)")
    else:
        display_info(f"📋 Processing {len(discovery.files_to_process)} files...")
    
    # Show processing mode
    mode_messages = {
        ProcessingMode.MOCK: "🤖 Running in mock mode (no API calls)",
        ProcessingMode.COPY: "📄 Running in copy mode (raw content only)",
        ProcessingMode.AI_SUMMARIZATION: "🤖 Running AI summarization"
    }
    display_info(mode_messages[config.mode])
    
    # Process all files with live table display
    display_info(f"🚀 Processing {len(discovery.files_to_process)} files...")
    
    summaries = []
    with create_live_processing_context(discovery.files_to_process, discovery.directory) as live_ctx:
        for file_info in discovery.files_to_process:
            # Update file status to processing
            live_ctx.update_file_status(file_info, 'processing')
            
            # Process the file
            summary = processor._process_single_file(file_info)
            if summary:
                summaries.append(summary)
                live_ctx.update_file_status(file_info, 'completed')
            else:
                live_ctx.update_file_status(file_info, 'error')
            
            # Advance progress
            live_ctx.advance_progress()
    
    # Write output
    display_info("📝 Writing output...")
    processor.write_output(summaries, discovery.files_to_process)
    
    # Show completion stats
    display_completion_stats(len(summaries), config.output_file)


if __name__ == "__main__":
    main()