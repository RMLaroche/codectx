"""
New modular CLI for codectx
"""
import argparse
from . import __version__
from .modes import run_direct_mode, run_interactive_mode, run_update_mode


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="codectx - AI-powered code context and file summarization tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codectx                    # Enter interactive mode
  codectx /path/to/project   # Update changed files only (default)
  codectx --interactive      # Force interactive mode with menu
  codectx --scan-all .       # Process all files (override update mode)
  codectx --mock-mode .      # Test without API calls
  codectx --copy-mode .      # Copy files without summarization
        """
    )
    
    parser.add_argument(
        'directory_path', 
        nargs='?', 
        default=None, 
        help='The directory to process (default: interactive mode if no path specified)'
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
    parser.add_argument(
        '--interactive', '-i',
        action='store_true', 
        help='Force interactive mode even when directory is specified'
    )
    parser.add_argument(
        '--scan-all',
        action='store_true',
        help='Process all files instead of just changed files'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'codectx {__version__}'
    )

    args = parser.parse_args()
    
    # Determine which mode to use
    use_interactive = args.interactive or (
        args.directory_path is None and 
        not args.mock_mode and 
        not args.copy_mode and
        not args.scan_all
    )
    
    if use_interactive:
        # Interactive mode
        directory = args.directory_path or "."
        run_interactive_mode(directory)
    elif args.scan_all:
        # Direct mode (scan all files)
        directory = args.directory_path or "."
        run_direct_mode(directory, args.mock_mode, args.copy_mode)
    else:
        # Update mode (default - only changed files)
        directory = args.directory_path or "."
        run_update_mode(directory, args.mock_mode, args.copy_mode)


if __name__ == "__main__":
    main()