"""
New modular CLI for codectx with advanced configuration support
"""
import argparse
from typing import Dict, Any
from . import __version__
from .modes import run_direct_mode, run_interactive_mode, run_update_mode
from .utils.configuration import ConfigurationLoader


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
    
    # Configuration arguments
    parser.add_argument(
        '--config', '-c',
        help='Path to configuration file (YAML, JSON, or TOML)'
    )
    parser.add_argument(
        '--api-key',
        help='API key (overrides CODECTX_API_KEY env var)'
    )
    parser.add_argument(
        '--api-url', 
        help='API URL (overrides CODECTX_API_URL env var)'
    )
    parser.add_argument(
        '--retry-attempts',
        type=int,
        help='Number of API retry attempts (default: 3)'
    )
    parser.add_argument(
        '--api-timeout',
        type=float,
        help='API timeout in seconds (default: 30.0)'
    )
    parser.add_argument(
        '--token-threshold',
        type=int,
        help='Token threshold for summarization (default: 200)'
    )
    parser.add_argument(
        '--llm-provider',
        help='LLM provider (default: mistral)'
    )
    parser.add_argument(
        '--llm-model',
        help='LLM model to use (default: codestral-latest)'
    )
    parser.add_argument(
        '--output-file',
        help='Output filename (default: codectx.md)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--concurrent-requests',
        type=int,
        help='Number of concurrent API requests (default: 5)'
    )
    parser.add_argument(
        '--max-file-size',
        type=float,
        help='Maximum file size in MB to process (default: 10.0)'
    )
    parser.add_argument(
        '--generate-config',
        choices=['yaml', 'json', 'toml'],
        help='Generate a sample configuration file and exit'
    )

    args = parser.parse_args()
    
    # Handle --generate-config option
    if args.generate_config:
        try:
            sample_config = ConfigurationLoader.generate_sample_config(args.generate_config)
            filename = f".codectx.{args.generate_config}"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sample_config)
            
            print(f"Generated sample configuration file: {filename}")
            print("Edit this file to customize your codectx settings.")
            return
            
        except Exception as e:
            print(f"Error generating config file: {e}")
            return
    
    # Build CLI overrides dictionary
    cli_overrides = _build_cli_overrides(args)
    
    # Load configuration with CLI overrides
    try:
        config = ConfigurationLoader.load_config(args.config, cli_overrides)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
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
        run_interactive_mode(directory, config)
    elif args.scan_all:
        # Direct mode (scan all files)
        directory = args.directory_path or "."
        run_direct_mode(directory, args.mock_mode, args.copy_mode, config)
    else:
        # Update mode (default - only changed files)
        directory = args.directory_path or "."
        run_update_mode(directory, args.mock_mode, args.copy_mode, config)


def _build_cli_overrides(args) -> Dict[str, Any]:
    """Build configuration overrides from CLI arguments."""
    cli_overrides = {}
    
    if args.api_key:
        cli_overrides['api_key'] = args.api_key
    if args.api_url:
        cli_overrides['api_url'] = args.api_url
    if args.retry_attempts is not None:
        cli_overrides['api_retry_attempts'] = args.retry_attempts
    if args.api_timeout is not None:
        cli_overrides['api_timeout'] = args.api_timeout
    if args.token_threshold is not None:
        cli_overrides['token_threshold'] = args.token_threshold
    if args.llm_provider:
        cli_overrides['llm_provider'] = args.llm_provider
    if args.llm_model:
        cli_overrides['llm_model'] = args.llm_model
    if args.output_file:
        cli_overrides['output_filename'] = args.output_file
    if args.log_level:
        cli_overrides['log_level'] = args.log_level
    if args.concurrent_requests is not None:
        cli_overrides['concurrent_requests'] = args.concurrent_requests
    if args.max_file_size is not None:
        cli_overrides['max_file_size_mb'] = args.max_file_size
    
    return cli_overrides


if __name__ == "__main__":
    main()