"""
Simple global configuration system for codectx.

Configuration priority:
1. CLI arguments (highest priority)
2. Global user config file (~/.config/codectx/config.yml or ~/.codectx.yml)
3. Environment variables (backward compatibility)
4. Default values (fallback)
"""
import os
import yaml
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodectxConfig:
    """
    Comprehensive configuration for codectx with validation and type safety.
    """
    
    # Core API Configuration
    api_key: Optional[str] = None
    api_url: str = ""
    api_retry_attempts: int = 3
    api_timeout: float = 30.0
    
    # LLM Configuration (extensible for future providers)
    llm_provider: str = "mistral"  # future: "claude", "openai", "local", etc.
    llm_model: str = "codestral-latest"
    custom_system_prompt: Optional[str] = None
    
    # File Processing Configuration
    token_threshold: int = 200
    max_file_size_mb: float = 10.0
    file_extensions: List[str] = field(default_factory=lambda: [
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json',
        '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log',
        '.sql', '.sh', '.bat', '.ps1', '.java', '.c', '.cpp', '.h',
        '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt'
    ])
    encoding_priority: List[str] = field(default_factory=lambda: ['utf-8', 'latin1', 'cp1252'])
    
    # Processing Behavior Configuration
    concurrent_requests: int = 5
    default_mode: str = "update"  # "update", "scan-all", "mock", "copy"
    cache_enabled: bool = False
    cache_ttl_hours: int = 24
    
    # Output Configuration
    output_filename: str = "codectx.md"
    output_format: str = "markdown"  # future: "json", "html"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    
    # UI/Display Configuration
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    show_progress: bool = True
    color_output: bool = True
    
    # Advanced Configuration
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '__pycache__/*', '*.pyc', '.git/*', 'node_modules/*',
        '.vscode/*', '.idea/*', 'dist/*', 'build/*'
    ])
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values and raise errors for invalid ones."""
        if self.api_retry_attempts < 1:
            raise ValueError("api_retry_attempts must be at least 1")
        
        if self.api_timeout <= 0:
            raise ValueError("api_timeout must be positive")
            
        if self.token_threshold < 0:
            raise ValueError("token_threshold must be non-negative")
            
        if self.concurrent_requests < 1:
            raise ValueError("concurrent_requests must be at least 1")
        
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
            
        valid_modes = {"update", "scan-all", "mock", "copy", "interactive"}
        if self.default_mode not in valid_modes:
            raise ValueError(f"default_mode must be one of: {valid_modes}")
            
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"log_level must be one of: {valid_log_levels}")
            
        valid_formats = {"markdown", "json", "html"}
        if self.output_format not in valid_formats:
            raise ValueError(f"output_format must be one of: {valid_formats}")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt, using custom if provided, otherwise default."""
        if self.custom_system_prompt:
            return self.custom_system_prompt
        return DEFAULT_SYSTEM_PROMPT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            field.name: getattr(self, field.name) 
            for field in self.__dataclass_fields__.values()
        }


# Default system prompt (moved from old config)
DEFAULT_SYSTEM_PROMPT = """
You are an assistant that analyzes a source code file and produces a structured summary. Your goal is to help a developer understand the purpose of this file without including the raw code.

Follow these rules strictly:
- Summarize the overall purpose of the file in one sentence.
- List all classes with:
    - Their role in the file.
    - Their methods (name, parameters, parameter types) with a short description.
- List global functions similarly.
- Mention important internal dependencies (imports from the same project).
- DO NOT include any raw code or implementation details.
- Keep the summary concise but informative (max 300 tokens).
- Use the following Markdown format:

## File: <relative_path> (SUMMARIZED)
- **Role**: [Short description of what this file does]
- **Classes**:
  - ClassName:
    - Role: [Short description]
    - Methods:
      - method_name(param1[type], param2[type]): [Short description]
- **Global Functions**:
  - function_name(param1, param2): [Short description]
- **Dependencies**: [List of internal imports if any]
"""


class ConfigurationLoader:
    """Simple global configuration loader for codectx."""
    
    @staticmethod
    def get_global_config_path() -> Path:
        """Get the path to the global configuration file."""
        # Try XDG config directory first, fall back to home directory
        if config_home := os.getenv('XDG_CONFIG_HOME'):
            return Path(config_home) / 'codectx' / 'config.yml'
        else:
            # Try ~/.config/codectx/config.yml first
            config_dir = Path.home() / '.config' / 'codectx'
            if config_dir.exists() or not (Path.home() / '.codectx.yml').exists():
                return config_dir / 'config.yml'
            else:
                # Fall back to ~/.codectx.yml if it already exists
                return Path.home() / '.codectx.yml'
    
    @staticmethod
    def load_config(cli_overrides: Optional[Dict[str, Any]] = None) -> CodectxConfig:
        """
        Load configuration from global config and environment with CLI overrides.
        
        Priority: CLI args > global config > env vars > defaults
        """
        # Start with defaults
        config_data = {}
        
        # Load from environment variables
        env_config = ConfigurationLoader._load_from_env()
        config_data.update(env_config)
        
        # Load from global configuration file
        file_config = ConfigurationLoader._load_global_config()
        if file_config:
            config_data.update(file_config)
        
        # Apply CLI overrides
        if cli_overrides:
            config_data.update(cli_overrides)
        
        # Create and return configuration object
        return CodectxConfig(**config_data)
    
    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables (backward compatibility)."""
        env_config = {}
        
        # Core API configuration
        if api_key := os.getenv('CODECTX_API_KEY'):
            env_config['api_key'] = api_key
        if api_url := os.getenv('CODECTX_API_URL'):
            env_config['api_url'] = api_url
        
        # New environment variables
        if retry_attempts := os.getenv('CODECTX_API_RETRY_ATTEMPTS'):
            try:
                env_config['api_retry_attempts'] = int(retry_attempts)
            except ValueError:
                pass
        
        if timeout := os.getenv('CODECTX_API_TIMEOUT'):
            try:
                env_config['api_timeout'] = float(timeout)
            except ValueError:
                pass
        
        if token_threshold := os.getenv('CODECTX_TOKEN_THRESHOLD'):
            try:
                env_config['token_threshold'] = int(token_threshold)
            except ValueError:
                pass
        
        if llm_provider := os.getenv('CODECTX_LLM_PROVIDER'):
            env_config['llm_provider'] = llm_provider
        
        if llm_model := os.getenv('CODECTX_LLM_MODEL'):
            env_config['llm_model'] = llm_model
        
        if custom_prompt := os.getenv('CODECTX_CUSTOM_PROMPT'):
            env_config['custom_system_prompt'] = custom_prompt
        
        if output_file := os.getenv('CODECTX_OUTPUT_FILENAME'):
            env_config['output_filename'] = output_file
        
        if log_level := os.getenv('CODECTX_LOG_LEVEL'):
            env_config['log_level'] = log_level.upper()
        
        if concurrent := os.getenv('CODECTX_CONCURRENT_REQUESTS'):
            try:
                env_config['concurrent_requests'] = int(concurrent)
            except ValueError:
                pass
                
        return env_config
    
    @staticmethod
    def _load_global_config() -> Optional[Dict[str, Any]]:
        """Load configuration from global config file, creating it if it doesn't exist."""
        config_path = ConfigurationLoader.get_global_config_path()
        
        # Create config file with defaults if it doesn't exist
        if not config_path.exists():
            ConfigurationLoader._create_default_config(config_path)
            return {}  # Return empty dict as defaults will be used
        
        try:
            content = config_path.read_text(encoding='utf-8')
            return yaml.safe_load(content) or {}
        except Exception as e:
            print(f"Warning: Error loading config file {config_path}: {e}")
            print("Using default configuration.")
            return None
    
    @staticmethod
    def _create_default_config(config_path: Path) -> None:
        """Create default configuration file at the specified path."""
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate default YAML config
        default_content = ConfigurationLoader._generate_default_yaml_config()
        
        # Write to file
        config_path.write_text(default_content, encoding='utf-8')
        print(f"Created default configuration file: {config_path}")
        print("Edit this file to customize your codectx settings.")
    
    @staticmethod
    def get_config_path_for_display() -> str:
        """Get config path as string for display purposes."""
        return str(ConfigurationLoader.get_global_config_path())
    
    @staticmethod  
    def edit_config() -> None:
        """Open the global configuration file in the default editor."""
        config_path = ConfigurationLoader.get_global_config_path()
        
        # Create config if it doesn't exist
        if not config_path.exists():
            ConfigurationLoader._create_default_config(config_path)
        
        # Try to open with default editor
        import subprocess
        import sys
        
        editor = os.getenv('EDITOR', 'nano' if sys.platform != 'win32' else 'notepad')
        try:
            subprocess.run([editor, str(config_path)], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Could not open editor. Please edit the config file manually: {config_path}")
    
    @staticmethod
    def generate_sample_config() -> str:
        """Generate sample YAML configuration content."""
        return ConfigurationLoader._generate_default_yaml_config()
    
    @staticmethod
    def _generate_default_yaml_config() -> str:
        """Generate default YAML configuration with comments."""
        return """# codectx - Global Configuration File
# This file stores your personal preferences for codectx
# Location: This file is stored in your user directory and applies to all projects

# API Configuration (most important settings)
api_key: ""  # Your AI API key - REQUIRED for summarization
api_url: "https://codestral.mistral.ai/v1/chat/completions"  # Default Mistral API endpoint
api_retry_attempts: 3  # Number of retry attempts for failed API calls
api_timeout: 30.0  # Timeout in seconds for each API request

# LLM Configuration
llm_provider: "mistral"  # Current: mistral (future: claude, openai, local)
llm_model: "codestral-latest"  # Model name to use

# Processing Preferences
token_threshold: 200  # Files above this estimated token count get AI summarized
max_file_size_mb: 10.0  # Skip files larger than this (prevents accidents)
concurrent_requests: 5  # Number of parallel API requests (higher = faster but more load)

# Output Preferences  
output_filename: "codectx.md"  # Default output filename
log_level: "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR
show_progress: true  # Show progress bars and status updates
color_output: true  # Use colored console output

# Advanced Settings (usually don't need to change these)
default_mode: "update"  # Default processing mode
timestamp_format: "%Y-%m-%d %H:%M:%S"  # Timestamp format in output

# Global ignore patterns (in addition to project .codectxignore files)
ignore_patterns:
  - "__pycache__/*"
  - "*.pyc"
  - ".git/*"
  - "node_modules/*"
  - ".vscode/*"
  - ".idea/*"
  - "dist/*"
  - "build/*"

# Uncomment and customize if you want a custom AI prompt:
# custom_system_prompt: |
#   You are a helpful assistant that creates concise code summaries.
#   Focus on the main purpose and key functions of each file.
""".strip()
    
# Convenience functions for backward compatibility
def get_config(cli_overrides: Optional[Dict[str, Any]] = None) -> CodectxConfig:
    """Main function to get configuration."""
    return ConfigurationLoader.load_config(cli_overrides)


def get_api_key() -> Optional[str]:
    """Backward compatibility function."""
    config = get_config()
    return config.api_key


def get_api_url() -> str:
    """Backward compatibility function."""
    config = get_config()
    return config.api_url