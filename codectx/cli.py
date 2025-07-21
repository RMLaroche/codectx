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
  codectx                    # Enter interactive mode (auto-creates config on first run)
  codectx /path/to/project   # Update changed files only (default)
  codectx --edit-config      # Open global configuration in editor
  codectx --show-config      # Display current configuration
  codectx --scan-all .       # Process all files (override update mode)
  codectx --mock-mode .      # Test without API calls
  codectx --token-threshold 50 .  # Override token threshold for this run
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
        '--edit-config',
        action='store_true',
        help='Open global configuration file in default editor'
    )
    parser.add_argument(
        '--show-config',
        action='store_true', 
        help='Show current configuration and exit'
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
        '--init-config',
        action='store_true',
        help='Initialize global configuration file with defaults (if not exists)'
    )

    args = parser.parse_args()
    
    # Handle configuration management options
    if args.edit_config:
        try:
            ConfigurationLoader.edit_config()
            return
        except Exception as e:
            print(f"Error opening configuration file: {e}")
            return
    
    if args.show_config:
        try:
            config = ConfigurationLoader.load_config()
            config_path = ConfigurationLoader.get_config_path_for_display()
            print(f"Configuration loaded from: {config_path}")
            print("\nCurrent configuration:")
            print(f"  API Key: {'***set***' if config.api_key else 'not set'}")
            print(f"  API URL: {config.api_url}")
            print(f"  Retry attempts: {config.api_retry_attempts}")
            print(f"  Token threshold: {config.token_threshold}")
            print(f"  LLM provider: {config.llm_provider}")
            print(f"  LLM model: {config.llm_model}")
            print(f"  Output filename: {config.output_filename}")
            print(f"  Log level: {config.log_level}")
            return
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return
    
    if args.init_config:
        try:
            config_path = ConfigurationLoader.get_global_config_path()
            if config_path.exists():
                print(f"Configuration file already exists: {config_path}")
                print("Use --edit-config to modify it.")
            else:
                ConfigurationLoader._create_default_config(config_path)
            return
        except Exception as e:
            print(f"Error creating configuration file: {e}")
            return
    
    # Build CLI overrides dictionary
    cli_overrides = _build_cli_overrides(args)
    
    # Load configuration with CLI overrides
    try:
        config = ConfigurationLoader.load_config(cli_overrides)
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